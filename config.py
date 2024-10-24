import toml
import os

class Config:
    # Class-level attributes to store configuration
    TWITTER_API_KEY = None
    TWITTER_API_SECRET_KEY = None
    TWITTER_ACCESS_TOKEN = None
    TWITTER_ACCESS_TOKEN_SECRET = None
    BLUESKY_USERNAME = None
    BLUESKY_PASSWORD = None
    BLUESKY_IDENTIFIER = None
    BLUESKY_REFRESH = None

    @classmethod
    def init(cls, config_path="config.toml"):
        """
        Initializes the configuration by loading the .toml file and assigning values
        to class-level attributes.
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file '{config_path}' not found.")
        
        # Load the .toml configuration file
        with open(config_path, 'r') as f:
            config_data = toml.load(f)

        # Assign the values from the file to class-level attributes
        cls.TWITTER_API_KEY = config_data['twitter']['api_key']
        cls.TWITTER_API_SECRET_KEY = config_data['twitter']['api_secret_key']
        cls.TWITTER_ACCESS_TOKEN = config_data['twitter']['access_token']
        cls.TWITTER_ACCESS_TOKEN_SECRET = config_data['twitter']['access_token_secret']

        cls.BLUESKY_USERNAME = config_data['bluesky']['username']
        cls.BLUESKY_PASSWORD = config_data['bluesky']['password']
        cls.BLUESKY_IDENTIFIER = config_data['bluesky']['identifier']
        cls.BLUESKY_REFRESH = config_data['bluesky']['refresh']

        print("Configuration initialized successfully.")


