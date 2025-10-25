"""Service for interacting with Sonarr API."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging
import requests

from radarr_sonarr_mcp.config import SonarrConfig

logger = logging.getLogger(__name__)


@dataclass
class Statistics:
    """Statistics for a TV series."""
    episode_file_count: int
    episode_count: int
    total_episode_count: int
    size_on_disk: int
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Statistics':
        """Create a Statistics object from a dictionary."""
        return cls(
            episode_file_count=data.get('episodeFileCount', 0),
            episode_count=data.get('episodeCount', 0),
            total_episode_count=data.get('totalEpisodeCount', 0),
            size_on_disk=data.get('sizeOnDisk', 0)
        )


@dataclass
class Series:
    """TV Series data class."""
    id: int
    title: str
    year: Optional[int]
    overview: str
    status: str
    network: str
    tags: List[int]
    genres: List[str]
    statistics: Optional[Statistics]
    data: Dict[str, Any]  # Store original data for reference
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Series':
        """Create a Series object from a dictionary."""
        statistics = None
        if 'statistics' in data:
            statistics = Statistics.from_dict(data['statistics'])
        
        return cls(
            id=data['id'],
            title=data['title'],
            year=data.get('year'),
            overview=data.get('overview', ''),
            status=data.get('status', ''),
            network=data.get('network', ''),
            tags=data.get('tags', []),
            genres=data.get('genres', []),
            statistics=statistics,
            data=data
        )


@dataclass
class Episode:
    """TV Episode data class."""
    id: int
    series_id: int
    episode_file_id: Optional[int]
    season_number: int
    episode_number: int
    title: str
    air_date: Optional[str]
    has_file: bool
    monitored: bool
    overview: str
    data: Dict[str, Any]  # Store original data for reference
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Episode':
        """Create an Episode object from a dictionary."""
        return cls(
            id=data['id'],
            series_id=data['seriesId'],
            episode_file_id=data.get('episodeFileId'),
            season_number=data['seasonNumber'],
            episode_number=data['episodeNumber'],
            title=data.get('title', ''),
            air_date=data.get('airDate'),
            has_file=data.get('hasFile', False),
            monitored=data.get('monitored', True),
            overview=data.get('overview', ''),
            data=data
        )


class SonarrService:
    """Service for interacting with Sonarr API."""
    
    def __init__(self, config: SonarrConfig):
        """Initialize the Sonarr service with configuration."""
        self.config = config
    
    def get_all_series(self) -> List[Series]:
        """Fetch all TV series from Sonarr."""
        try:
            response = requests.get(
                f"{self.config.base_url}/series",
                params={"apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()
            
            series_list = []
            for series_data in response.json():
                series_list.append(Series.from_dict(series_data))
            
            return series_list
        except requests.RequestException as e:
            import logging
            logging.error(f"Error fetching series from Sonarr: {e}")
            raise Exception(f"Failed to fetch series from Sonarr: {e}")
    
    def get_series(self, series_id: int) -> Series:
        """
        Fetch a single TV series by ID from Sonarr.

        Args:
            series_id: The Sonarr series ID

        Returns:
            Series object

        Raises:
            Exception: If series not found or API error
        """
        try:
            response = requests.get(
                f"{self.config.base_url}/series/{series_id}",
                params={"apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()
            return Series.from_dict(response.json())
        except requests.RequestException as e:
            import logging
            logging.error(f"Error fetching series ID {series_id} from Sonarr: {e}")
            raise Exception(f"Failed to fetch series from Sonarr: {e}")

    def lookup_series(self, term: str) -> List[Series]:
        """Look up TV series by search term."""
        try:
            response = requests.get(
                f"{self.config.base_url}/series/lookup",
                params={"term": term, "apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()
            
            series_list = []
            for series_data in response.json():
                series_list.append(Series.from_dict(series_data))
            
            return series_list
        except requests.RequestException as e:
            import logging
            logging.error(f"Error looking up series in Sonarr: {e}")
            raise Exception(f"Failed to lookup series from Sonarr: {e}")
    
    def get_episodes(self, series_id: int) -> List[Episode]:
        """Fetch episodes for a TV series."""
        try:
            response = requests.get(
                f"{self.config.base_url}/episode",
                params={"seriesId": series_id, "apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()
            
            episodes = []
            for episode_data in response.json():
                episodes.append(Episode.from_dict(episode_data))
            
            return episodes
        except requests.RequestException as e:
            import logging
            logging.error(f"Error fetching episodes for series ID {series_id}: {e}")
            raise Exception(f"Failed to fetch episodes: {e}")

    def is_series_watched(self, series: Series) -> bool:
        """Check if a series is watched based on tags."""
        # This is an assumption - actual implementation may vary based on how
        # watched status is tracked in your Sonarr setup
        if not series.statistics:
            return False
        
        # Consider series watched if all episodes are downloaded
        return (series.statistics.episode_file_count >= 
                series.statistics.episode_count)

    def is_series_in_watchlist(self, series: Series) -> bool:
        """Check if a series is in the watchlist based on tags."""
        # This is an assumption - implementation may vary
        # Assuming 'watchlist' tag with ID 1 (adjust as needed)
        return 1 in (series.tags or [])
