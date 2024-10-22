from flask import Flask, request, jsonify, render_template_string, redirect
import requests
from bs4 import BeautifulSoup
import cv2  # For handling video frames
from diskcache import Cache
# Initialize cache (stored in a directory on disk)
cache_dir = './cache'  # You can change this to your preferred cache directory
cache = Cache(cache_dir)
app = Flask(__name__)

# Template for the dynamic HTML preview


preview_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta property="og:title" content="{{ display_name }}">
    <meta property="og:description" content="{{ preview_text }}">
    <meta property="og:image" content="{{ image_url }}">
    <meta property="og:url" content="{{ bluesky_url }}">
    <meta property="twitter:card" content="summary">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .container {
            display: flex;
            align-items: flex-start;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            max-width: 600px;
        }
        .thumbnail {
            margin-right: 15px;
            flex-shrink: 0;
        }
        .thumbnail img {
            max-width: 100px;
            border-radius: 8px;
        }
        .content {
            flex-grow: 1;
        }
        .content h1 {
            font-size: 18px;
            margin: 0;
        }
        .content p {
            margin-top: 8px;
            font-size: 14px;
            color: #555;
        }
        a {
            text-decoration: none;
            color: #1da1f2;
        }
    </style>
    <title>{{ display_name }}'s Bluesky Post</title>
</head>
<body>
    <div class="container">
        {% if image_url %}
        <div class="thumbnail">
            <img src="{{ image_url }}" alt="Bluesky Post Image">
        </div>
        {% endif %}
        <div class="content">
            <h1>{{ display_name }}</h1>
            <p>{{ preview_text }}</p>
            <a href="{{ bluesky_url }}">View Full Post on Bluesky</a>
        </div>
    </div>
</body>
</html>
"""


def fetch_bluesky_post(handle, post_id):
    post_url = f"https://bsky.app/profile/{handle}/post/{post_id}"
    response = requests.get(post_url)

    if response.status_code != 200:
        print(f"Failed to fetch Bluesky post. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract necessary information with error handling
    try:
        display_name_meta = soup.find('meta', {'property': 'og:title'})
        post_text_meta = soup.find('meta', {'property': 'og:description'})
        image_meta = soup.find('meta', {'property': 'og:image'})
        twitter_card = soup.find('meta', {'name': 'twitter:card'})

        display_name = display_name_meta['content'] if display_name_meta else "Unknown"
        post_text = post_text_meta['content'] if post_text_meta else "No text available"
        image_url = image_meta['content'] if image_meta else None

        # If the card type indicates a summary (e.g., video or embed), fetch additional info
        if twitter_card and twitter_card['content'] == 'summary':
            api_url = f"https://public.api.bsky.app/xrpc/app.bsky.feed.getPostThread?uri=at%3A%2F%2F{handle}%2Fapp.bsky.feed.post%2F{post_id}&depth=10"
            api_response = requests.get(api_url)

            if api_response.status_code == 200:
                data = api_response.json()
                post = data['thread']['post']
                author = post['author']
                video_link = post.get('record', {}).get('embed', {}).get('video', {}).get('ref', {}).get('$link')
                if video_link:
                    did = author['did']
                    thumbnail_url = f"https://video.bsky.app/watch/{did}/{video_link}/thumbnail.jpg"
                    image_url = thumbnail_url

    except (KeyError, TypeError, AttributeError) as e:
        print(f"Error while extracting data: {e}")
        return None

    # Return the post data
    return {
        "display_name": display_name,
        "text": post_text,
        "image_url": image_url,
        "bluesky_url": post_url
    }

@app.route("/preview/<handle>/post/<post_id>", methods=["GET"])
def generate_preview(handle, post_id):
    # Check if the request is from a web browser (not for embedding)
    user_agent = request.headers.get('User-Agent', '').lower()

    # Detect if the request is for a direct visit (not an embed) and redirect
    if 'twitterbot/1.0' not in user_agent and 'facebookexternalhit' not in user_agent and 'linkedinbot' not in user_agent:
        return redirect(f"https://bsky.app/profile/{handle}/post/{post_id}")

    # Define the cache key
    cache_key = f"{handle}/{post_id}"

    # Check if the fully rendered HTML is in the cache
    cached_html = cache.get(cache_key)

    if cached_html:
        # Return the cached HTML without further processing
        print(f"Cache hit for {cache_key}")
        return cached_html

    print(f"Cache miss for {cache_key}, generating preview...")

    # Fetch the Bluesky post data
    post_data = fetch_bluesky_post(handle, post_id)

    if post_data:
        # Truncate the text to the first 200 characters
        preview_text = post_data["text"][:200] + "..." if len(post_data["text"]) > 200 else post_data["text"]

        # Render the preview HTML
        rendered_html = render_template_string(preview_template,
                                               display_name=post_data["display_name"],
                                               preview_text=preview_text,
                                               image_url=post_data["image_url"],
                                               handle=handle,
                                               post_id=post_id)

        # Cache the rendered HTML
        cache.set(cache_key, rendered_html, expire=3600)  # Cache for 1 hour

        # Return the rendered HTML
        return rendered_html
    else:
        return "Post not found or unsupported post type", 404

# Don't forget to close the cache properly
@app.teardown_appcontext
def close_cache(exception):
    cache.close()

if __name__ == "__main__":
    app.run(host="10.18.40.163", debug=True, port=3030)

