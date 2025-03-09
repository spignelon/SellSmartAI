import cv2
import os

class ImageQualityChecker:
    def __init__(self, images_list, threshold=100.0):
        self.images_list = images_list
        self.threshold = threshold
        self.quality_scores = []

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

    def process_images(self):
        """
        Processes all images in the directory, calculates their quality scores,
        and filters out blurry images based on the threshold.
        """
        for filename in self.images_list:
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                image = cv2.imread(filename)
                if image is None:
                    print(f"Could not read file: {filename}")
                    continue
                
                laplacian_var = self.calculate_laplacian_variance(image)
                if laplacian_var > self.threshold:
                    self.quality_scores.append((filename, laplacian_var))

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
        self.process_images()
        self.sort_images_by_quality()
        top_3_images = self.get_sorted_images()[:3]
        return [image[0] for image in top_3_images]

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