import instaloader

# Initialize Instaloader
loader = instaloader.Instaloader()

# Log in if needed (optional, only for private profiles)
# loader.login('your_username', 'your_password')

# Specify the username
username = "bata.india"

# Fetch the profile
try:
    profile = instaloader.Profile.from_username(loader.context, username)

    # Fetch posts and download the latest 5
    posts = profile.get_posts()
    for i, post in enumerate(posts):
        if i >= 5:  # Limit to the latest 5 posts
            break
        print(f"Downloading post {i+1} - {post.url}")
        loader.download_post(post, target=f"{username}_post_{i+1}")
except Exception as e:
    print(f"An error occurred: {e}")
