import requests
from pprint import pprint
import random
import string
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

class VideoFrameExtractor:
    def __init__(self, video_path, output_folder="static"):
        """
        Initializes the VideoFrameExtractor.

        :param video_path: Path to the video file.
        :param output_folder: Directory where extracted frames will be saved.
        """
        self.video_path = video_path
        self.output_folder = output_folder
        self._validate_video_path()
        self._create_output_folder()

    def _validate_video_path(self):
        """Validates the existence of the video file."""
        if not os.path.isfile(self.video_path):
            raise FileNotFoundError(f"The video file '{self.video_path}' does not exist.")

    def _create_output_folder(self):
        """Creates the output folder if it does not exist."""
        os.makedirs(self.output_folder, exist_ok=True)

    def extract_frames(self):
        """
        Extracts frames from the video every 2 seconds.

        :return: List of file paths to the extracted frames.
        """
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise Exception("Failed to open the video file.")

        fps = cap.get(cv2.CAP_PROP_FPS)  # Get frames per second
        interval = int(fps * 1)  # Number of frames corresponding to 1 seconds

        frame_paths = []
        frame_count = 0
        frame_index = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % interval == 0:
                frame_name = f"frame_{frame_index:04d}.jpg"
                frame_path = os.path.join(self.output_folder, frame_name)
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                frame_index += 1

            frame_count += 1

        cap.release()
        return frame_paths

class InstaFetcher:
    def __init__(self, api_key: str):
        """
        Initialize the InstaFetcher with the provided API key.
        
        :param api_key: API key for authentication
        """
        # self.api_url = "https://instagram-scraper-api3.p.rapidapi.com/user_posts"
        # self.api_host = "instagram-scraper-api3.p.rapidapi.com"
        self.api_url = "https://instagram-scraper-api2.p.rapidapi.com/v1.2/posts"
        self.api_host = "instagram-scraper-api2.p.rapidapi.com"
        self.api_key = api_key

    def get_user_posts(self, username: str, count: int = 5):
        """
        Fetch user posts from the Instagram API.
        
        :param username: Instagram username or ID
        :param count: Number of posts to fetch (default is 5)
        :return: JSON response from the API
        """
        headers = {
            "x-rapidapi-host": self.api_host,
            "x-rapidapi-key": self.api_key,
        }
        params = {
            "username_or_id_or_url": username,
        }

        try:
            response = requests.get(self.api_url, headers=headers, params=params)
            response.raise_for_status()
            all_data = response.json()
            username = all_data["data"]["user"]["username"]
            all_posts_data = all_data["data"]["items"]
            posts = []
            for post in all_posts_data:
                post_code = post["code"]
                if post["is_video"] == False:
                    images_list = []
                    if "carousel_media" not in post:
                        images_list.append(post["image_versions"]["items"][0]["url"])
                    else:
                        images_data = post["carousel_media"]
                        for image in images_data:
                            images_list.append(image["image_versions"]["items"][0]["url"])
                            
                    posts.append({
                        "post_link": f"https://www.instagram.com/{username}/p/{post_code}/",
                        "image_url": images_list,
                        "description": post["caption"]["text"],
                    })
                else:
                    video_url = post["video_url"]
                    # video_file_path = self.download_video(video_url)
                    # extractor = VideoFrameExtractor(video_file_path)
                    # frame_files = extractor.extract_frames()
                    # get_quality = ImageQualityChecker(frame_files)
                    # quality_images = get_quality.start()
                    posts.append({
                        "post_link": f"https://www.instagram.com/{username}/p/{post_code}/",
                        "video_url": video_url,
                        "description": post["caption"]["text"],
                    })
            return posts
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None

# Example usage:
if __name__ == "__main__":
    api_key = input("Enter your API key: ")
    username = input("Enter the Instagram username: ")
    
    scraper = InstaFetcher(api_key)
    posts = scraper.get_user_posts(username)
    
    pprint(posts)
