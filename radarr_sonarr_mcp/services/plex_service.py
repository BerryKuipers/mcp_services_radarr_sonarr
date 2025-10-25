import logging
import requests
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class PlexService:
    """
    Service for interacting with the Plex API.
    
    Note: Plex’s API typically returns XML, but here we assume a JSON endpoint 
    (or you can use an XML parser). This is a simplified example.
    """
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get("baseUrl")  # e.g., "http://10.0.0.23:32400"
        self.token = config.get("token")
    
    def search_series(self, title: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/library/search"
        params = {
            "query": title,
            "type": 4  # type 4 usually indicates a TV series
        }
        headers = {"X-Plex-Token": self.token}
        response = requests.get(url, params=params, headers=headers, timeout=30)
        # In a real implementation, parse XML; here we assume JSON for simplicity.
        try:
            return response.json().get("MediaContainer", {}).get("Metadata", [])
        except Exception:
            return []
    
    def get_episodes_for_series(self, rating_key: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/library/metadata/{rating_key}/children"
        headers = {"X-Plex-Token": self.token}
        response = requests.get(url, headers=headers, timeout=30)
        try:
            return response.json().get("MediaContainer", {}).get("Metadata", [])
        except Exception:
            return []
    
    def is_series_watched(self, series_title: str) -> bool:
        items = self.search_series(series_title)
        if not items:
            return False
        # Assume the first matching series is our target.
        series_item = items[0]
        rating_key = series_item.get("ratingKey")
        episodes = self.get_episodes_for_series(rating_key)
        if not episodes:
            return False
        # Consider the series watched if every episode's UserData indicates it was played.
        return all(ep.get("UserData", {}).get("viewCount", 0) > 0 for ep in episodes)
    
    def search_movie(self, title: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/library/search"
        params = {
            "query": title,
            "type": 2  # type 2 for movies
        }
        headers = {"X-Plex-Token": self.token}
        response = requests.get(url, params=params, headers=headers, timeout=30)
        try:
            return response.json().get("MediaContainer", {}).get("Metadata", [])
        except Exception:
            return []
    
    def is_movie_watched(self, movie_title: str) -> bool:
        items = self.search_movie(movie_title)
        if not items:
            return False
        movie_item = items[0]
        return movie_item.get("UserData", {}).get("viewCount", 0) > 0
