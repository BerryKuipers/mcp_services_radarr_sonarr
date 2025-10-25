#!/usr/bin/env python
"""Main MCP server implementation for Radarr/Sonarr with FastMCP 2.0+."""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastmcp import FastMCP
from pydantic import Field

from radarr_sonarr_mcp.config import (
    RadarrConfig,
    SonarrConfig,
    JellyfinConfig,
    PlexConfig,
    ServerConfig,
)
from radarr_sonarr_mcp.services.radarr_service import RadarrService
from radarr_sonarr_mcp.services.sonarr_service import SonarrService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Configuration Loading
# =============================================================================

def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables or config file.

    Returns:
        Dictionary containing all configuration settings.
    """
    if os.environ.get('RADARR_API_KEY') or os.environ.get('SONARR_API_KEY'):
        logger.info("Loading configuration from environment variables")
        nas_ip = os.environ.get('NAS_IP', '10.0.0.23')
        return {
            "nasConfig": {
                "ip": nas_ip,
            },
            "radarrConfig": {
                "apiKey": os.environ.get('RADARR_API_KEY', ''),
                "basePath": os.environ.get('RADARR_BASE_PATH', '/api/v3'),
                "port": os.environ.get('RADARR_PORT', '7878'),
                "nasIp": nas_ip,
            },
            "sonarrConfig": {
                "apiKey": os.environ.get('SONARR_API_KEY', ''),
                "basePath": os.environ.get('SONARR_BASE_PATH', '/api/v3'),
                "port": os.environ.get('SONARR_PORT', '8989'),
                "nasIp": nas_ip,
            },
            "jellyfinConfig": {
                "baseUrl": os.environ.get('JELLYFIN_BASE_URL', ''),
                "apiKey": os.environ.get('JELLYFIN_API_KEY', ''),
                "userId": os.environ.get('JELLYFIN_USER_ID', ''),
            },
            "plexConfig": {
                "baseUrl": os.environ.get('PLEX_BASE_URL', ''),
                "token": os.environ.get('PLEX_TOKEN', ''),
            },
            "traktConfig": {
                "clientId": os.environ.get('TRAKT_CLIENT_ID', ''),
                "accessToken": os.environ.get('TRAKT_ACCESS_TOKEN', ''),
                "clientSecret": os.environ.get('TRAKT_CLIENT_SECRET', ''),
            },
            "server": {
                "port": int(os.environ.get('MCP_SERVER_PORT', '3000'))
            }
        }

    # Try loading from config file
    config_path = Path('config.json')
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                logger.info(f"Loading configuration from {config_path}")
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")

    # Return default configuration
    logger.warning("Using default configuration")
    return {
        "nasConfig": {"ip": "10.0.0.23"},
        "radarrConfig": {
            "apiKey": "",
            "basePath": "/api/v3",
            "port": "7878",
            "nasIp": "10.0.0.23",
        },
        "sonarrConfig": {
            "apiKey": "",
            "basePath": "/api/v3",
            "port": "8989",
            "nasIp": "10.0.0.23",
        },
        "jellyfinConfig": {"baseUrl": "", "apiKey": "", "userId": ""},
        "plexConfig": {"baseUrl": "", "token": ""},
        "traktConfig": {"clientId": "", "accessToken": "", "clientSecret": ""},
        "server": {"port": 3000}
    }


# =============================================================================
# Helper Functions
# =============================================================================

def is_watched_series(title: str, config: Dict[str, Any], sonarr_service: SonarrService) -> bool:
    """
    Check if a series is watched using available media services.

    Checks Trakt, Jellyfin, and Plex in order of priority.

    Args:
        title: Series title to check
        config: Configuration dictionary
        sonarr_service: SonarrService instance

    Returns:
        True if series is watched, False otherwise
    """
    statuses = []

    # Check Trakt first (most reliable for watch status)
    trakt_cfg = config.get("traktConfig", {})
    if trakt_cfg.get("clientId"):
        try:
            from radarr_sonarr_mcp.services.trakt_service import TraktService
            trakt = TraktService(trakt_cfg)
            statuses.append(trakt.is_show_watched(title))
        except Exception as e:
            logger.debug(f"Trakt check failed for '{title}': {e}")

    # Check Jellyfin
    jellyfin_cfg = config.get("jellyfinConfig", {})
    if jellyfin_cfg.get("baseUrl"):
        try:
            from radarr_sonarr_mcp.services.jellyfin_service import JellyfinService
            jellyfin = JellyfinService(jellyfin_cfg)
            statuses.append(jellyfin.is_series_watched(title))
        except Exception as e:
            logger.debug(f"Jellyfin check failed for '{title}': {e}")

    # Check Plex
    plex_cfg = config.get("plexConfig", {})
    if plex_cfg.get("baseUrl"):
        try:
            from radarr_sonarr_mcp.services.plex_service import PlexService
            plex = PlexService(plex_cfg)
            statuses.append(plex.is_series_watched(title))
        except Exception as e:
            logger.debug(f"Plex check failed for '{title}': {e}")

    # Return True if any service reports watched
    if statuses:
        return any(statuses)

    # Fallback to Sonarr's own logic
    return False


def is_watched_movie(title: str, config: Dict[str, Any], year: Optional[int] = None) -> bool:
    """
    Check if a movie is watched using available media services.

    Checks Trakt, Jellyfin, and Plex in order of priority.

    Args:
        title: Movie title to check
        config: Configuration dictionary
        year: Movie release year (for better Trakt matching)

    Returns:
        True if movie is watched, False otherwise
    """
    statuses = []

    # Check Trakt first (most reliable for watch status)
    trakt_cfg = config.get("traktConfig", {})
    if trakt_cfg.get("clientId"):
        try:
            from radarr_sonarr_mcp.services.trakt_service import TraktService
            trakt = TraktService(trakt_cfg)
            statuses.append(trakt.is_movie_watched(title, year))
        except Exception as e:
            logger.debug(f"Trakt movie check failed for '{title}': {e}")

    # Check Jellyfin
    jellyfin_cfg = config.get("jellyfinConfig", {})
    if jellyfin_cfg.get("baseUrl"):
        try:
            from radarr_sonarr_mcp.services.jellyfin_service import JellyfinService
            jellyfin = JellyfinService(jellyfin_cfg)
            statuses.append(jellyfin.is_movie_watched(title))
        except Exception as e:
            logger.debug(f"Jellyfin movie check failed for '{title}': {e}")

    # Check Plex
    plex_cfg = config.get("plexConfig", {})
    if plex_cfg.get("baseUrl"):
        try:
            from radarr_sonarr_mcp.services.plex_service import PlexService
            plex = PlexService(plex_cfg)
            statuses.append(plex.is_movie_watched(title))
        except Exception as e:
            logger.debug(f"Plex movie check failed for '{title}': {e}")

    return any(statuses)


# =============================================================================
# MCP Server Implementation
# =============================================================================

# Initialize FastMCP server
mcp = FastMCP(
    "radarr-sonarr-mcp",
    dependencies=["fastmcp>=2.0.0", "requests>=2.28.0", "pydantic>=2.0.0"]
)

# Load configuration
config = load_config()

# Initialize services
radarr_config = RadarrConfig(
    api_key=config["radarrConfig"]["apiKey"],
    base_path=config["radarrConfig"]["basePath"],
    port=config["radarrConfig"]["port"],
    nas_ip=config["radarrConfig"].get("nasIp", config["nasConfig"]["ip"]),
)

sonarr_config = SonarrConfig(
    api_key=config["sonarrConfig"]["apiKey"],
    base_path=config["sonarrConfig"]["basePath"],
    port=config["sonarrConfig"]["port"],
    nas_ip=config["sonarrConfig"].get("nasIp", config["nasConfig"]["ip"]),
)

radarr_service = RadarrService(radarr_config)
sonarr_service = SonarrService(sonarr_config)


# =============================================================================
# Tools - Movies
# =============================================================================

@mcp.tool()
def get_available_movies(
    year: Optional[int] = Field(None, description="Filter by release year"),
    downloaded: Optional[bool] = Field(None, description="Filter by download status"),
    watched: Optional[bool] = Field(None, description="Filter by watched status"),
    actors: Optional[str] = Field(None, description="Filter by actor/actress name"),
    limit: int = Field(100, description="Maximum number of results to return", ge=1, le=1000),
) -> Dict[str, Any]:
    """
    Get a list of available movies from Radarr with optional filters.

    This tool retrieves your movie collection from Radarr and supports filtering by:
    - Release year
    - Download status (whether the movie file exists)
    - Watched status (checked via Plex/Jellyfin)
    - Cast members (actors/actresses)

    Example queries:
    - "Show me sci-fi movies from 2023"
    - "What movies with Tom Hanks haven't I watched?"
    - "List all downloaded movies from the 1990s"

    Returns:
        Dictionary containing count and list of movies with details
    """
    try:
        all_movies = radarr_service.get_all_movies()
        filtered_movies = all_movies

        # Apply filters
        if year is not None:
            filtered_movies = [m for m in filtered_movies if m.year == year]

        if downloaded is not None:
            filtered_movies = [m for m in filtered_movies if m.has_file == downloaded]

        if watched is not None:
            if watched:
                filtered_movies = [
                    m for m in filtered_movies
                    if is_watched_movie(m.title, config, m.year)
                ]
            else:
                filtered_movies = [
                    m for m in filtered_movies
                    if not is_watched_movie(m.title, config, m.year)
                ]

        if actors:
            filtered_movies = [
                m for m in filtered_movies
                if m.data.get("credits") and any(
                    actors.lower() in cast.get("name", "").lower()
                    for cast in m.data.get("credits", {}).get("cast", [])
                )
            ]

        # Apply limit
        filtered_movies = filtered_movies[:limit]

        return {
            "count": len(filtered_movies),
            "movies": [
                {
                    "id": m.id,
                    "title": m.title,
                    "year": m.year,
                    "overview": m.overview,
                    "hasFile": m.has_file,
                    "status": m.status,
                    "genres": m.genres or [],
                    "watched": is_watched_movie(m.title, config, m.year),
                }
                for m in filtered_movies
            ]
        }
    except Exception as e:
        logger.error(f"Error getting movies: {e}")
        return {"error": str(e), "count": 0, "movies": []}


@mcp.tool()
def lookup_movie(term: str) -> Dict[str, Any]:
    """
    Search for movies by title using Radarr's lookup feature.

    This tool searches for movies that match the search term, including
    movies that may not be in your collection yet. Useful for finding
    movies to add to your library.

    Args:
        term: Movie title or search term

    Returns:
        Dictionary containing search results with movie details
    """
    try:
        results = radarr_service.lookup_movie(term)
        return {
            "count": len(results),
            "movies": [
                {
                    "id": m.id,
                    "title": m.title,
                    "year": m.year,
                    "overview": m.overview,
                    "hasFile": m.has_file,
                    "status": m.status,
                }
                for m in results
            ]
        }
    except Exception as e:
        logger.error(f"Error looking up movie '{term}': {e}")
        return {"error": str(e), "count": 0, "movies": []}


@mcp.tool()
def get_movie_details(movie_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific movie.

    Args:
        movie_id: The Radarr ID of the movie

    Returns:
        Dictionary containing detailed movie information
    """
    try:
        all_movies = radarr_service.get_all_movies()
        movie = next((m for m in all_movies if m.id == movie_id), None)

        if not movie:
            return {"error": f"Movie with ID {movie_id} not found"}

        return {
            "id": movie.id,
            "title": movie.title,
            "year": movie.year,
            "overview": movie.overview,
            "hasFile": movie.has_file,
            "status": movie.status,
            "genres": movie.genres or [],
            "tags": movie.tags or [],
            "watched": is_watched_movie(movie.title, config),
            "data": movie.data,
        }
    except Exception as e:
        logger.error(f"Error getting movie details for ID {movie_id}: {e}")
        return {"error": str(e)}


