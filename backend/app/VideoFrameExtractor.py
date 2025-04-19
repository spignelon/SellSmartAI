import os
import uuid
import cv2
import tempfile
import requests
import random
import string
from django.conf import settings

class VideoFrameExtractor:
    def __init__(self, video_url):
        self.video_url = video_url
        # Generate a unique folder name for this extraction
        self.unique_folder_name = str(uuid.uuid4().hex)[:10]
        # Use absolute path for storage
        self.output_dir = os.path.join(settings.BASE_DIR, 'static', self.unique_folder_name)
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Created directory at: {self.output_dir}")

    def _download_video(self):
        """Download the video from the given URL and return the path to the downloaded file"""
        try:
            # Generate random filename
            random_alphanumeric_file_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            video_path = os.path.join(settings.BASE_DIR, "static", f"video_{random_alphanumeric_file_name}.mp4")
            
            # Download video with progress reporting
            print(f"Downloading video from {self.video_url}...")
            response = requests.get(self.video_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(video_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            if downloaded % (1024 * 1024) == 0:  # Report every MB
                                print(f"Downloaded {downloaded/(1024*1024):.1f}MB of {total_size/(1024*1024):.1f}MB ({percent:.1f}%)")
            
            print(f"Video downloaded and saved as: {video_path}")
            return video_path
        except Exception as e:
            print(f"Error downloading video: {str(e)}")
            raise

    def _validate_video_path(self):
        """Validates the existence of the video file."""
        if not os.path.isfile(self.video_path):
            raise FileNotFoundError(f"The video file '{self.video_path}' does not exist.")

    def _create_output_folder(self):
        """Create the output folder for extracted frames if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_frames(self):
        """Extract frames from the video and return a list of paths to the extracted frames"""
        try:
            self.video_path = self._download_video()
            self._validate_video_path()
            
            print(f"Opening video file: {self.video_path}")
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                raise Exception(f"Failed to open the video file: {self.video_path}")

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(f"Video has {total_frames} frames at {fps} FPS")
            
            # Calculate interval (1 frame per second)
            interval = max(1, int(fps))
            
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
                    success = cv2.imwrite(frame_path, frame)
                    
                    if success:
                        print(f"Saved frame {frame_index} to {frame_path}")
                        frame_paths.append(frame_path)
                        frame_index += 1
                    else:
                        print(f"Failed to save frame {frame_index}")

                frame_count += 1
                if frame_count % 100 == 0:
                    print(f"Processed {frame_count} frames...")

            cap.release()
            print(f"Extracted {len(frame_paths)} frames from video")
            
            # When returning frame paths, convert to URLs
            frame_urls = []
            for frame_path in frame_paths:
                # Get the path relative to the static directory
                rel_path = os.path.relpath(frame_path, os.path.join(settings.BASE_DIR, 'static'))
                url_path = f"/static/{rel_path}"
                frame_urls.append(url_path)
                
            return frame_urls
            
        except Exception as e:
            print(f"Error in extract_frames: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

# Example usage
if __name__ == "__main__":
    video_file = "/home/byte/Projects/hackathons/amazon_sambhav/reel_images/watch.mp4"
    extractor = VideoFrameExtractor(video_file)
    frame_files = extractor.extract_frames()
    print("Extracted frames:", frame_files)