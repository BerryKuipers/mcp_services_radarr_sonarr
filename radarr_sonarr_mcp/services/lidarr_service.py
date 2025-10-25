"""Service for interacting with Lidarr API."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import logging
import requests

from radarr_sonarr_mcp.config import LidarrConfig

logger = logging.getLogger(__name__)


@dataclass
class AlbumStatistics:
    """Statistics for an album."""
    track_file_count: int
    track_count: int
    total_track_count: int
    size_on_disk: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AlbumStatistics':
        """Create an AlbumStatistics object from a dictionary."""
        return cls(
            track_file_count=data.get('trackFileCount', 0),
            track_count=data.get('trackCount', 0),
            total_track_count=data.get('totalTrackCount', 0),
            size_on_disk=data.get('sizeOnDisk', 0)
        )


@dataclass
class Album:
    """Album data class."""
    id: int
    title: str
    artist_name: str
    release_date: Optional[str]
    monitored: bool
    artist_id: int
    genres: List[str]
    statistics: Optional[AlbumStatistics]
    data: Dict[str, Any]  # Store original data for reference

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Album':
        """Create an Album object from a dictionary."""
        statistics = None
        if 'statistics' in data:
            statistics = AlbumStatistics.from_dict(data['statistics'])

        # Get artist name from the artist object if available
        artist_name = ""
        if 'artist' in data and isinstance(data['artist'], dict):
            artist_name = data['artist'].get('artistName', '')

        return cls(
            id=data['id'],
            title=data.get('title', ''),
            artist_name=artist_name,
            release_date=data.get('releaseDate'),
            monitored=data.get('monitored', False),
            artist_id=data.get('artistId', 0),
            genres=data.get('genres', []),
            statistics=statistics,
            data=data
        )

    @property
    def has_file(self) -> bool:
        """Check if album has files."""
        if self.statistics:
            return self.statistics.track_file_count > 0
        return False


@dataclass
class ArtistStatistics:
    """Statistics for an artist."""
    album_count: int
    track_file_count: int
    track_count: int
    total_track_count: int
    size_on_disk: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArtistStatistics':
        """Create an ArtistStatistics object from a dictionary."""
        return cls(
            album_count=data.get('albumCount', 0),
            track_file_count=data.get('trackFileCount', 0),
            track_count=data.get('trackCount', 0),
            total_track_count=data.get('totalTrackCount', 0),
            size_on_disk=data.get('sizeOnDisk', 0)
        )


@dataclass
class Artist:
    """Artist data class."""
    id: int
    name: str
    monitored: bool
    genres: List[str]
    statistics: Optional[ArtistStatistics]
    data: Dict[str, Any]  # Store original data for reference

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Artist':
        """Create an Artist object from a dictionary."""
        statistics = None
        if 'statistics' in data:
            statistics = ArtistStatistics.from_dict(data['statistics'])

        return cls(
            id=data['id'],
            name=data.get('artistName', ''),
            monitored=data.get('monitored', False),
            genres=data.get('genres', []),
            statistics=statistics,
            data=data
        )


class LidarrService:
    """Service for interacting with Lidarr API."""

    def __init__(self, config: LidarrConfig):
        """Initialize the Lidarr service with configuration."""
        self.config = config

    def get_all_artists(self) -> List[Artist]:
        """Fetch all artists from Lidarr."""
        try:
            response = requests.get(
                f"{self.config.base_url}/artist",
                params={"apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()

            artists = []
            for artist_data in response.json():
                artists.append(Artist.from_dict(artist_data))

            return artists
        except requests.RequestException as e:
            logger.error(f"Error fetching artists from Lidarr: {e}")
            raise Exception(f"Failed to fetch artists from Lidarr: {e}")

    def get_artist(self, artist_id: int) -> Artist:
        """
        Fetch a single artist by ID from Lidarr.

        Args:
            artist_id: The Lidarr artist ID

        Returns:
            Artist object

        Raises:
            Exception: If artist not found or API error
        """
        try:
            response = requests.get(
                f"{self.config.base_url}/artist/{artist_id}",
                params={"apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()
            return Artist.from_dict(response.json())
        except requests.RequestException as e:
            logger.error(f"Error fetching artist ID {artist_id} from Lidarr: {e}")
            raise Exception(f"Failed to fetch artist from Lidarr: {e}")

    def get_all_albums(self) -> List[Album]:
        """Fetch all albums from Lidarr."""
        try:
            response = requests.get(
                f"{self.config.base_url}/album",
                params={"apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()

            albums = []
            for album_data in response.json():
                albums.append(Album.from_dict(album_data))

            return albums
        except requests.RequestException as e:
            logger.error(f"Error fetching albums from Lidarr: {e}")
            raise Exception(f"Failed to fetch albums from Lidarr: {e}")

    def get_album(self, album_id: int) -> Album:
        """
        Fetch a single album by ID from Lidarr.

        Args:
            album_id: The Lidarr album ID

        Returns:
            Album object

        Raises:
            Exception: If album not found or API error
        """
        try:
            response = requests.get(
                f"{self.config.base_url}/album/{album_id}",
                params={"apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()
            return Album.from_dict(response.json())
        except requests.RequestException as e:
            logger.error(f"Error fetching album ID {album_id} from Lidarr: {e}")
            raise Exception(f"Failed to fetch album from Lidarr: {e}")

    def lookup_artist(self, term: str) -> List[Artist]:
        """Look up artists by search term."""
        try:
            response = requests.get(
                f"{self.config.base_url}/artist/lookup",
                params={"term": term, "apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()

            artists = []
            for artist_data in response.json():
                artists.append(Artist.from_dict(artist_data))

            return artists
        except requests.RequestException as e:
            logger.error(f"Error looking up artists in Lidarr: {e}")
            raise Exception(f"Failed to lookup artists from Lidarr: {e}")

    def lookup_album(self, term: str) -> List[Album]:
        """Look up albums by search term."""
        try:
            response = requests.get(
                f"{self.config.base_url}/album/lookup",
                params={"term": term, "apikey": self.config.api_key},
                timeout=30
            )
            response.raise_for_status()

            albums = []
            for album_data in response.json():
                albums.append(Album.from_dict(album_data))

            return albums
        except requests.RequestException as e:
            logger.error(f"Error looking up albums in Lidarr: {e}")
            raise Exception(f"Failed to lookup albums from Lidarr: {e}")

    def get_calendar(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Album]:
        """
        Fetch upcoming album releases from Lidarr calendar.

        Args:
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)

        Returns:
            List of upcoming albums
        """
        try:
            params = {"apikey": self.config.api_key}
            if start_date:
                params["start"] = start_date
            if end_date:
                params["end"] = end_date

            response = requests.get(
                f"{self.config.base_url}/calendar",
                params=params,
                timeout=30
            )
            response.raise_for_status()

            albums = []
            for album_data in response.json():
                albums.append(Album.from_dict(album_data))

            return albums
        except requests.RequestException as e:
            logger.error(f"Error fetching calendar from Lidarr: {e}")
            raise Exception(f"Failed to fetch calendar from Lidarr: {e}")

    def get_wanted_missing(self) -> List[Album]:
        """
        Fetch wanted/missing albums from Lidarr with pagination support.

        Fetches all pages to ensure no missing albums are excluded.

        Returns:
            List of all missing albums
        """
        try:
            albums = []
            page = 1
            page_size = 100
            total_records = None

            while True:
                response = requests.get(
                    f"{self.config.base_url}/wanted/missing",
                    params={
                        "apikey": self.config.api_key,
                        "page": page,
                        "pageSize": page_size
                    },
                    timeout=30
                )
                response.raise_for_status()

                data = response.json()
                records = data.get('records', [])

                # Add albums from this page
                for album_data in records:
                    albums.append(Album.from_dict(album_data))

                # Get total records from first page
                if total_records is None:
                    total_records = data.get('totalRecords', 0)

                # Check if we've fetched all records
                if len(albums) >= total_records or len(records) < page_size:
                    break

                page += 1

            logger.info(f"Fetched {len(albums)} missing albums from Lidarr across {page} page(s)")
            return albums
        except requests.RequestException as e:
            logger.error(f"Error fetching missing albums from Lidarr: {e}")
            raise Exception(f"Failed to fetch missing albums from Lidarr: {e}")
