"""Configuration data classes for Radarr and Sonarr MCP Server."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RadarrConfig:
    """Configuration for Radarr API."""
    api_key: str
    base_path: str = "/api/v3"
    port: str = "7878"
    nas_ip: str = "10.0.0.23"

    @property
    def base_url(self) -> str:
        """Get the full base URL for Radarr API."""
        return f"http://{self.nas_ip}:{self.port}{self.base_path}"


@dataclass
class SonarrConfig:
    """Configuration for Sonarr API."""
    api_key: str
    base_path: str = "/api/v3"
    port: str = "8989"
    nas_ip: str = "10.0.0.23"

    @property
    def base_url(self) -> str:
        """Get the full base URL for Sonarr API."""
        return f"http://{self.nas_ip}:{self.port}{self.base_path}"


@dataclass
class LidarrConfig:
    """Configuration for Lidarr API."""
    api_key: str
    base_path: str = "/api/v1"
    port: str = "8686"
    nas_ip: str = "10.0.0.23"

    @property
    def base_url(self) -> str:
        """Get the full base URL for Lidarr API."""
        return f"http://{self.nas_ip}:{self.port}{self.base_path}"


@dataclass
class JellyfinConfig:
    """Configuration for Jellyfin API."""
    base_url: str
    api_key: str
    user_id: str


@dataclass
class PlexConfig:
    """Configuration for Plex API."""
    base_url: str
    token: str


@dataclass
class TraktConfig:
    """Configuration for Trakt API."""
    client_id: str = ""
    access_token: str = ""
    client_secret: str = ""


@dataclass
class ServerConfig:
    """Configuration for MCP Server."""
    port: int = 3000
