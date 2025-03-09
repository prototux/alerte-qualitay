import discord
from discord.ext import tasks, commands
import yaml
import os
import logging
from yt_dlp import YoutubeDL

logger = logging.getLogger(__name__)

# Load the configuration file
def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)

# Load the cache file
def load_cache():
    with open("cache.yaml", "r") as f:
        return yaml.safe_load(f)

# Save the cache file
def save_cache(cache):
    with open("cache.yaml", "w") as f:
        yaml.safe_dump(cache, f)

# Fetch the latest video using yt-dlp
def get_latest_video(channel_url):
    ydl_opts = {
        "quiet": True,
        "extract_flat": "yes",  # Only extract metadata, not download content
        "playlist_items": "1",  # Get only the first video
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(channel_url, download=False)
            if "entries" in result and len(result["entries"]) > 0:
                video = result["entries"][0]
                return {
                    "id": video["id"],
                    "title": video["title"],
                    "url": video["url"]
                }
    except Exception as e:
        print(f"Error fetching video for {channel_url}: {e}")
    return None

class YouTubeBot(commands.Bot):
    def __init__(self, cache, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.dis_chan = os.getenv("DISCORD_CHANNEL_ID")
        self.cache = cache

    async def on_ready(self):
        logger.error(f"Logged in as {self.user}")
        if not self.check_videos.is_running():
            self.check_videos.start()

    @tasks.loop(hours=1)
    async def check_videos(self):
        for channel in self.config["channels"]:
            latest_video = get_latest_video(channel)
            if not latest_video:
                continue

            cached_video_id = self.cache["cache"].get(channel)
            if cached_video_id == latest_video["id"]:
                continue

            # Update cache
            self.cache["cache"][channel] = latest_video["id"]
            save_cache(self.cache)

            # Send message to Discord
            discord_channel = self.get_channel(self.dis_chan)
            if discord_channel:
                message = f"Alerte Qualitaÿ: {latest_video['title']}\\n{latest_video['url']}"
                await discord_channel.send(message)

if __name__ == "__main__":
    # Retrieve bot token from environment variables
    discord_bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not discord_bot_token:
        print("Error: DISCORD_BOT_TOKEN environment variable is not set.")
        exit(1)

    intents = discord.Intents.default()
    bot = YouTubeBot(load_cache(), load_config(), command_prefix="!", intents=intents)

    bot.run(discord_bot_token)
