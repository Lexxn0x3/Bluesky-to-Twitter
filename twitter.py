import requests
from requests_oauthlib import OAuth1
import os
from config import Config

auth = OAuth1(
    Config.TWITTER_API_KEY,
    Config.TWITTER_API_SECRET_KEY,
    Config.TWITTER_ACCESS_TOKEN,
    Config.TWITTER_ACCESS_TOKEN_SECRET
)
# Step 1: Upload image to Twitter
def download_media(media_url):
    """
    Downloads media from the given URL and returns the local file path.
    """
    media_filename = media_url.split('/')[-1].replace('@jpeg', '.jpeg')  # Extract filename from URL
    local_path = os.path.join('/tmp', media_filename)  # Save in the /tmp directory
    
    response = requests.get(media_url)
    
    if response.status_code == 200:
        with open(local_path, 'wb') as media_file:
            media_file.write(response.content)
        return local_path
    else:
        raise Exception(f"Failed to download media: {response.status_code}")

def upload_media(media_url):
    """
    Uploads media to Twitter after downloading it locally.
    """
    # Step 1: Download the media file
    media_path = download_media(media_url)

    # Step 2: Use the downloaded media file to upload to Twitter
    files = {"media": open(media_path, "rb")}
    
    # Twitter API endpoint for media upload (you may need to adjust this)
    url = "https://upload.twitter.com/1.1/media/upload.json"

    response = requests.post(url, files=files, auth=auth)

    if response.status_code == 200:
        media_id = response.json().get("media_id_string")
        return media_id
    else:
        raise Exception(f"Failed to upload media to Twitter: {response.status_code}")

def convert_bluesky_to_preview_url(bluesky_url):
    """
    Converts a Bluesky post URL to your custom preview URL format.
    """
    try:
        # Example Bluesky URL: https://bsky.app/profile/centralscruty.bsky.social/post/3l6zrfcjs2y2t
    # Desired preview URL: https://bluesky.owo.nexus/preview/centralscruty.bsky.social/post/3l6zrfcjs2y2t

        # Split the Bluesky URL to extract the handle and post ID
        parts = bluesky_url.split('/')
        handle = parts[4]  # The handle is in the 5th position
        post_id = parts[6]  # The post ID is in the 7th position

        # Construct the preview URL
        preview_url = f"https://bluesky.owo.nexus/preview/{handle}/post/{post_id}"
        return preview_url

    except IndexError:
        print("Invalid Bluesky URL format.")
        return None

# Step 2: Post a tweet with the uploaded image and a quoted Bluesky post
def post_tweet_with_media_and_quote(text, media_id=None, quoted_url=None):
    tweet_url = "https://api.x.com/2/tweets"

    payload = {
        "text": text
    }

    # Add media to tweet if media_id is provided
    if media_id:
        payload["media"] = {"media_ids": [media_id]}

    # Convert Bluesky URL to preview URL and add it to the tweet text
    if quoted_url:
        preview_url = convert_bluesky_to_preview_url(quoted_url)
        if preview_url:
            payload["text"] += f"\n\n{preview_url}"
        else:
            print(f"Failed to convert quoted Bluesky URL: {quoted_url}")

    response = requests.post(tweet_url, json=payload, auth=auth)

    if response.status_code == 201:
        print("Tweet posted successfully:", response.json())
        return response
    else:
        print(f"Failed to post tweet. Status code: {response.status_code}, Response: {response.text}")
        return response

def comment_with_original_post(tweet_id, post_data):
    """
    Comment on the Twitter post with a link to the original Bluesky post.
    Accesses the author_handle directly from the post_data.
    """
    uri = post_data.get('uri')
    author_handle = post_data.get('author_handle')  # Access the author handle from post_data
    post_id = uri.split('/')[-1]  # Extract the last part of the URI
    bluesky_url = f"https://bsky.app/profile/{author_handle}/post/{post_id}"

    tweet_url = "https://api.x.com/2/tweets"

    # Payload for replying to the tweet with the original Bluesky URL
    payload = {
        "text": f"Original post on Bluesky: {convert_bluesky_to_preview_url(bluesky_url)}",
        "reply": {
            "in_reply_to_tweet_id": tweet_id
        }
    }

    response = requests.post(tweet_url, json=payload, auth=auth)

    if response.status_code == 201:
        print(f"Comment posted successfully: {response.json()}")
    else:
        print(f"Failed to post comment. Status code: {response.status_code}, Response: {response.text}")

