"""Service for interacting with Trakt.tv API."""

import logging
import requests
from typing import Any, Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TraktService:
    """
    Service for interacting with the Trakt.tv API.

    Trakt provides watch history, recommendations, trending content,
    and social features for movies and TV shows.

    Authentication:
        Trakt uses OAuth 2.0. For read-only operations, you can use
        a Client ID. For user-specific data, you need an Access Token.
    """

    BASE_URL = "https://api.trakt.tv"
    API_VERSION = "2"

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Trakt service.

        Args:
            config: Configuration dict with keys:
                - client_id: Trakt application client ID (required)
                - access_token: User access token (optional, for user-specific data)
                - client_secret: Application secret (optional, for OAuth)
        """
        self.client_id = config.get("clientId", "")
        self.access_token = config.get("accessToken", "")
        self.client_secret = config.get("clientSecret", "")

        # Cache for watch history to avoid redundant API calls
        self._watched_movies_cache: Optional[List[Dict[str, Any]]] = None
        self._watched_shows_cache: Optional[List[Dict[str, Any]]] = None

        if not self.client_id:
            logger.warning("Trakt client_id not configured. Some features may not work.")

    def _get_headers(self, authenticated: bool = False) -> Dict[str, str]:
        """
        Get request headers for Trakt API.

        Args:
            authenticated: Whether to include access token

        Returns:
            Dictionary of headers
        """
        headers = {
            "Content-Type": "application/json",
            "trakt-api-version": self.API_VERSION,
            "trakt-api-key": self.client_id,
        }

        if authenticated and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"

        return headers

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        authenticated: bool = False,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make a request to the Trakt API.

        Args:
            endpoint: API endpoint (without base URL)
            method: HTTP method (GET, POST, etc.)
            authenticated: Whether authentication is required
            params: URL parameters
            data: Request body data

        Returns:
            JSON response data

        Raises:
            Exception: If request fails
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers(authenticated)

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30,
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.RequestException as e:
            logger.error(f"Trakt API request failed: {e}")
            raise Exception(f"Failed to fetch from Trakt: {e}")

    # =========================================================================
    # Watch History
    # =========================================================================

    def get_watched_movies(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get watched movies for a user.

        Results are cached after the first call to avoid redundant API requests.

        Args:
            username: Trakt username (uses authenticated user if None)

        Returns:
            List of watched movies with play counts and last watched date
        """
        # Return cached result if available
        if self._watched_movies_cache is not None:
            return self._watched_movies_cache

        if username:
            endpoint = f"/users/{username}/watched/movies"
            authenticated = False
        else:
            endpoint = "/sync/watched/movies"
            authenticated = True

        result = self._make_request(endpoint, authenticated=authenticated)
        # Cache the result
        self._watched_movies_cache = result
        return result

    def get_watched_shows(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get watched TV shows for a user.

        Results are cached after the first call to avoid redundant API requests.

        Args:
            username: Trakt username (uses authenticated user if None)

        Returns:
            List of watched shows with episode details
        """
        # Return cached result if available
        if self._watched_shows_cache is not None:
            return self._watched_shows_cache

        if username:
            endpoint = f"/users/{username}/watched/shows"
            authenticated = False
        else:
            endpoint = "/sync/watched/shows"
            authenticated = True

        result = self._make_request(endpoint, authenticated=authenticated)
        # Cache the result
        self._watched_shows_cache = result
        return result

    def get_history(
        self,
        media_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get watch history for authenticated user.

        Args:
            media_type: Filter by 'movies' or 'shows' (None for all)
            limit: Number of results to return

        Returns:
            List of recently watched items
        """
        endpoint = "/sync/history"
        if media_type:
            endpoint += f"/{media_type}"

        params = {"limit": limit}
        return self._make_request(endpoint, authenticated=True, params=params)

    def is_movie_watched(self, title: str, year: Optional[int] = None) -> bool:
        """
        Check if a movie has been watched.

        Args:
            title: Movie title
            year: Release year (for better matching)

        Returns:
            True if watched, False otherwise
        """
        try:
            watched = self.get_watched_movies()
            for item in watched:
                movie = item.get("movie", {})
                if movie.get("title", "").lower() == title.lower():
                    if year is None or movie.get("year") == year:
                        return item.get("plays", 0) > 0
            return False
        except Exception as e:
            logger.debug(f"Error checking if movie watched on Trakt: {e}")
            return False

    def is_show_watched(self, title: str) -> bool:
        """
        Check if all aired episodes of a show have been watched.

        Args:
            title: Show title

        Returns:
            True if fully watched, False otherwise
        """
        try:
            watched = self.get_watched_shows()
            for item in watched:
                show = item.get("show", {})
                if show.get("title", "").lower() == title.lower():
                    # Consider watched if show appears in watched list
                    # (Trakt tracks individual episodes)
                    return True
            return False
        except Exception as e:
            logger.debug(f"Error checking if show watched on Trakt: {e}")
            return False

    # =========================================================================
    # Recommendations
    # =========================================================================

    def get_recommended_movies(
        self,
        limit: int = 10,
        ignore_collected: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get personalized movie recommendations.

        Args:
            limit: Number of recommendations
            ignore_collected: Hide movies already in collection

        Returns:
            List of recommended movies
        """
        endpoint = "/recommendations/movies"
        params = {
            "limit": limit,
            "ignore_collected": "true" if ignore_collected else "false",
        }
        return self._make_request(endpoint, authenticated=True, params=params)

    def get_recommended_shows(
        self,
        limit: int = 10,
        ignore_collected: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Get personalized TV show recommendations.

        Args:
            limit: Number of recommendations
            ignore_collected: Hide shows already in collection

        Returns:
            List of recommended shows
        """
        endpoint = "/recommendations/shows"
        params = {
            "limit": limit,
            "ignore_collected": "true" if ignore_collected else "false",
        }
        return self._make_request(endpoint, authenticated=True, params=params)

    # =========================================================================
    # Trending & Popular
    # =========================================================================

    def get_trending_movies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending movies.

        Args:
            limit: Number of results

        Returns:
            List of trending movies with watcher counts
        """
        endpoint = "/movies/trending"
        params = {"limit": limit}
        return self._make_request(endpoint, params=params)

    def get_trending_shows(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get trending TV shows.

        Args:
            limit: Number of results

        Returns:
            List of trending shows with watcher counts
        """
        endpoint = "/shows/trending"
        params = {"limit": limit}
        return self._make_request(endpoint, params=params)

    def get_popular_movies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular movies.

        Args:
            limit: Number of results

        Returns:
            List of popular movies
        """
        endpoint = "/movies/popular"
        params = {"limit": limit}
        return self._make_request(endpoint, params=params)

    def get_popular_shows(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get popular TV shows.

        Args:
            limit: Number of results

        Returns:
            List of popular shows
        """
        endpoint = "/shows/popular"
        params = {"limit": limit}
        return self._make_request(endpoint, params=params)

    # =========================================================================
    # User Lists & Collections
    # =========================================================================

    def get_user_lists(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get user's custom lists.

        Args:
            username: Trakt username (uses authenticated user if None)

        Returns:
            List of custom lists
        """
        if username:
            endpoint = f"/users/{username}/lists"
            authenticated = False
        else:
            endpoint = "/users/me/lists"
            authenticated = True

        return self._make_request(endpoint, authenticated=authenticated)

    def get_list_items(
        self,
        username: str,
        list_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get items in a custom list.

        Args:
            username: List owner's username
            list_id: List ID or slug

        Returns:
            List of items (movies/shows)
        """
        endpoint = f"/users/{username}/lists/{list_id}/items"
        return self._make_request(endpoint)

    def get_watchlist_movies(self) -> List[Dict[str, Any]]:
        """
        Get movies from authenticated user's watchlist.

        Returns:
            List of watchlisted movies
        """
        endpoint = "/sync/watchlist/movies"
        return self._make_request(endpoint, authenticated=True)

    def get_watchlist_shows(self) -> List[Dict[str, Any]]:
        """
        Get shows from authenticated user's watchlist.

        Returns:
            List of watchlisted shows
        """
        endpoint = "/sync/watchlist/shows"
        return self._make_request(endpoint, authenticated=True)

    # =========================================================================
    # Ratings
    # =========================================================================

    def get_user_ratings(
        self,
        media_type: Optional[str] = None,
        rating: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get user's ratings.

        Args:
            media_type: Filter by 'movies', 'shows', or 'episodes'
            rating: Filter by specific rating (1-10)

        Returns:
            List of rated items
        """
        endpoint = "/sync/ratings"
        if media_type:
            endpoint += f"/{media_type}"
        if rating:
            endpoint += f"/{rating}"

        return self._make_request(endpoint, authenticated=True)

    # =========================================================================
    # Search
    # =========================================================================

    def search(
        self,
        query: str,
        search_type: str = "movie,show",
        extended: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Search for movies and shows.

        Args:
            query: Search query
            search_type: Comma-separated types ('movie', 'show', 'episode', 'person')
            extended: Include extended info

        Returns:
            List of search results
        """
        endpoint = "/search/" + search_type
        params = {
            "query": query,
            "extended": "full" if extended else "min",
        }
        return self._make_request(endpoint, params=params)

    # =========================================================================
    # Stats
    # =========================================================================

    def get_user_stats(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get user statistics.

        Args:
            username: Trakt username (uses authenticated user if None)

        Returns:
            Dictionary with stats (movies watched, shows watched, etc.)
        """
        if username:
            endpoint = f"/users/{username}/stats"
            authenticated = False
        else:
            endpoint = "/users/me/stats"
            authenticated = True

        return self._make_request(endpoint, authenticated=authenticated)
