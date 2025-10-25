# Radarr, Sonarr, and Lidarr MCP Server

A Python-based Model Context Protocol (MCP) server that provides AI assistants like Claude with access to your Radarr (movies), Sonarr (TV series), and Lidarr (music) data.

## Overview

This MCP server allows AI assistants to query your complete media library via Radarr, Sonarr, and Lidarr APIs. Built with FastMCP 2.0+, it implements the standardized protocol for AI context that Claude Desktop and other MCP-compatible clients can use.

## Features

- **Native MCP 2.0+ Implementation**: Built with FastMCP for seamless AI integration
- **Radarr Integration**: Access your movie collection with 3 tools
- **Sonarr Integration**: Access your TV show and episode data with 4 tools
- **Lidarr Integration**: Access your music library with 9 tools for artists and albums
- **Trakt Integration**: Watch status tracking, trending content, and personalized recommendations (6 tools)
- **Calendar & Statistics**: Upcoming releases and comprehensive collection statistics (5 tools)
- **Rich Filtering**: Filter by year, watched status, actors, artists, and more
- **Multi-Source Watch Status**: Trakt, Jellyfin, and Plex integration
- **Claude Desktop Compatible**: Works seamlessly with Claude's MCP client
- **29 Total Tools**: Comprehensive media management capabilities
- **4 Resources**: Browse your entire collection
- **Well-tested**: Comprehensive test suite for reliability

## Installation

### From Source

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/radarr-sonarr-mcp.git
   cd radarr-sonarr-mcp-python
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

### Using pip (coming soon)

```bash
pip install radarr-sonarr-mcp
```

## Quick Start

1. Configure the server:
   ```bash
   radarr-sonarr-mcp configure
   ```
   Follow the prompts to enter your Radarr/Sonarr API keys and other settings.

2. Start the server:
   ```bash
   radarr-sonarr-mcp start
   ```

3. Connect Claude Desktop:
   - In Claude Desktop, go to Settings > MCP Servers
   - Add a new server with URL: `http://localhost:3000` (or your configured port)

## Configuration

The configuration wizard will guide you through setting up:

- NAS/Server IP address
- Radarr API key and port
- Sonarr API key and port
- MCP server port

You can also manually edit the `config.json` file:

```json
{
  "nasConfig": {
    "ip": "10.0.0.23",
    "port": "7878"
  },
  "radarrConfig": {
    "apiKey": "YOUR_RADARR_API_KEY",
    "basePath": "/api/v3",
    "port": "7878"
  },
  "sonarrConfig": {
    "apiKey": "YOUR_SONARR_API_KEY",
    "basePath": "/api/v3",
    "port": "8989"
  },
  "server": {
    "port": 3000
  }
}
```

## Available MCP Tools

This server provides **29 tools** across 5 categories:

### Movies (3 tools)
- `get_available_movies` - Get a list of movies with optional filters
- `lookup_movie` - Search for a movie by title
- `get_movie_details` - Get detailed information about a specific movie

### TV Series (4 tools)
- `get_available_series` - Get a list of TV series with optional filters
- `lookup_series` - Search for a TV series by title
- `get_series_details` - Get detailed information about a specific series
- `get_series_episodes` - Get episodes for a specific series

### Music (9 tools)
- `get_available_albums` - Get a list of albums with optional filters
- `get_available_artists` - Get a list of artists with optional filters
- `lookup_album` - Search for albums by search term
- `lookup_artist` - Search for artists by search term
- `get_album_details` - Get detailed information about a specific album
- `get_artist_details` - Get detailed information about a specific artist
- `get_upcoming_albums` - Get upcoming album releases
- `get_missing_albums` - Get monitored albums without files
- `get_music_collection_statistics` - Get comprehensive music library stats

### Calendar & Statistics (5 tools)
- `get_upcoming_movies` - Get movies releasing in next N days
- `get_upcoming_episodes` - Get TV episodes airing in next N days
- `get_missing_movies` - Get monitored movies not downloaded
- `get_missing_episodes` - Get monitored episodes not downloaded
- `get_collection_statistics` - Get comprehensive collection statistics

### Trakt Integration (6 tools)
- `get_trakt_trending_movies` - Get currently trending movies
- `get_trakt_trending_shows` - Get currently trending TV shows
- `get_trakt_recommendations_movies` - Get personalized movie recommendations
- `get_trakt_recommendations_shows` - Get personalized TV show recommendations
- `get_trakt_user_stats` - Get user statistics and watch history overview
- `get_trakt_watch_history` - Get recent watch history

### Resources (4 total)

The server also provides standard MCP resources:

- `radarr://movies` - Browse all available movies
- `sonarr://series` - Browse all available TV series
- `lidarr://albums` - Browse all music albums
- `lidarr://artists` - Browse all music artists

### Filtering Options

Most tools support various filtering options:

- `year` - Filter by release year
- `watched` - Filter by watched status (true/false)
- `downloaded` - Filter by download status (true/false)
- `watchlist` - Filter by watchlist status (true/false)
- `actors` - Filter by actor/cast name
- `actresses` - Filter by actress name (movies only)

## Example Queries for Claude

Once your MCP server is connected to Claude Desktop, you can ask questions like:

- "What sci-fi movies from 2023 do I have?"
- "Show me TV shows starring Pedro Pascal"
- "Do I have any unwatched episodes of The Mandalorian?"
- "Find movies with Tom Hanks that I haven't watched yet"
- "How many episodes of Stranger Things do I have downloaded?"

## Finding API Keys

### Radarr API Key
1. Open Radarr in your browser
2. Go to Settings > General
3. Find the "API Key" section
4. Copy the API Key

### Sonarr API Key
1. Open Sonarr in your browser
2. Go to Settings > General
3. Find the "API Key" section
4. Copy the API Key

### Lidarr API Key
1. Open Lidarr in your browser
2. Go to Settings > General
3. Find the "API Key" section
4. Copy the API Key

### Trakt API Setup
See [TRAKT_INTEGRATION.md](TRAKT_INTEGRATION.md) for detailed setup instructions including:
- Creating a Trakt application
- Obtaining OAuth tokens
- Configuring personalized recommendations

## Command-Line Interface

The package provides a command-line interface:

- `radarr-sonarr-mcp configure` - Run configuration wizard
- `radarr-sonarr-mcp start` - Start the MCP server
- `radarr-sonarr-mcp status` - Show the current configuration

## Development

### Running Tests

To run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=radarr_sonarr_mcp
```

### Local Development

For quick development and testing:

```bash
# Run directly without installation
python run.py
```

## Requirements

- Python 3.7+
- FastMCP
- Requests
- Pydantic

## Notes

- The watched/watchlist status functionality assumes these are tracked using specific mechanisms in Radarr/Sonarr. You may need to adapt this to your specific setup.
- For security reasons, it's recommended to run this server only on your local network.
