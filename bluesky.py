import requests
import os
from config import Config

# File to store the Bearer token
TOKEN_FILE = 'bsky_token.txt'

def save_token(token):
    """Save the Bearer token to a file."""
    with open(TOKEN_FILE, 'w') as f:
        f.write(token)

def load_token():
    """Load the Bearer token from the file."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return None

def login_and_get_token():
    """Login and retrieve the Bearer token."""
    login_url = 'https://bsky.social/xrpc/com.atproto.server.createSession'
    
    login_data = {
        "identifier": Config.BLUESKY_IDENTIFIER,
        "password": Config.BLUESKY_PASSWORD,
        "authFactorToken": ""
    }

    login_response = requests.post(login_url, json=login_data)

    if login_response.status_code == 200:
        login_response_json = login_response.json()
        if 'accessJwt' in login_response_json:
            token = login_response_json['accessJwt']
            save_token(token)
            return token
        else:
            raise Exception("Login succeeded, but no Bearer token found.")
    else:
        raise Exception(f"Login failed with status code {login_response.status_code}: {login_response.text}")

def get_fullsize_image_url(embed):
    """Extract the full-size image URL from the embed block if it's an image."""
    if embed.get('$type') == 'app.bsky.embed.images#view':
        images = embed.get('images', [])
        if images:
            return images[0].get('fullsize')  # Get the full-size image URL
    return None

def get_quoted_post_url(embed):
    """Construct the URL for the quoted post."""
    if embed.get('$type') == 'app.bsky.embed.record#view':
        quoted_post = embed.get('record', {})
        author_handle = quoted_post.get('author', {}).get('handle')
        post_uri = quoted_post.get('uri', '')
        post_id = post_uri.split('/')[-1]  # Extract the post ID from the URI
        if author_handle and post_id:
            return f"https://bsky.app/profile/{author_handle}/post/{post_id}"
    return None

def get_bsky_posts():
    """Fetch posts and filter for the author and post type."""
    # Load the token if available, otherwise log in
    token = load_token()
    if not token:
        print("no token... loggin in...")
        token = login_and_get_token()

    posts_url = "https://porcini.us-east.host.bsky.network/xrpc/app.bsky.feed.getAuthorFeed?actor=did:plc:i4rdsz3ihxtbzkowuqzrhilc&limit=30"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cache-Control": "no-cache"
    }

    # Send the GET request
    posts_response = requests.get(posts_url, headers=headers)

    if posts_response.status_code == 200:
        posts_data = posts_response.json()
        return filter_posts(posts_data)

        
    elif posts_response.status_code == 400:
        error_data = posts_response.json()
        if error_data.get("error") == "ExpiredToken":
            print("Token expired. Attempting to refresh and retry...")
            # Refresh token and retry once
            token = login_and_get_token()
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(posts_url, headers=headers)

            if response.status_code == 200:
                return filter_posts(response.json())
            else:
                print("Failed after retry. Aborting.")
                return None
        else:
            print(f"Failed to fetch posts. Status code: {posts_response.status_code}")
            return None
    else:
        print(f"Failed to fetch posts. Status code: {posts_response.status_code}")
        print(posts_response.text)

def filter_posts(posts_data):
    """
    Filters posts from Bluesky, extracting relevant information such as URI, text, media, or quoted post.
    Returns a list of dictionaries containing the post type and necessary details.
    """
    filtered_posts = []

    # Iterate through the feed and extract relevant posts
    for feed_item in posts_data.get('feed', []):
        post = feed_item.get('post', {})
        author = post.get('author', {})
        record = post.get('record', {})
        record_embed = record.get('embed', {})
        outer_embed = post.get('embed', {})

        # Check if the author matches, if the record type is correct, and if the post is not a reply
        if (
            author.get('handle') == Config.BLUESKY_USERNAME and
            record.get('$type') == 'app.bsky.feed.post' and
            'reply' not in record  # Exclude posts that are replies
        ):
            text = record.get('text')
            uri = post.get('uri')
            author_handle = author.get('handle', 'unknown')

            post_data = {
                'uri': uri,
                'text': text,
                'type': 'text',  # Default to text-only
                'media_url': None,
                'quoted_post_url': None,
                'author_handle': author_handle  # Add author handle
            }

            # Case 1: Text-only post
            if not record_embed and not outer_embed:
                post_data['type'] = 'text'

            # Case 2: Post with media (extracting the fullsize image URL)
            elif outer_embed.get('$type') == 'app.bsky.embed.images#view':
                media_url = get_fullsize_image_url(outer_embed)
                post_data['type'] = 'media'
                post_data['media_url'] = media_url

            # Case 3: Quote retweet (quoted post)
            elif outer_embed.get('$type') == 'app.bsky.embed.record#view':
                quoted_post_url = get_quoted_post_url(outer_embed)
                post_data['type'] = 'quote'
                post_data['quoted_post_url'] = quoted_post_url

            # Append the post data to the list
            filtered_posts.append(post_data)

    return filtered_posts