# =============================================================================
# Tools - TV Series
# =============================================================================

@mcp.tool()
def get_available_series(
    year: Optional[int] = Field(None, description="Filter by release year"),
    downloaded: Optional[bool] = Field(None, description="Filter by download status"),
    watched: Optional[bool] = Field(None, description="Filter by watched status"),
    actors: Optional[str] = Field(None, description="Filter by actor name"),
    limit: int = Field(100, description="Maximum number of results to return", ge=1, le=1000),
) -> Dict[str, Any]:
    """
    Get a list of available TV series from Sonarr with optional filters.

    This tool retrieves your TV series collection from Sonarr and supports filtering by:
    - Release year
    - Download status (whether episodes are downloaded)
    - Watched status (checked via Plex/Jellyfin)
    - Cast members

    Example queries:
    - "Show me TV series from 2022"
    - "What shows with Pedro Pascal haven't I watched?"
    - "List all series with downloaded episodes"

    Returns:
        Dictionary containing count and list of series with details
    """
    try:
        all_series = sonarr_service.get_all_series()
        filtered_series = all_series

        # Apply filters
        if year is not None:
            filtered_series = [s for s in filtered_series if s.year == year]

        if downloaded is not None:
            filtered_series = [
                s for s in filtered_series
                if (s.statistics and s.statistics.episode_file_count > 0) == downloaded
            ]

        if watched is not None:
            if watched:
                filtered_series = [
                    s for s in filtered_series
                    if is_watched_series(s.title, config, sonarr_service)
                ]
            else:
                filtered_series = [
                    s for s in filtered_series
                    if not is_watched_series(s.title, config, sonarr_service)
                ]

        if actors:
            filtered_series = [
                s for s in filtered_series
                if s.data.get("credits") and any(
                    actors.lower() in cast.get("name", "").lower()
                    for cast in s.data.get("credits", {}).get("cast", [])
                )
            ]

        # Apply limit
        filtered_series = filtered_series[:limit]

        return {
            "count": len(filtered_series),
            "series": [
                {
                    "id": s.id,
                    "title": s.title,
                    "year": s.year,
                    "overview": s.overview,
                    "status": s.status,
                    "network": s.network,
                    "genres": s.genres or [],
                    "watched": is_watched_series(s.title, config, sonarr_service),
                    "episodeCount": s.statistics.episode_count if s.statistics else 0,
                    "downloadedEpisodes": s.statistics.episode_file_count if s.statistics else 0,
                }
                for s in filtered_series
            ]
        }
    except Exception as e:
        logger.error(f"Error getting series: {e}")
        return {"error": str(e), "count": 0, "series": []}


