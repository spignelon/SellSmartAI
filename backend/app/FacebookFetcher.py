import requests
from datetime import datetime, timedelta
from pprint import pprint

class FacebookFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_host = "facebook-scraper3.p.rapidapi.com"
    
    def get_page_id(self, profile_link):
        """
        Fetches the page ID from the given Facebook profile link.
        
        Args:
            profile_link (str): The Facebook profile link.
        
        Returns:
            str: The page ID if found, None otherwise.
        """
        url = f"https://{self.api_host}/page/page_id"
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
        }
        params = {"url": profile_link}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get("page_id")
        else:
            print(f"Error fetching page ID: {response.status_code}, {response.text}")
            return None
    
    def get_posts(self, page_id, start_date, end_date):
        """
        Fetches posts from a Facebook page within a given date range.
        
        Args:
            page_id (str): The ID of the Facebook page.
            start_date (str): The start date in 'YYYY-MM-DD' format.
            end_date (str): The end date in 'YYYY-MM-DD' format.
        
        Returns:
            dict: The response JSON containing the posts.
        """
        url = f"https://{self.api_host}/page/posts"
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.api_host,
        }
        params = {
            "page_id": page_id,
            "start_date": start_date,
            "end_date": end_date,
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            raw_data = response.json()
            posts = []
            for post in raw_data["results"]:
                images_list = []
                for image in post["album_preview"]:
                    images_list.append(image["image_file_uri"])
                posts.append({
                    "post_link": post["url"],
                    "image_url": images_list,
                    "description": post["message"]
                })
            return posts
        else:
            print(f"Error fetching posts: {response.status_code}, {response.text}")
            return None
    
    def fetch_posts_from_profile(self, profile_link):
        """
        Fetches posts from a Facebook profile link for the last seven days by first obtaining the page ID.
        
        Args:
            profile_link (str): The Facebook profile link.
        
        Returns:
            dict: The response JSON containing the posts.
        """
        # Calculate the date range for the last 7 days
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        # Fetch page ID
        page_id = self.get_page_id(profile_link)
        if not page_id:
            print("Failed to retrieve page ID.")
            return None
        
        print(f"Page ID fetched: {page_id}")
        # Fetch posts
        posts = self.get_posts(page_id, start_date, end_date)
        return posts

# Example usage:
if __name__ == "__main__":
    api_key = "01775ad35amsh438e2ccad6415c1p1c6a88jsn7156243a3153"
    scraper = FacebookFetcher(api_key)
    
    profile_link = "https://www.facebook.com/boat.lifestyle"
    
    posts = scraper.fetch_posts_from_profile(profile_link)
    if posts:
        pprint(posts)
