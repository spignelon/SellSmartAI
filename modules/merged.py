import os
import glob
from instaloader import Instaloader, Post
from PIL import Image
import pytesseract
import google.generativeai as genai
import json
import time

class GeminiAnalyzer:
    def __init__(self, GOOGLE_API_KEY):
        """
        Initialize the GeminiAnalyzer class and configure the API.
        """
        # Load the API key from environment variables
        self.api_key = GOOGLE_API_KEY
        genai.configure(api_key=self.api_key)

    def upload_file(self, file_path):
        """
        Upload a file (image or video) to Gemini.
        :param file_path: Path to the file to upload.
        :return: Uploaded file object.
        """
        print(f"Uploading file: {file_path}")
        uploaded_file = genai.upload_file(path=file_path)
        print(f"Completed upload: {uploaded_file.uri}")
        return uploaded_file

    def process_images(self, image_paths):
        """
        Process one or more image files, upload them to Gemini, and ask "What's in this image?".
        :param image_paths: List of paths to image files.
        :return: Generated content describing the images.
        """
        # Open and validate all image files
        image_files = [Image.open(image_path) for image_path in image_paths]
        
        # Initialize the Gemini model for images
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        
        # Prompt for the image analysis
        prompt = "What's in this image?"
        
        # Generate content for all uploaded images
        response = model.generate_content([prompt, *image_files])
        return response.text

    def process_video(self, video_path):
        """
        Process a video file, upload it to Gemini, and ask "What's in this video?".
        :param video_path: Path to the video file.
        :return: Generated content describing the video.
        """
        # Upload the video
        video_file = self.upload_file(video_path)
        
        # Wait for the video file to be ready
        print("Processing video...")
        while video_file.state.name == "PROCESSING":
            print('.', end='', flush=True)
            time.sleep(10)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise ValueError("Video processing failed.")

        # Initialize the Gemini model for video
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        
        # Prompt for the video analysis
        prompt = "What's in this video?"
        
        # Generate content for the uploaded video
        response = model.generate_content([video_file, prompt], request_options={"timeout": 600})
        return response.text

    def analyze(self, file_paths):
        """
        Analyze the input files (images or video).
        :param file_paths: List of file paths. Can include one or more images or a single video.
        :return: Analysis results as text.
        """
        # Check the file types
        if len(file_paths) == 1 and file_paths[0].lower().endswith(('.mp4', '.mov', '.avi')):
            # Single video file
            return self.process_video(file_paths[0])
        else:
            # One or more image files
            return self.process_images(file_paths)

