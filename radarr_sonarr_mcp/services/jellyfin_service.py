import logging
import requests
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class JellyfinService:
    """
    Service for interacting with the Jellyfin API.
    This service searches for a series by title and retrieves its episodes to check the watch status.
    """
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get("baseUrl")  # e.g., "http://10.0.0.23:5055"
        self.api_key = config.get("apiKey")
        self.user_id = config.get("userId")  # The user ID to check watch status for

    def search_series(self, title: str) -> List[Dict[str, Any]]:
        """
        Search for a series in Jellyfin by title.
        """
        url = f"{self.base_url}/Users/{self.user_id}/Items"
        params = {
            "IncludeItemTypes": "Series",
            "SearchTerm": title,
            "api_key": self.api_key
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("Items", [])

    def get_episodes_for_series(self, series_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve episodes for a given series ID from Jellyfin.
        """
        url = f"{self.base_url}/Users/{self.user_id}/Items"
        params = {
            "ParentId": series_id,
            "IncludeItemTypes": "Episode",
            "api_key": self.api_key
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("Items", [])

    def is_series_watched(self, series_title: str) -> bool:
        """
        Determine if the series is watched.
        A series is considered watched if all episodes have a PlayCount > 0.
        """
        items = self.search_series(series_title)
        if not items:
            return False
        series_item = items[0]  # take the first match
        series_id = series_item.get("Id")
        episodes = self.get_episodes_for_series(series_id)
        if not episodes:
            return False
        # Consider the series watched if every episode has a PlayCount > 0
        return all(ep.get("UserData", {}).get("PlayCount", 0) > 0 for ep in episodes)

    def search_movie(self, title: str) -> List[Dict[str, Any]]:
        """
        Search for a movie in Jellyfin by title.
        """
        url = f"{self.base_url}/Users/{self.user_id}/Items"
        params = {
            "IncludeItemTypes": "Movie",
            "SearchTerm": title,
            "api_key": self.api_key
        }
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("Items", [])

    def is_movie_watched(self, movie_title: str) -> bool:
        """
        Determine if a movie is watched.
        A movie is considered watched if it has a PlayCount > 0.
        """
        items = self.search_movie(movie_title)
        if not items:
            return False
        movie_item = items[0]  # take the first match
        return movie_item.get("UserData", {}).get("PlayCount", 0) > 0
