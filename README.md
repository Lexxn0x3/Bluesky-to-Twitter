# 🐾 Bluesky-to-Twitter: Post Automation 🐾

Welcome to the **Bluesky-to-Twitter** automation tool! Are you tired of manually crossposting all your adorable Bluesky posts onto Twitter? Let this handy program take over your paws so you can focus on more important things—like napping in the sun or chasing virtual tail! 🐾✨

This project fetches your latest Bluesky posts and automagically posts them to your Twitter, complete with media uploads, quotes, and embeds. Now that’s pawsome! 🦊🐱

## 🌟 Features
- **Automated posting from Bluesky to Twitter** 🐾
- **Handles text, media, and quote posts** 🖼️
- **Supports Twitter API for uploading images and creating Tweets** 📸

---

## 🛠️ Setup Guide (Because Even Smart Foxes Need Instructions)

To set this up and run with your furry paws free, follow these steps:

### 1. Clone this repo 🐱‍💻
```bash
git clone https://github.com/your-furry-repo/bluesky-to-twitter.git
cd bluesky-to-twitter
```

### 2. Install the Dependencies 🍂
Run the following command to install all the necessary Python dependencies:
```bash
pip install -r requirements.txt
```

### 3. Create Your Own Config File 🦊
The config is stored in a `.toml` file. You’ll need to create `config.toml` in the root directory. Here’s a template to help you along:

```toml
# config.toml 🐾 Example Configuration

[twitter]
# Go to https://developer.x.com/en/portal/dashboard to create your API keys to interact with Twitter.
api_key = "YOUR_TWITTER_API_KEY"  # Your Twitter API key (grab your shiny key from the Twitter dev portal!)
api_secret_key = "YOUR_TWITTER_API_SECRET_KEY"
access_token = "YOUR_TWITTER_ACCESS_TOKEN"
access_token_secret = "YOUR_TWITTER_ACCESS_TOKEN_SECRET"

[bluesky]
username = "lexxvr.bsky.social"  # Your Bluesky username 🐾 (example: lexxvr.bsky.social)
password = "your_bluesky_password"  # Your Bluesky password 🐾 (shhh... keep this a secret!)
identifier = "youremail@domain.com"  # Your Bluesky identifier (usually your email)
refresh = 300 # Fetch new posts every 5 minutes
```

### 4. Get Twitter API Keys 🐦
To let this adorable program post on your behalf, you’ll need to generate API keys from Twitter:

1. Go to [Twitter Developer Dashboard](https://developer.x.com/en/portal/dashboard) and create a new app.
2. Generate your **API key**, **API secret key**, **Access token**, and **Access token secret**.
3. Place them into the `config.toml` file under `[twitter]`.

### 5. Run the program 🐾
```bash
python main.py
```

That's it! The magic begins, and your latest Bluesky posts will be pawsitively racing their way onto Twitter. 🏃‍♀️✨

---

## 📸 Tweet Previews with Embeds!

Twitter doesn’t give previews for Bluesky posts by default. But don’t worry! This little app will generate a beautiful embed, complete with the post’s image and a link back to the full post on Bluesky. If you want to host this service yourself:

- Simply run `preview.py`:
  ```ash
  python preview.py
  ```
  And access it at `http://localhost:3030/preview/<handle>/post/<post_id>`. 

Or, if you're feeling lazy, you can use **my hosted version** at:

`https://bluesky.owo.nexus/preview/<handle>/post/<post_id>` 🦊✨

---

## 🦊🦄 Enjoy OwO