@mcp.tool()
def lookup_series(term: str) -> Dict[str, Any]:
    """
    Search for TV series by title using Sonarr's lookup feature.

    This tool searches for TV series that match the search term, including
    series that may not be in your collection yet. Useful for finding
    shows to add to your library.

    Args:
        term: Series title or search term

    Returns:
        Dictionary containing search results with series details
    """
    try:
        results = sonarr_service.lookup_series(term)
        return {
            "count": len(results),
            "series": [
                {
                    "id": s.id,
                    "title": s.title,
                    "year": s.year,
                    "overview": s.overview,
                    "status": s.status,
                    "network": s.network,
                }
                for s in results
            ]
        }
    except Exception as e:
        logger.error(f"Error looking up series '{term}': {e}")
        return {"error": str(e), "count": 0, "series": []}


@mcp.tool()
def get_series_details(series_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific TV series.

    Args:
        series_id: The Sonarr ID of the series

    Returns:
        Dictionary containing detailed series information
    """
    try:
        all_series = sonarr_service.get_all_series()
        series = next((s for s in all_series if s.id == series_id), None)

        if not series:
            return {"error": f"Series with ID {series_id} not found"}

        return {
            "id": series.id,
            "title": series.title,
            "year": series.year,
            "overview": series.overview,
            "status": series.status,
            "network": series.network,
            "genres": series.genres or [],
            "tags": series.tags or [],
            "watched": is_watched_series(series.title, config, sonarr_service),
            "statistics": {
                "episodeCount": series.statistics.episode_count if series.statistics else 0,
                "episodeFileCount": series.statistics.episode_file_count if series.statistics else 0,
                "totalEpisodeCount": series.statistics.total_episode_count if series.statistics else 0,
                "sizeOnDisk": series.statistics.size_on_disk if series.statistics else 0,
            } if series.statistics else {},
            "data": series.data,
        }
    except Exception as e:
        logger.error(f"Error getting series details for ID {series_id}: {e}")
        return {"error": str(e)}


@mcp.tool()
def get_series_episodes(
    series_id: int,
    season_number: Optional[int] = Field(None, description="Filter by season number"),
) -> Dict[str, Any]:
    """
    Get episodes for a specific TV series.

    Args:
        series_id: The Sonarr ID of the series
        season_number: Optional season number to filter episodes

    Returns:
        Dictionary containing episode information
    """
    try:
        episodes = sonarr_service.get_episodes(series_id)

        if season_number is not None:
            episodes = [e for e in episodes if e.season_number == season_number]

        return {
            "count": len(episodes),
            "episodes": [
                {
                    "id": e.id,
                    "seriesId": e.series_id,
                    "seasonNumber": e.season_number,
                    "episodeNumber": e.episode_number,
                    "title": e.title,
                    "airDate": e.air_date,
                    "hasFile": e.has_file,
                    "monitored": e.monitored,
                    "overview": e.overview,
                }
                for e in episodes
            ]
        }
    except Exception as e:
        logger.error(f"Error getting episodes for series ID {series_id}: {e}")
        return {"error": str(e), "count": 0, "episodes": []}


# =============================================================================
# Resources
# =============================================================================

@mcp.resource("radarr://movies")
def movies_resource() -> str:
    """
    Browse all available movies from Radarr.

    Returns a formatted list of all movies in your collection.
    """
    try:
        movies = radarr_service.get_all_movies()
        output = f"# Movies Collection ({len(movies)} total)\n\n"

        for movie in movies[:100]:  # Limit to first 100 for resource
            output += f"## {movie.title} ({movie.year})\n"
            output += f"- ID: {movie.id}\n"
            output += f"- Status: {movie.status}\n"
            output += f"- Downloaded: {'Yes' if movie.has_file else 'No'}\n"
            output += f"- Genres: {', '.join(movie.genres) if movie.genres else 'N/A'}\n"
            output += f"- Overview: {movie.overview[:200]}...\n\n"

        if len(movies) > 100:
            output += f"\n... and {len(movies) - 100} more movies\n"

        return output
    except Exception as e:
        logger.error(f"Error fetching movies resource: {e}")
        return f"Error: {str(e)}"


@mcp.resource("sonarr://series")
def series_resource() -> str:
    """
    Browse all available TV series from Sonarr.

    Returns a formatted list of all TV series in your collection.
    """
    try:
        series = sonarr_service.get_all_series()
        output = f"# TV Series Collection ({len(series)} total)\n\n"

        for show in series[:100]:  # Limit to first 100 for resource
            output += f"## {show.title} ({show.year or 'N/A'})\n"
            output += f"- ID: {show.id}\n"
            output += f"- Status: {show.status}\n"
            output += f"- Network: {show.network}\n"
            if show.statistics:
                output += f"- Episodes: {show.statistics.episode_file_count}/{show.statistics.episode_count}\n"
            output += f"- Genres: {', '.join(show.genres) if show.genres else 'N/A'}\n"
            output += f"- Overview: {show.overview[:200]}...\n\n"

        if len(series) > 100:
            output += f"\n... and {len(series) - 100} more series\n"

        return output
    except Exception as e:
        logger.error(f"Error fetching series resource: {e}")
        return f"Error: {str(e)}"


# =============================================================================
# Tools - Calendar & Upcoming
# =============================================================================

@mcp.tool()
def get_upcoming_movies(
    days_ahead: int = Field(30, description="Days to look ahead", ge=1, le=365),
) -> Dict[str, Any]:
    """
    Get movies releasing in the next N days (in cinemas or digital).

    Useful for planning what to watch and staying updated on new releases.

    Example queries:
    - "What movies are coming out this month?"
    - "Show me upcoming releases in the next 7 days"

    Args:
        days_ahead: Number of days to look ahead (1-365)

    Returns:
        Dictionary containing upcoming movies with release dates
    """
    try:
        import datetime

        all_movies = radarr_service.get_all_movies()
        today = datetime.datetime.now()
        end_date = today + datetime.timedelta(days=days_ahead)

        upcoming = []
        for movie in all_movies:
            # Check if movie has a release date in the data
            release_date_str = movie.data.get('inCinemas') or movie.data.get('digitalRelease')
            if release_date_str:
                try:
                    release_date = datetime.datetime.fromisoformat(release_date_str.replace('Z', '+00:00'))
                    if today <= release_date <= end_date:
                        upcoming.append({
                            "id": movie.id,
                            "title": movie.title,
                            "year": movie.year,
                            "releaseDate": release_date_str,
                            "overview": movie.overview,
                            "genres": movie.genres or [],
                            "hasFile": movie.has_file,
                        })
                except (ValueError, AttributeError):
                    pass

        # Sort by release date
        upcoming.sort(key=lambda x: x["releaseDate"])

        return {
            "count": len(upcoming),
            "daysAhead": days_ahead,
            "movies": upcoming
        }
    except Exception as e:
        logger.error(f"Error getting upcoming movies: {e}")
        return {"error": str(e), "count": 0, "movies": []}


@mcp.tool()
def get_upcoming_episodes(
    days_ahead: int = Field(7, description="Days to look ahead", ge=1, le=90),
    unmonitored: bool = Field(False, description="Include unmonitored series"),
) -> Dict[str, Any]:
    """
    Get TV episodes airing in the next N days.

    Useful for staying current with your TV shows.

    Example queries:
    - "What new episodes are coming this week?"
    - "Show me upcoming episodes for my series"

    Args:
        days_ahead: Number of days to look ahead (1-90)
        unmonitored: Whether to include unmonitored series

    Returns:
        Dictionary containing upcoming episodes with air dates
    """
    try:
        import datetime

        all_series = sonarr_service.get_all_series()
        today = datetime.datetime.now()
        end_date = today + datetime.timedelta(days=days_ahead)

        upcoming = []
        for series in all_series:
            if not unmonitored and not series.data.get('monitored', True):
                continue

            try:
                episodes = sonarr_service.get_episodes(series.id)
                for episode in episodes:
                    if episode.air_date:
                        try:
                            air_date = datetime.datetime.fromisoformat(episode.air_date)
                            if today <= air_date <= end_date:
                                upcoming.append({
                                    "seriesId": series.id,
                                    "seriesTitle": series.title,
                                    "episodeId": episode.id,
                                    "seasonNumber": episode.season_number,
                                    "episodeNumber": episode.episode_number,
                                    "title": episode.title,
                                    "airDate": episode.air_date,
                                    "hasFile": episode.has_file,
                                    "overview": episode.overview,
                                })
                        except (ValueError, AttributeError):
                            pass
            except Exception as e:
                logger.debug(f"Error getting episodes for series {series.id}: {e}")
                continue

        # Sort by air date
        upcoming.sort(key=lambda x: x["airDate"])

        return {
            "count": len(upcoming),
            "daysAhead": days_ahead,
            "episodes": upcoming
        }
    except Exception as e:
        logger.error(f"Error getting upcoming episodes: {e}")
        return {"error": str(e), "count": 0, "episodes": []}


# =============================================================================
# Tools - Missing & Wanted Content
# =============================================================================

@mcp.tool()
def get_missing_movies(
    limit: int = Field(50, description="Maximum results to return", ge=1, le=500),
) -> Dict[str, Any]:
    """
    Get movies in your library that haven't been downloaded yet.

    Shows your wishlist of wanted movies that are being monitored.

    Example queries:
    - "What movies am I missing?"
    - "Show me my wishlist that hasn't downloaded"

    Args:
        limit: Maximum number of results (1-500)

    Returns:
        Dictionary containing missing movies
    """
    try:
        all_movies = radarr_service.get_all_movies()
        missing = [
            {
                "id": m.id,
                "title": m.title,
                "year": m.year,
                "overview": m.overview,
                "status": m.status,
                "genres": m.genres or [],
            }
            for m in all_movies
            if not m.has_file and m.data.get('monitored', True)
        ][:limit]

        return {
            "count": len(missing),
            "movies": missing
        }
    except Exception as e:
        logger.error(f"Error getting missing movies: {e}")
        return {"error": str(e), "count": 0, "movies": []}


@mcp.tool()
def get_missing_episodes(
    series_id: Optional[int] = Field(None, description="Filter by specific series ID"),
    limit: int = Field(100, description="Maximum results to return", ge=1, le=1000),
) -> Dict[str, Any]:
    """
    Get episodes that haven't been downloaded yet.

    Shows episodes you're missing from monitored series.

    Example queries:
    - "What episodes am I missing?"
    - "Show missing episodes for Breaking Bad"

    Args:
        series_id: Optional series ID to filter by
        limit: Maximum number of results (1-1000)

    Returns:
        Dictionary containing missing episodes
    """
    try:
        missing = []

        if series_id:
            series_list = [s for s in sonarr_service.get_all_series() if s.id == series_id]
        else:
            series_list = sonarr_service.get_all_series()

        for series in series_list:
            if not series.data.get('monitored', True):
                continue

            try:
                episodes = sonarr_service.get_episodes(series.id)
                for episode in episodes:
                    if not episode.has_file and episode.monitored:
                        missing.append({
                            "seriesId": series.id,
                            "seriesTitle": series.title,
                            "episodeId": episode.id,
                            "seasonNumber": episode.season_number,
                            "episodeNumber": episode.episode_number,
                            "title": episode.title,
                            "airDate": episode.air_date,
                            "overview": episode.overview,
                        })

                        if len(missing) >= limit:
                            break
            except Exception as e:
                logger.debug(f"Error getting episodes for series {series.id}: {e}")
                continue

            if len(missing) >= limit:
                break

        return {
            "count": len(missing),
            "episodes": missing
        }
    except Exception as e:
        logger.error(f"Error getting missing episodes: {e}")
        return {"error": str(e), "count": 0, "episodes": []}


# =============================================================================
# Tools - Statistics & Analytics
# =============================================================================

@mcp.tool()
def get_collection_statistics() -> Dict[str, Any]:
    """
    Get comprehensive statistics about your entire media collection.

    Provides insights into your library including counts, storage, quality,
    and genre distributions.

    Example queries:
    - "Show me my collection stats"
    - "How big is my library?"

    Returns:
        Dictionary containing comprehensive collection statistics
    """
    try:
        # Get all data
        movies = radarr_service.get_all_movies()
        series = sonarr_service.get_all_series()

        # Movie statistics
        movie_count = len(movies)
        movies_downloaded = sum(1 for m in movies if m.has_file)
        movies_watched = sum(1 for m in movies if is_watched_movie(m.title, config, m.year))

        # Series statistics
        series_count = len(series)
        total_episodes = sum(s.statistics.episode_count if s.statistics else 0 for s in series)
        downloaded_episodes = sum(s.statistics.episode_file_count if s.statistics else 0 for s in series)
        total_size = sum(s.statistics.size_on_disk if s.statistics else 0 for s in series)

        # Genre distribution
        from collections import Counter
        movie_genres = Counter()
        series_genres = Counter()

        for movie in movies:
            if movie.genres:
                for genre in movie.genres:
                    movie_genres[genre] += 1

        for show in series:
            if show.genres:
                for genre in show.genres:
                    series_genres[genre] += 1

        return {
            "movies": {
                "total": movie_count,
                "downloaded": movies_downloaded,
                "missing": movie_count - movies_downloaded,
                "watched": movies_watched,
                "unwatched": movies_downloaded - movies_watched,
                "topGenres": dict(movie_genres.most_common(5)),
            },
            "series": {
                "total": series_count,
                "totalEpisodes": total_episodes,
                "downloadedEpisodes": downloaded_episodes,
                "missingEpisodes": total_episodes - downloaded_episodes,
                "storageSizeBytes": total_size,
                "storageSizeGB": round(total_size / (1024**3), 2),
                "topGenres": dict(series_genres.most_common(5)),
            },
            "overall": {
                "totalItems": movie_count + series_count,
                "totalStorageGB": round(total_size / (1024**3), 2),
            }
        }
    except Exception as e:
        logger.error(f"Error getting collection statistics: {e}")
        return {"error": str(e)}


# =============================================================================
# Tools - Trakt Integration
# =============================================================================

@mcp.tool()
def get_trakt_trending_movies(
    limit: int = Field(10, description="Number of results", ge=1, le=50),
) -> Dict[str, Any]:
    """
    Get currently trending movies from Trakt.

    Shows what movies people are watching right now worldwide.

    Example queries:
    - "What movies are trending on Trakt?"
    - "Show me popular movies people are watching"

    Args:
        limit: Number of movies to return (1-50)

    Returns:
        Dictionary containing trending movies with watcher counts
    """
    try:
        trakt_cfg = config.get("traktConfig", {})
        if not trakt_cfg.get("clientId"):
            return {"error": "Trakt not configured. Please set TRAKT_CLIENT_ID.", "movies": []}

        from radarr_sonarr_mcp.services.trakt_service import TraktService
        trakt = TraktService(trakt_cfg)
        trending = trakt.get_trending_movies(limit)

        return {
            "count": len(trending),
            "movies": [
                {
                    "title": item.get("movie", {}).get("title"),
                    "year": item.get("movie", {}).get("year"),
                    "overview": item.get("movie", {}).get("overview"),
                    "watchers": item.get("watchers", 0),
                    "rating": item.get("movie", {}).get("rating"),
                    "genres": item.get("movie", {}).get("genres", []),
                }
                for item in trending
            ]
        }
    except Exception as e:
        logger.error(f"Error getting trending movies from Trakt: {e}")
        return {"error": str(e), "count": 0, "movies": []}


@mcp.tool()
def get_trakt_trending_shows(
    limit: int = Field(10, description="Number of results", ge=1, le=50),
) -> Dict[str, Any]:
    """
    Get currently trending TV shows from Trakt.

    Shows what TV series people are watching right now worldwide.

    Example queries:
    - "What shows are trending on Trakt?"
    - "Show me popular TV series people are binge-watching"

    Args:
        limit: Number of shows to return (1-50)

    Returns:
        Dictionary containing trending shows with watcher counts
    """
    try:
        trakt_cfg = config.get("traktConfig", {})
        if not trakt_cfg.get("clientId"):
            return {"error": "Trakt not configured. Please set TRAKT_CLIENT_ID.", "shows": []}

        from radarr_sonarr_mcp.services.trakt_service import TraktService
        trakt = TraktService(trakt_cfg)
        trending = trakt.get_trending_shows(limit)

        return {
            "count": len(trending),
            "shows": [
                {
                    "title": item.get("show", {}).get("title"),
                    "year": item.get("show", {}).get("year"),
                    "overview": item.get("show", {}).get("overview"),
                    "watchers": item.get("watchers", 0),
                    "rating": item.get("show", {}).get("rating"),
                    "genres": item.get("show", {}).get("genres", []),
                    "network": item.get("show", {}).get("network"),
                }
                for item in trending
            ]
        }
    except Exception as e:
        logger.error(f"Error getting trending shows from Trakt: {e}")
        return {"error": str(e), "count": 0, "shows": []}


@mcp.tool()
def get_trakt_recommendations_movies(
    limit: int = Field(10, description="Number of recommendations", ge=1, le=25),
) -> Dict[str, Any]:
    """
    Get personalized movie recommendations from Trakt.

    Based on your watch history, returns movies you might enjoy.
    Requires Trakt authentication (access token).

    Example queries:
    - "What movies does Trakt recommend for me?"
    - "Suggest movies based on what I've watched"

    Args:
        limit: Number of recommendations (1-25)

    Returns:
        Dictionary containing personalized movie recommendations
    """
    try:
        trakt_cfg = config.get("traktConfig", {})
        if not trakt_cfg.get("clientId"):
            return {"error": "Trakt not configured. Please set TRAKT_CLIENT_ID.", "movies": []}
        if not trakt_cfg.get("accessToken"):
            return {"error": "Trakt access token required for recommendations. Please set TRAKT_ACCESS_TOKEN.", "movies": []}

        from radarr_sonarr_mcp.services.trakt_service import TraktService
        trakt = TraktService(trakt_cfg)
        recommendations = trakt.get_recommended_movies(limit)

        return {
            "count": len(recommendations),
            "movies": [
                {
                    "title": movie.get("title"),
                    "year": movie.get("year"),
                    "overview": movie.get("overview"),
                    "rating": movie.get("rating"),
                    "genres": movie.get("genres", []),
                }
                for movie in recommendations
            ]
        }
    except Exception as e:
        logger.error(f"Error getting Trakt movie recommendations: {e}")
        return {"error": str(e), "count": 0, "movies": []}


@mcp.tool()
def get_trakt_recommendations_shows(
    limit: int = Field(10, description="Number of recommendations", ge=1, le=25),
) -> Dict[str, Any]:
    """
    Get personalized TV show recommendations from Trakt.

    Based on your watch history, returns shows you might enjoy.
    Requires Trakt authentication (access token).

    Example queries:
    - "What shows does Trakt recommend for me?"
    - "Suggest TV series based on my taste"

    Args:
        limit: Number of recommendations (1-25)

    Returns:
        Dictionary containing personalized show recommendations
    """
    try:
        trakt_cfg = config.get("traktConfig", {})
        if not trakt_cfg.get("clientId"):
            return {"error": "Trakt not configured. Please set TRAKT_CLIENT_ID.", "shows": []}
        if not trakt_cfg.get("accessToken"):
            return {"error": "Trakt access token required for recommendations. Please set TRAKT_ACCESS_TOKEN.", "shows": []}

        from radarr_sonarr_mcp.services.trakt_service import TraktService
        trakt = TraktService(trakt_cfg)
        recommendations = trakt.get_recommended_shows(limit)

        return {
            "count": len(recommendations),
            "shows": [
                {
                    "title": show.get("title"),
                    "year": show.get("year"),
                    "overview": show.get("overview"),
                    "rating": show.get("rating"),
                    "genres": show.get("genres", []),
                    "network": show.get("network"),
                }
                for show in recommendations
            ]
        }
    except Exception as e:
        logger.error(f"Error getting Trakt show recommendations: {e}")
        return {"error": str(e), "count": 0, "shows": []}


@mcp.tool()
def get_trakt_user_stats() -> Dict[str, Any]:
    """
    Get your Trakt user statistics.

    Shows your watch history statistics including total movies/shows watched,
    time spent watching, and more.

    Requires Trakt authentication (access token).

    Example queries:
    - "Show me my Trakt stats"
    - "How many movies have I watched according to Trakt?"

    Returns:
        Dictionary containing comprehensive user statistics
    """
    try:
        trakt_cfg = config.get("traktConfig", {})
        if not trakt_cfg.get("clientId"):
            return {"error": "Trakt not configured. Please set TRAKT_CLIENT_ID."}
        if not trakt_cfg.get("accessToken"):
            return {"error": "Trakt access token required. Please set TRAKT_ACCESS_TOKEN."}

        from radarr_sonarr_mcp.services.trakt_service import TraktService
        trakt = TraktService(trakt_cfg)
        stats = trakt.get_user_stats()

        return stats
    except Exception as e:
        logger.error(f"Error getting Trakt user stats: {e}")
        return {"error": str(e)}


@mcp.tool()
def get_trakt_watch_history(
    media_type: Optional[str] = Field(None, description="Filter: 'movies' or 'shows'"),
    limit: int = Field(20, description="Number of items", ge=1, le=100),
) -> Dict[str, Any]:
    """
    Get your recent watch history from Trakt.

    Shows what you've recently watched across all platforms.
    Requires Trakt authentication (access token).

    Example queries:
    - "What have I watched recently on Trakt?"
    - "Show my movie watch history"

    Args:
        media_type: Filter by 'movies' or 'shows' (None for all)
        limit: Number of items to return (1-100)

    Returns:
        Dictionary containing recent watch history
    """
    try:
        trakt_cfg = config.get("traktConfig", {})
        if not trakt_cfg.get("clientId"):
            return {"error": "Trakt not configured. Please set TRAKT_CLIENT_ID.", "history": []}
        if not trakt_cfg.get("accessToken"):
            return {"error": "Trakt access token required. Please set TRAKT_ACCESS_TOKEN.", "history": []}

        from radarr_sonarr_mcp.services.trakt_service import TraktService
        trakt = TraktService(trakt_cfg)
        history = trakt.get_history(media_type, limit)

        return {
            "count": len(history),
            "history": [
                {
                    "watchedAt": item.get("watched_at"),
                    "action": item.get("action"),
                    "type": item.get("type"),
                    "movie": item.get("movie") if item.get("type") == "movie" else None,
                    "show": item.get("show") if item.get("type") == "episode" else None,
                    "episode": item.get("episode") if item.get("type") == "episode" else None,
                }
                for item in history
            ]
        }
    except Exception as e:
        logger.error(f"Error getting Trakt watch history: {e}")
        return {"error": str(e), "count": 0, "history": []}


# =============================================================================
# Prompts
# =============================================================================

@mcp.prompt()
def whats_new_this_week() -> str:
    """Check what's new in movies and TV this week."""
    return """Please show me what's new this week:
1. Movies releasing in cinemas or digital in the next 7 days
2. New TV episodes airing this week for series I'm watching
3. Highlight anything from popular or highly-rated content
4. Any anticipated releases I should know about

Present this as a weekly digest."""


@mcp.prompt()
def catch_up_on_series() -> str:
    """Find series that need catching up."""
    return """Show me series I should catch up on:
1. Series with new downloaded episodes I haven't watched
2. Series I started but haven't finished
3. Priority order based on what's ending soon or currently popular
4. Estimated time needed to catch up

Help me decide what to binge next!"""


@mcp.prompt()
def plan_movie_marathon() -> str:
    """Plan a themed movie marathon."""
    return """Help me plan a movie marathon:
1. Suggest a theme (director, actor, genre, franchise, decade)
2. Find 4-6 movies in my collection that fit the theme
3. Order them for the best viewing experience
4. Estimate total runtime
5. Note which ones I haven't watched yet

Make it a memorable movie day!"""


@mcp.prompt()
def collection_audit() -> str:
    """Audit collection for improvements."""
    return """Audit my media collection:
1. Missing movies from popular franchises I have started
2. Incomplete TV series (missing episodes or seasons)
3. Most-wanted missing content based on ratings
4. Series I'm watching that have new seasons available
5. Storage hogs (very large files)

Help me optimize and complete my collection!"""


@mcp.prompt()
def recommend_unwatched_movies() -> str:
    """Generate a prompt to recommend unwatched movies from the collection."""
    return """Please analyze my movie collection and recommend 5 unwatched movies
that I should watch next. Consider:
1. Variety of genres
2. Highly rated films
3. Recent releases I might have missed
4. Classic films if available

For each recommendation, explain briefly why I should watch it."""


@mcp.prompt()
def find_series_to_binge() -> str:
    """Generate a prompt to find TV series suitable for binge-watching."""
    return """Please find TV series in my collection that are good for binge-watching.
Look for:
1. Complete series (status: ended) that I haven't watched
2. Series with multiple seasons already downloaded
3. Highly engaging shows across different genres

Recommend 3-5 series with a brief explanation of what makes each one binge-worthy."""


@mcp.prompt()
def media_stats_summary() -> str:
    """Generate a prompt for comprehensive media collection statistics."""
    return """Please provide a comprehensive summary of my media collection including:
1. Total number of movies and TV series
2. Breakdown by watched/unwatched status
3. Storage usage statistics
4. Most common genres
5. Recent additions
6. Completion status of ongoing series

Present this in a clear, organized format."""


@mcp.prompt()
def find_actor_filmography(actor_name: str = "Tom Hanks") -> str:
    """Generate a prompt to explore an actor's filmography in your collection."""
    return f"""Please search my collection for all movies and TV shows featuring {actor_name}.
For each title found, include:
1. Title and year
2. Whether I've watched it
3. Download status
4. Brief description

Organize the results chronologically and highlight any unwatched titles."""


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    logger.info("="*60)
    logger.info("Starting Radarr-Sonarr MCP Server")
    logger.info("="*60)
    logger.info(f"Radarr URL: {radarr_config.base_url}")
    logger.info(f"Sonarr URL: {sonarr_config.base_url}")
    logger.info("="*60)

    # Run the server
    mcp.run()
