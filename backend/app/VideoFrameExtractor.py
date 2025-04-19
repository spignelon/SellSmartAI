import os
import uuid
import cv2
import tempfile
import requests
from django.conf import settings

class VideoFrameExtractor:
    def __init__(self, video_url):
        self.video_url = video_url
        # Generate a unique folder name for this extraction
        self.unique_folder_name = str(uuid.uuid4().hex)[:10]
        # Use STATIC_ROOT for file storage
        self.output_dir = os.path.join(settings.BASE_DIR, 'static', self.unique_folder_name)
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Created directory at: {self.output_dir}")

    def _download_video(self):
        """Download the video from the given URL and return the path to the downloaded file"""
        random_alphanumeric_file_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        filename = f"static/video_{random_alphanumeric_file_name}.mp4"
        try:
            response = requests.get(self.video_url)
            response.raise_for_status()
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"Video downloaded and saved as: {filename}")
            return filename
        except requests.exceptions.RequestException as e:
            print(f"An error occurred")

    def _validate_video_path(self):
        """Validates the existence of the video file."""
        if not os.path.isfile(self.video_path):
            raise FileNotFoundError(f"The video file '{self.video_path}' does not exist.")

    def _create_output_folder(self):
        """Create the output folder for extracted frames if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_frames(self):
        """Extract frames from the video and return a list of paths to the extracted frames"""
        self.video_path = self._download_video()
        self._validate_video_path()
        self._create_output_folder()
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
                frame_path = os.path.join(self.output_dir, frame_name)
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
                frame_index += 1

            frame_count += 1

        cap.release()
        
        # When returning frame paths, convert to full URLs
        frame_urls = []
        for frame_file in frame_paths:
            # Get relative path from STATIC_ROOT
            relative_path = os.path.relpath(frame_file, settings.STATIC_ROOT)
            # Create URL using STATIC_URL
            frame_url = f"{settings.STATIC_URL}{relative_path}"
            # For development, add the full URL if not already present
            if settings.DEBUG and not frame_url.startswith('http'):
                # Use your site domain - in development this is typically localhost:8000
                frame_url = f"http://127.0.0.1:8000{frame_url}"
            frame_urls.append(frame_url)
            
        return frame_urls

# Example usage
if __name__ == "__main__":
    video_file = "/home/byte/Projects/hackathons/amazon_sambhav/reel_images/watch.mp4"
    extractor = VideoFrameExtractor(video_file)
    frame_files = extractor.extract_frames()
    print("Extracted frames:", frame_files)