import cv2
import os
import requests
import tempfile
import urllib.parse
from urllib.parse import urlparse

class ImageQualityChecker:
    def __init__(self, images_list, threshold=100.0):
        self.images_list = images_list
        self.threshold = threshold
        self.quality_scores = []
        self.temp_files = []  # Track temp files to clean up later

    def calculate_laplacian_variance(self, image):
        """
        Calculate the variance of the Laplacian of an image.
        A lower variance indicates the image is blurry.

        Parameters:
        - image: The input image in BGR format.

        Returns:
        - laplacian_var: The variance of the Laplacian.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        return laplacian_var

    def download_image(self, image_url):
        """Download an image from URL to a temporary file and return the file path"""
        try:
            # Parse the URL to handle both absolute and relative URLs
            parsed_url = urlparse(image_url)
            
            # If it's a local file (starts with /static/ or similar)
            if not parsed_url.scheme and not parsed_url.netloc:
                if image_url.startswith('/'):
                    # Remove leading slash if present
                    local_path = image_url[1:]
                else:
                    local_path = image_url
                
                # Handle static files correctly
                if os.path.exists(local_path):
                    return local_path
                    
                # Try full path from project root
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                full_path = os.path.join(base_dir, local_path)
                if os.path.exists(full_path):
                    return full_path
            
            # For HTTP URLs, download the image
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            # Create a temporary file
            fd, temp_path = tempfile.mkstemp(suffix=".jpg")
            self.temp_files.append(temp_path)  # Track for cleanup
            
            # Write the image data to the temp file
            with os.fdopen(fd, 'wb') as temp_file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        temp_file.write(chunk)
                        
            return temp_path
            
        except Exception as e:
            print(f"Error downloading image from {image_url}: {str(e)}")
            return None

    def process_images(self):
        """
        Processes all images in the list, calculates their quality scores,
        and filters out blurry images based on the threshold.
        """
        for image_url in self.images_list:
            try:
                # Download image if it's a URL
                local_image_path = self.download_image(image_url)
                
                if not local_image_path:
                    print(f"Failed to download or locate image: {image_url}")
                    continue
                
                # Read the local image file
                image = cv2.imread(local_image_path)
                if image is None:
                    print(f"Could not read file: {local_image_path}")
                    continue
                
                laplacian_var = self.calculate_laplacian_variance(image)
                if laplacian_var > self.threshold:
                    # Store original URL, not the temporary file path
                    self.quality_scores.append((image_url, laplacian_var))
                    print(f"Image quality score for {image_url}: {laplacian_var}")
                
            except Exception as e:
                print(f"Error processing image {image_url}: {str(e)}")

    def sort_images_by_quality(self):
        """
        Sorts the processed images by quality score in descending order.
        """
        self.quality_scores.sort(key=lambda x: x[1], reverse=True)

    def get_sorted_images(self):
        """
        Returns the sorted list of good quality images and their scores.

        Returns:
        - List of tuples containing (filename, quality_score).
        """
        return self.quality_scores

    def start(self):
        """
        Starts the image quality checking process.
        """
        print(f"Starting quality check for {len(self.images_list)} images")
        self.process_images()
        self.sort_images_by_quality()
        
        # Clean up any temporary files
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except:
                pass
        
        # Return top 3 images or all if less than 3
        top_images = self.get_sorted_images()[:3]
        result = [image[0] for image in top_images]
        print(f"Top quality images: {result}")
        return result

# Example usage
if __name__ == "__main__":
    input_directory = "static"  # Change to your directory
    sharpness_threshold = 100.0  # Adjust based on your quality needs
    
    # Initialize the ImageQualityChecker class
    checker = ImageQualityChecker(input_directory, sharpness_threshold)
    
    # Process images and sort by quality
    checker.process_images()
    checker.sort_images_by_quality()
    
    # Retrieve and print the sorted images with their scores
    sorted_quality_images = checker.get_sorted_images()
    
    print("Sorted good quality images and their scores:")
    for filename, score in sorted_quality_images:
        print(f"{filename}: {score}")