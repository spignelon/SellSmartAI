import os
from dotenv import load_dotenv
import time
import google.generativeai as genai
from PIL import Image

load_dotenv()

class GeminiAnalyzer:
    def __init__(self):
        """
        Initialize the GeminiAnalyzer class and configure the API.
        """
        # Load the API key from environment variables
        self.api_key = os.getenv("GOOGLE_API_KEY")
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

# Main execution
if __name__ == "__main__":
    # Example input: List of file paths (images or a single video)
    input_files = input("Enter paths to files (comma-separated): ").strip().split(",")

    # Strip whitespace and clean file paths
    input_files = [file_path.strip() for file_path in input_files]

    # Initialize the analyzer
    analyzer = GeminiAnalyzer()

    try:
        # Analyze the input files
        result = analyzer.analyze(input_files)
        print("Analysis Result:")
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")
