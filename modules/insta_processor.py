import os
import glob
from instaloader import Instaloader, Post
from PIL import Image
import pytesseract
from ultralytics import YOLO


class InstagramProcessor:
    def __init__(self, base_folder="insta"):
        """
        Initializes the InstagramProcessor class.

        :param base_folder: The base folder where all data will be saved.
        """
        self.base_folder = base_folder
        if not os.path.exists(self.base_folder):
            os.makedirs(self.base_folder)

    def download_post(self, url):
        """
        Downloads Instagram post media and description using Instaloader.

        :param url: The URL of the Instagram post.
        :return: The post description if available.
        """
        loader = Instaloader(download_videos=True, save_metadata=False)
        post_description = None

        try:
            # Extract shortcode and download the post
            shortcode = url.split("/p/")[1].split("/")[0]
            post = Post.from_shortcode(loader.context, shortcode)
            loader.download_post(post, target=self.base_folder)

            # Find and read the post description file
            for file in os.listdir(self.base_folder):
                if file.endswith(".txt"):
                    description_path = os.path.join(self.base_folder, file)
                    with open(description_path, "r", encoding="utf-8") as desc_file:
                        post_description = desc_file.read().strip()
                    break

            print(f"Post downloaded successfully to {self.base_folder}.")
        except Exception as e:
            print(f"Error downloading the post: {e}")

        return post_description

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

    def detect_objects(self):
        """
        Detects objects in images using YOLO.

        :return: A dictionary mapping image paths to detected objects.
        """
        model = YOLO("yolov8s.pt")  # Load YOLO model
        detection_results = {}

        # Process images for object detection
        for file_name in sorted(os.listdir(self.base_folder)):
            file_path = os.path.join(self.base_folder, file_name)
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                try:
                    results = model(file_path)
                    detected_objects = []
                    for result in results:
                        for box in result.boxes:
                            class_id = int(box.cls)  # Class index
                            class_name = model.names[class_id]  # Get class name
                            detected_objects.append(class_name)
                    detection_results[file_path] = detected_objects
                except Exception as e:
                    print(f"Error detecting objects in {file_name}: {e}")

        return detection_results

    def process_post(self, url):
        """
        Main function to process an Instagram post: download, OCR, and object detection.

        :param url: The URL of the Instagram post.
        :return: A dictionary with images, post description, OCR text, and detection results.
        """
        # Step 1: Download Instagram post
        print("Downloading Instagram post...")
        post_description = self.download_post(url)

        # Step 2: Perform OCR
        print("Performing OCR on images...")
        ocr_text = self.perform_ocr()

        # Step 3: Detect objects in images
        print("Performing object detection...")
        detection_results = self.detect_objects()
        
        image_files = glob.glob(self.base_folder + '/*.{png,jpg,jpeg,gif,bmp,tiff}', recursive=True)

        # Compile results
        results = {
            "images_folder": image_files,
            "post_description": post_description,
            "ocr_text": ocr_text,
            "detection_results": detection_results,
        }

        return results


# Example usage
if __name__ == "__main__":
    url = input("Enter the Instagram post URL: ")
    import shutil
    shutil.rmtree('insta', ignore_errors=True)
    processor = InstagramProcessor()
    results = processor.process_post(url)
    print("\nProcessing complete. Results:")
    print(results)
