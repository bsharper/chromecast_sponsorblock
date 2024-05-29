import pychromecast
import requests
import time
import json
import os
import logging
from datetime import datetime, timedelta
import yt_dlp 

# Constants
SPONSORBLOCK_API = "https://sponsor.ajay.app/api/skipSegments"
CHROMECAST_NAME = "Living Room TV"
CACHE_FILE = "sponsorblock_cache.json"
CACHE_EXPIRATION_HOURS = 2

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_chromecast():
    chromecasts, _ = pychromecast.get_listed_chromecasts(friendly_names=[CHROMECAST_NAME])
    if not chromecasts:
        logger.error("Chromecast not found")
        raise ValueError("Chromecast not found")
    logger.info(f"Connected to Chromecast: {CHROMECAST_NAME}")
    return chromecasts[0]

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            cache = json.load(file)
            logger.info("Cache loaded")
            return cache
    logger.info("No cache file found, starting with an empty cache")
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file)
    logger.info("Cache saved")

def is_cache_expired(timestamp):
    cache_time = datetime.fromisoformat(timestamp)
    return datetime.now() > cache_time + timedelta(hours=CACHE_EXPIRATION_HOURS)

def get_sponsorblock_segments(cache_key):
    cache = load_cache()
    
    if cache_key in cache and not is_cache_expired(cache[cache_key]['timestamp']):
        logger.info(f"Using cached segments for key: {cache_key}")
        return cache[cache_key]['segments'], cache[cache_key]['video_id']

    logger.info(f"Fetching segments from SponsorBlock for key: {cache_key}")
    video_id = search_youtube_video_id(cache_key)
    if not video_id:
        logger.error(f"Failed to find video ID for key: {cache_key}")
        #return [], None
        segments = []
    else:
        response = requests.get(f"{SPONSORBLOCK_API}?videoID={video_id}")
        if response.status_code != 200:
            logger.error(f"No segments found for video ID: {video_id}")
            segments = []
            #return [], None
        else:
            segments = [seg for seg in response.json() ]
        
    cache[cache_key] = {
        'segments': segments,
        'video_id': video_id,
        'timestamp': datetime.now().isoformat()
    }
    save_cache(cache)
    segments = [ seg for seg in segments if seg['category'] in ('sponsor', 'selfpromo')]
    return segments, video_id


def search_youtube_video_id(query):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'format': 'best',
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'] 
            if len(results) > 0:
                return results[0]['id']
            else:
                return ""
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

def monitor_chromecast(cast):
    cast.wait()
    mc = cast.media_controller
    mc.block_until_active()
    played_segments = set()
    sleep_time = 1    
    while True:
        #cast.wait()  # Update status
        #mc = cast.media_controller
        mc.update_status()
        if mc.status.player_state == "PLAYING" and "YouTube" == cast.app_display_name:
            sleep_time = 1
            title = mc.status.title
            artist = mc.status.artist
            if title and artist:
                cache_key = f"{artist} {title}"
                segments, video_id = get_sponsorblock_segments(cache_key)
                if video_id:
                    current_time = mc.status.current_time
                    remaining_segments = [ segment for segment in segments if segment['segment'][0] not in played_segments]
                    logging.info(f"Current time in video: {current_time}, remaining segments: {len(remaining_segments)}")
                    for segment in segments:
                        if segment['segment'][0] <= current_time <= segment['segment'][1] and segment['segment'][0] not in played_segments:
                            logger.info(f"Skipping segment from {segment['segment'][0]} to {segment['segment'][1]} for key: {cache_key}")
                            mc.seek(segment['segment'][1])
                            played_segments.add(segment['segment'][0])
        else:
            sleep_time = 3

        time.sleep(1)

if __name__ == "__main__":
    chromecast = get_chromecast()
    monitor_chromecast(chromecast)
    # try:
    # except Exception as e:
    #     logger.error(f"An error occurred: {e}")
