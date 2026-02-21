# Radarr and Sonarr MCP Server

A Python-based Model Context Protocol (MCP) server that provides AI assistants like Claude with access to your Radarr (movies) and Sonarr (TV series) data.

<a href="https://glama.ai/mcp/servers/@BerryKuipers/mcp_services_radarr_sonarr">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@BerryKuipers/mcp_services_radarr_sonarr/badge" alt="Radarr and Sonarr Server MCP server" />
</a>

## Overview

This MCP server allows AI assistants to query your movie and TV show collection via Radarr and Sonarr APIs. Built with FastMCP, it implements the standardized protocol for AI context that Claude Desktop and other MCP-compatible clients can use.

## Features

- **Native MCP Implementation**: Built with FastMCP for seamless AI integration
- **Radarr Integration**: Access your movie collection
- **Sonarr Integration**: Access your TV show and episode data
- **Rich Filtering**: Filter by year, watched status, actors, and more
- **Claude Desktop Compatible**: Works seamlessly with Claude's MCP client
- **Easy Setup**: Interactive configuration wizard
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

This server provides the following tools to Claude:

### Movies
- `get_available_movies` - Get a list of movies with optional filters
- `lookup_movie` - Search for a movie by title
- `get_movie_details` - Get detailed information about a specific movie

### Series
- `get_available_series` - Get a list of TV series with optional filters
- `lookup_series` - Search for a TV series by title
- `get_series_details` - Get detailed information about a specific series
- `get_series_episodes` - Get episodes for a specific series

### Resources

The server also provides standard MCP resources:

- `/movies` - Browse all available movies
- `/series` - Browse all available TV series

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