class InstagramProcessor:
    def __init__(self, base_folder="insta", GOOGLE_API_KEY=""):
        """
        Initializes the InstagramProcessor class.

        :param base_folder: The base folder where all data will be saved.
        """
        self.base_folder = base_folder
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)
        self.gemini_analyzer = GeminiAnalyzer(GOOGLE_API_KEY)  # Initialize GeminiAnalyzer
        genai.configure(api_key=GOOGLE_API_KEY)

    def download_post(self, url):
        """
        Downloads Instagram post media and description using Instaloader.

        :param url: The URL of the Instagram post.
        :return: A tuple of post description and downloaded file paths.
        """
        loader = Instaloader(download_videos=True, save_metadata=False)
        post_description = None
        downloaded_files = []

        try:
            # Extract shortcode and download the post
            shortcode = url.split("/p/")[1].split("/")[0]
            post = Post.from_shortcode(loader.context, shortcode)
            loader.download_post(post, target=self.base_folder)

            # Collect all downloaded files
            for file in os.listdir(self.base_folder):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.mp4', '.mov', '.avi', '.txt')):
                    downloaded_files.append(os.path.join(self.base_folder, file))

            # Find and read the post description file
            for file_path in downloaded_files:
                if file_path.endswith(".txt"):
                    with open(file_path, "r", encoding="utf-8") as desc_file:
                        post_description = desc_file.read().strip()
                    downloaded_files.remove(file_path)  # Remove description from media files
                    break

            print(f"Post downloaded successfully to {self.base_folder}.")
        except Exception as e:
            print(f"Error downloading the post: {e}")

        return post_description, downloaded_files

    def perform_ocr(self):
        """
        Performs OCR on all images in the base folder.

        :return: The concatenated OCR text.
        """
        ocr_output_file = os.path.join(self.base_folder, "ocr.txt")
        ocr_text = []

        # Initialize the output file
        with open(ocr_output_file, "w", encoding="utf-8") as ocr_file:
            ocr_file.write("OCR Results:\n\n")

        # Process images for OCR
        for file_name in sorted(os.listdir(self.base_folder)):
            file_path = os.path.join(self.base_folder, file_name)
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                try:
                    text = pytesseract.image_to_string(Image.open(file_path))
                    ocr_text.append(f"--- {file_name} ---\n{text.strip()}\n")
                    with open(ocr_output_file, "a", encoding="utf-8") as ocr_file:
                        ocr_file.write(f"--- {file_name} ---\n{text.strip()}\n\n")
                except Exception as e:
                    print(f"Error performing OCR on {file_name}: {e}")

        return "\n".join(ocr_text)

    def analyze_with_gemini(self, media_files):
        """
        Analyze images and videos using Gemini.

        :param media_files: List of media file paths.
        :return: Generated content describing the media files.
        """
        # Separate images and videos
        image_files = [file for file in media_files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
        video_files = [file for file in media_files if file.lower().endswith(('.mp4', '.mov', '.avi'))]

        results = {}

        # Analyze images with Gemini
        if image_files:
            try:
                print("Analyzing images with Gemini...")
                image_results = self.gemini_analyzer.process_images(image_files)
                results["images"] = image_results
            except Exception as e:
                print(f"Error during image analysis: {e}")

        # Analyze videos with Gemini
        if video_files:
            try:
                print("Analyzing videos with Gemini...")
                video_results = []
                for video_file in video_files:
                    result = self.gemini_analyzer.process_video(video_file)
                    video_results.append({video_file: result})
                results["videos"] = video_results
            except Exception as e:
                print(f"Error during video analysis: {e}")

        return results
    
    def sanitize_to_json(self, response_text):
        """
        Sanitize the response text by removing triple backticks and converting it into a JSON object.

        :param response_text: The raw text response from Gemini.
        :return: A JSON object parsed from the text.
        """
        try:
            # Remove triple backticks if present
            sanitized_text = response_text.strip().strip("```json").strip("```").strip()
            
            # Parse the sanitized text into JSON
            json_data = json.loads(sanitized_text)
            return json_data
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return None

    def process_gemini_text(self, post_description, ocr_text, gemini_results, media_files):
        """
        Sends all extracted data to Gemini text model for summarization and extraction in JSON format.

        :param post_description: Description of the Instagram post.
        :param ocr_text: Text extracted from images using OCR.
        :param gemini_results: Results from Gemini image and video analysis.
        :param media_files: List of downloaded media files.
        :return: A JSON containing structured product data.
        """
        # Combine all text inputs for the prompt
        prompt = f"""
You are a helpful assistant extracting structured product information. Given the following data:

1. **Post Description**:
{post_description}

2. **OCR Text**:
{ocr_text}

3. **Gemini Results**:
{gemini_results}

Please return a JSON strictly in this format:
{{
   "images_list": {media_files},
   "product_title": "",
   "price": "",
   "product_details": {{
       "Key1": "Value1",
       "Key2": "Value2"
   }},
   "about this item": "",
   "Product description": ""
}}
The "product_details" field is dynamic, and its keys will vary depending on the product type. Fill in as much detail as possible based on the input. Also the product description should be long and very detailed paragraph about the product. If there is no prize in in the information above then assume a prize of the product yourself.
"""
        print("Sending data to Gemini text model...")
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return self.sanitize_to_json(response.text)


    def process_post(self, url):
        """
        Main function to process an Instagram post: download, OCR, and Gemini analysis.

        :param url: The URL of the Instagram post.
        :return: A JSON with product details and other extracted information.
        """
        # Step 1: Download Instagram post
        print("Downloading Instagram post...")
        post_description, media_files = self.download_post(url)

        # Step 2: Perform OCR
        print("Performing OCR on images...")
        ocr_text = self.perform_ocr()

        # Step 3: Analyze media with Gemini
        print("Analyzing media with Gemini...")
        gemini_results = self.analyze_with_gemini(media_files)

        # Step 4: Process Gemini text-only input
        print("Processing data with Gemini text model...")
        final_results = self.process_gemini_text(post_description, ocr_text, gemini_results, media_files)

        return final_results


# Example usage
if __name__ == "__main__":
    url = input("Enter the Instagram post URL: ")
    import shutil
    shutil.rmtree('insta', ignore_errors=True)
    processor = InstagramProcessor(GOOGLE_API_KEY="AIzaSyD9yTXXXXXXXd0yNSF65Afb4JA")
    results = processor.process_post(url)
    print("\nProcessing complete. Results:")
    print(results)
