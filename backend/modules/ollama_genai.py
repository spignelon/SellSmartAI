import ollama
import base64
import os
import logging
from PIL import Image
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaClientError(Exception):
    """Custom exception for Ollama client errors."""
    pass

class ImageHelper:
    """Helper class for image-related operations."""

    @staticmethod
    def encode_image_to_base64(image_path: str) -> str:
        """
        Encodes an image file to a base64 string.

        Args:
            image_path (str): The path to the image file.

        Returns:
            str: The base64 encoded string of the image.
        
        Raises:
            FileNotFoundError: If the image_path does not exist.
            IOError: If there's an error opening or reading the image.
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found at path: {image_path}")
        try:
            with Image.open(image_path) as img:
                # Ensure image is in a common format like RGB before saving to buffer
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                buffered = BytesIO()
                img.save(buffered, format="JPEG") # Or PNG
                img_byte = buffered.getvalue()
                return base64.b64encode(img_byte).decode('utf-8')
        except IOError as e:
            raise IOError(f"Error processing image file {image_path}: {e}")

class OllamaImageDescriber:
    """
    Uses a multimodal model via Ollama to describe images or identify objects.
    """
    def __init__(self, model_name: str = "llava:latest", ollama_host: Optional[str] = None):
        """
        Initializes the OllamaImageDescriber.

        Args:
            model_name (str): The name of the multimodal model in Ollama (e.g., "llava:latest", "llava:7b").
            ollama_host (Optional[str]): The host URL for Ollama if not default (e.g., "http://localhost:11434").
        """
        self.model_name = model_name
        self.client_args = {}
        if ollama_host:
            self.client_args['host'] = ollama_host
        
        try:
            # Check if model exists
            ollama.list(**self.client_args) # Basic check to see if client can connect
            logger.info(f"OllamaImageDescriber initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client or list models: {e}")
            raise OllamaClientError(f"Ollama connection failed: {e}")

    def describe_image(self, image_path: str, prompt: str = "Describe this image in detail, including all visible objects.") -> str:
        """
        Generates a textual description of an image using the multimodal model.

        Args:
            image_path (str): The path to the image file.
            prompt (str): The prompt to guide the model's description.

        Returns:
            str: The textual description of the image.
                 Returns an error message if description fails.
        """
        logger.info(f"Attempting to describe image: {image_path} using model {self.model_name}")
        try:
            base64_image = ImageHelper.encode_image_to_base64(image_path)
        except (FileNotFoundError, IOError) as e:
            logger.error(str(e))
            return f"Error: {str(e)}"

        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                images=[base64_image],
                stream=False,
                **self.client_args
            )
            description = response.get('response', '').strip()
            logger.info(f"Image description generated successfully for {image_path}.")
            return description
        except Exception as e:
            logger.error(f"Error during Ollama image description for {image_path}: {e}")
            return f"Error generating image description: {e}"

class OllamaTextGenerator:
    """
    Uses a text generation model (like Gemma) via Ollama.
    """
    def __init__(self, model_name: str = "gemma:2b", ollama_host: Optional[str] = None):
        """
        Initializes the OllamaTextGenerator.

        Args:
            model_name (str): The name of the text generation model in Ollama (e.g., "gemma:2b", "gemma:7b").
            ollama_host (Optional[str]): The host URL for Ollama if not default.
        """
        self.model_name = model_name
        self.client_args = {}
        if ollama_host:
            self.client_args['host'] = ollama_host
        
        try:
            ollama.list(**self.client_args) # Basic connection check
            logger.info(f"OllamaTextGenerator initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client or list models: {e}")
            raise OllamaClientError(f"Ollama connection failed: {e}")

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """
        Generates text based on a given prompt.

        Args:
            prompt (str): The main prompt for text generation.
            system_prompt (Optional[str]): An optional system message to guide the model's behavior.
            temperature (float): Controls randomness. Lower is more deterministic.
            max_tokens (Optional[int]): Maximum number of tokens to generate.

        Returns:
            str: The generated text.
                 Returns an error message if generation fails.
        """
        logger.info(f"Generating text with model {self.model_name} for prompt: '{prompt[:100]}...'")
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        options = {'temperature': temperature}
        if max_tokens:
            options['num_predict'] = max_tokens # Ollama uses num_predict for max tokens

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                stream=False,
                options=options,
                **self.client_args
            )
            generated_text = response['message']['content'].strip()
            logger.info("Text generation successful.")
            return generated_text
        except Exception as e:
            logger.error(f"Error during Ollama text generation: {e}")
            return f"Error generating text: {e}"

class GenerativeAIHandler:
    """
    Combines image description and text generation functionalities.
    """
    def __init__(self, 
                 image_model: str = "llava:latest", 
                 text_model: str = "gemma:2b", 
                 ollama_host: Optional[str] = None):
        """
        Initializes the GenerativeAIHandler.

        Args:
            image_model (str): Name of the multimodal model for image description.
            text_model (str): Name of the text generation model.
            ollama_host (Optional[str]): Ollama host URL.
        """
        try:
            self.image_describer = OllamaImageDescriber(model_name=image_model, ollama_host=ollama_host)
            self.text_generator = OllamaTextGenerator(model_name=text_model, ollama_host=ollama_host)
            logger.info("GenerativeAIHandler initialized successfully.")
        except OllamaClientError as e:
            logger.error(f"Failed to initialize GenerativeAIHandler: {e}")
            # Propagate the error or handle it as needed
            raise

    def generate_text_about_image(self, 
                                  image_path: str, 
                                  image_desc_prompt: str = "Briefly list the main objects in this image.",
                                  text_gen_prompt_template: str = "Write a short creative story about the following: {image_description}",
                                  text_gen_system_prompt: Optional[str] = "You are a creative storyteller.",
                                  temperature: float = 0.8,
                                  max_tokens: Optional[int] = 150
                                 ) -> Tuple[Optional[str], Optional[str]]:
        """
        Describes an image and then generates further text based on that description.

        Args:
            image_path (str): Path to the image.
            image_desc_prompt (str): Prompt for the image description model.
            text_gen_prompt_template (str): A template for the text generation prompt. 
                                           Must include '{image_description}'.
            text_gen_system_prompt (Optional[str]): System prompt for the text generator.
            temperature (float): Temperature for text generation.
            max_tokens (Optional[int]): Max tokens for text generation.

        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing (image_description, generated_text).
                                                 Returns (None, None) or error messages on failure.
        """
        logger.info(f"Processing image {image_path} for text generation.")
        
        image_description = self.image_describer.describe_image(image_path, prompt=image_desc_prompt)
        
        if image_description is None or "Error:" in image_description:
            logger.error(f"Failed to get image description for {image_path}. Aborting text generation.")
            return image_description, None # Return the error message from description

        # Prepare the prompt for the text generator using the description
        final_text_gen_prompt = text_gen_prompt_template.format(image_description=image_description)
        
        generated_text = self.text_generator.generate_text(
            prompt=final_text_gen_prompt,
            system_prompt=text_gen_system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return image_description, generated_text

# --- Example Usage ---
if __name__ == "__main__":
    # IMPORTANT: 
    # 1. Make sure Ollama is running.
    # 2. Make sure you have pulled the necessary models:
    #    ollama pull llava:latest  (or another llava variant)
    #    ollama pull gemma:2b     (or another gemma variant)
    # 3. Create a dummy image file named "sample_image.jpg" in the same directory
    #    as this script, or provide a valid path to an image.

    # Create a dummy image for testing if it doesn't exist
    sample_image_path = "sample_image.jpg"
    if not os.path.exists(sample_image_path):
        try:
            img = Image.new('RGB', (100, 100), color = 'red')
            img.save(sample_image_path)
            logger.info(f"Created dummy image: {sample_image_path}")
        except Exception as e:
            logger.error(f"Could not create dummy image: {e}")
            # Exit if dummy image cannot be created and path is not valid
            # This is to prevent the script from failing if no image is available
            # In a real application, you'd handle this more gracefully
            exit()

    try:
        # --- Test OllamaImageDescriber ---
        print("\n--- Testing Image Describer ---")
        describer = OllamaImageDescriber(model_name="llava:latest") # or "llava:7b" etc.
        description = describer.describe_image(sample_image_path, prompt="What objects are in this image?")
        print(f"Image Description for '{sample_image_path}':\n{description}\n")

        # --- Test OllamaTextGenerator ---
        print("\n--- Testing Text Generator ---")
        gemma_generator = OllamaTextGenerator(model_name="gemma:2b") # or "gemma:7b" etc.
        story_prompt = "Write a short poem about a robot dreaming of stars."
        generated_story = gemma_generator.generate_text(story_prompt, temperature=0.7, max_tokens=100)
        print(f"Generated Poem:\n{generated_story}\n")

        # --- Test GenerativeAIHandler (Combined) ---
        print("\n--- Testing Combined Generative AI Handler ---")
        ai_handler = GenerativeAIHandler(image_model="llava:latest", text_model="gemma:2b")
        
        img_desc, creative_text = ai_handler.generate_text_about_image(
            image_path=sample_image_path,
            image_desc_prompt="Describe the main subject of this image in one sentence.",
            text_gen_prompt_template="Based on the description: '{image_description}', write a very short story (2-3 sentences).",
            text_gen_system_prompt="You are a concise and imaginative storyteller.",
            temperature=0.7,
            max_tokens=80
        )
        print(f"Image Description used by Handler:\n{img_desc}\n")
        print(f"Generated Creative Text based on Image Description:\n{creative_text}\n")

    except OllamaClientError as e:
        logger.error(f"Ollama client error during example usage: {e}")
        print(f"Ollama client error: {e}. Please ensure Ollama is running and models are pulled.")
    except FileNotFoundError as e:
        logger.error(f"File not found during example usage: {e}")
        print(f"Error: {e}. Please ensure the image path is correct.")
    except Exception as e:
        logger.error(f"An unexpected error occurred during example usage: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")

