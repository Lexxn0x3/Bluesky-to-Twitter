import json
import os
from time import sleep
from bluesky import get_bsky_posts
from twitter import post_tweet_with_media_and_quote, upload_media, comment_with_original_post
from config import Config

# File to store the last processed posts
LAST_POSTS_FILE = 'last_posts.json'

def load_last_posts():
    """Load the last processed posts from the file."""
    if os.path.exists(LAST_POSTS_FILE):
        with open(LAST_POSTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_last_posts(posts):
    """Save the latest posts to the file."""
    with open(LAST_POSTS_FILE, 'w') as f:
        json.dump(posts, f)

def get_new_posts(current_posts, last_posts):
    """Compare current posts with the last processed posts to find new posts."""
    # Assuming each post has a unique 'uri', filter out the posts that were already processed
    last_post_uris = {post['uri'] for post in last_posts}
    new_posts = [post for post in current_posts if post['uri'] not in last_post_uris]
    return new_posts

def process_posts_and_tweet(new_posts):
    """Process each new post and post it to Twitter."""
    for post in new_posts:
        ptype = post.get("type", None)
        text = post.get('text', '')
        media_url = post.get('media_url', None)
        quoted_post_url = post.get('quoted_post_url', None)
        bluesky_url = post.get('uri', '')  # URL to the original Bluesky post

        tweet_response = None
        
        
        # Case 1: Text-only post
        if ptype == "text":
            print(f"Processing text-only post: {text}")
            tweet_response = post_tweet_with_media_and_quote(text)
        
        # Case 2: Post with media
        elif ptype == "media":
            print(f"Processing post with media: {text}")
            media_id = upload_media(media_url)
            tweet_response = post_tweet_with_media_and_quote(text, media_id)
        
        # Case 3: Quote retweet post
        elif ptype == "quote":
            print(f"Processing quote retweet post: {text}")
            tweet_response = post_tweet_with_media_and_quote(text, quoted_url=quoted_post_url)

        # Post a comment with the original Bluesky link after tweeting
        if tweet_response and tweet_response.status_code == 201:
            tweet_data = tweet_response.json()
            tweet_id = tweet_data['data']['id']
            comment_with_original_post(tweet_id, post)

def main():
    Config.init()
    while(True): 
    # Step 1: Load the last processed posts
        last_posts = load_last_posts()

    # Step 2: Get current posts from Bluesky
        current_posts = get_bsky_posts()

    # Step 3: Identify new posts
        new_posts = get_new_posts(current_posts, last_posts)

        if not new_posts:
            print("No new posts found.")

    # Step 4: Process and tweet new posts
        process_posts_and_tweet(new_posts)

    # Step 5: Save the latest posts for next time
        save_last_posts(current_posts)

        sleep(Config.BLUESKY_REFRESH)

if __name__ == "__main__":
    main()

