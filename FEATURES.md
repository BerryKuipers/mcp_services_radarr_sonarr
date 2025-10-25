# Radarr-Sonarr-Lidarr MCP Server - Features & Capabilities

## Overview

This FastMCP 2.0+ server provides AI assistants with comprehensive access to your media library through Radarr (movies), Sonarr (TV series), and Lidarr (music), with integrated watch status tracking via Jellyfin, Plex, and Trakt.

## ✨ Key Features

### 🎬 Movie Management (Radarr)
- **Browse Collection**: Query your entire movie library with rich metadata
- **Smart Filtering**: Filter by year, download status, watched status, cast/crew
- **Movie Lookup**: Search for new movies to add to your library
- **Detailed Information**: Get comprehensive movie details including genres, ratings, overview

### 📺 TV Series Management (Sonarr)
- **Browse Series**: Access your complete TV series collection
- **Episode Tracking**: View episode details, seasons, and download status
- **Smart Filtering**: Filter by year, download status, watched status, cast
- **Series Lookup**: Search for new shows to add to your library

### 🎵 Music Management (Lidarr)
- **Browse Music**: Query your entire music library with artists and albums
- **Album Tracking**: View album details, track counts, and download status
- **Artist Management**: Browse artists with album counts and statistics
- **Music Lookup**: Search for new artists and albums to add to your library
- **Calendar Integration**: Track upcoming album releases
- **Missing Albums**: Monitor wanted albums that haven't been downloaded

### 👁️ Watch Status Integration
- **Trakt Support**: Primary watch status tracking with trending and recommendations
- **Jellyfin Support**: Automatic watch status from Jellyfin media server
- **Plex Support**: Automatic watch status from Plex media server
- **Multi-Source**: Combines status from multiple sources (priority: Trakt → Jellyfin → Plex)
- **Real-time**: Current watch status for all queries

### 🎯 MCP Core Capabilities

#### 1. Tools (27 Total)

**Movies (3 tools):**
- `get_available_movies` - Query movies with filters (year, downloaded, watched, actors, limit)
- `lookup_movie` - Search for movies by title
- `get_movie_details` - Get detailed information about a specific movie

**TV Series (4 tools):**
- `get_available_series` - Query TV series with filters (year, downloaded, watched, actors, limit)
- `lookup_series` - Search for TV series by title
- `get_series_details` - Get detailed information about a specific series
- `get_series_episodes` - Get episodes for a series with optional season filter

**Music (9 tools):**
- `get_available_albums` - Query albums with filters (artist, monitored, has_file, limit)
- `get_available_artists` - Query artists with filters (monitored, limit)
- `lookup_album` - Search for albums by search term
- `lookup_artist` - Search for artists by search term
- `get_album_details` - Get detailed information about a specific album
- `get_artist_details` - Get detailed information about a specific artist
- `get_upcoming_albums` - Get upcoming album releases from calendar
- `get_missing_albums` - Get monitored albums missing files
- `get_music_collection_statistics` - Comprehensive music library stats

**Calendar & Statistics (5 tools):**
- `get_upcoming_movies` - Movies releasing in next N days
- `get_upcoming_episodes` - TV episodes airing in next N days
- `get_missing_movies` - Monitored movies not downloaded
- `get_missing_episodes` - Monitored episodes not downloaded
- `get_collection_statistics` - Comprehensive collection statistics

**Trakt Integration (6 tools):**
- `get_trakt_trending_movies` - Currently trending movies
- `get_trakt_trending_shows` - Currently trending TV shows
- `get_trakt_recommendations_movies` - Personalized movie recommendations
- `get_trakt_recommendations_shows` - Personalized TV show recommendations
- `get_trakt_user_stats` - User statistics and watch history overview
- `get_trakt_watch_history` - Recent watch history

#### 2. Resources (4 Total)

**Browseable Collections:**
- `radarr://movies` - Browse all movies in formatted markdown
- `sonarr://series` - Browse all TV series in formatted markdown
- `lidarr://albums` - Browse all music albums in formatted markdown
- `lidarr://artists` - Browse all music artists in formatted markdown

Resources provide read-only access to your entire collection in a human-readable format, perfect for browsing and exploration.

#### 3. Prompts (4 Total)

**Pre-built Interaction Templates:**
- `recommend_unwatched_movies` - Get AI recommendations for movies to watch next
- `find_series_to_binge` - Find complete series perfect for binge-watching
- `media_stats_summary` - Get comprehensive collection statistics
- `find_actor_filmography` - Explore an actor's work in your collection

Prompts provide standardized ways to interact with your media library, making common tasks easier.

## 🔧 Advanced Features

### Filtering & Search

All tools support comprehensive filtering:

```python
# Movies
get_available_movies(
    year=2023,              # Filter by release year
    downloaded=True,         # Only downloaded movies
    watched=False,           # Only unwatched
    actors="Tom Hanks",      # Filter by cast
    limit=50                 # Limit results
)

# TV Series
get_available_series(
    year=2022,
    downloaded=True,
    watched=False,
    actors="Pedro Pascal",
    limit=50
)
```

### Rich Metadata

Every response includes:
- Title, year, overview
- Genres and tags
- Download status
- Watch status (from Plex/Jellyfin)
- Episode counts (for series)
- Cast information (when available)
- Custom metadata from Radarr/Sonarr

### Error Handling

- Graceful fallbacks when media servers unavailable
- Detailed error messages in responses
- Comprehensive logging for debugging
- No crashes on API failures

## 📊 Use Cases

### For AI Assistants

1. **Content Discovery**
   - "Show me sci-fi movies from 2023 I haven't watched"
   - "Find comedies with Will Ferrell"
   - "What complete series can I binge this weekend?"

2. **Library Management**
   - "How many unwatched movies do I have?"
   - "Which shows have new episodes downloaded?"
   - "What's the storage size of my collection?"

3. **Recommendations**
   - "Recommend movies based on what I've watched"
   - "Find similar shows to Breaking Bad in my library"
   - "Suggest a movie for family movie night"

4. **Statistics**
   - "Show me my collection statistics"
   - "What genres do I have most of?"
   - "How much of my series are complete?"

## 🔌 Integration

### Supported Platforms

- **Radarr**: API v3+
- **Sonarr**: API v3+
- **Lidarr**: API v1+
- **Trakt**: API v2
- **Jellyfin**: All versions with API support
- **Plex**: All versions with token authentication

### Configuration

Simple environment variable or JSON configuration:
- API keys for Radarr/Sonarr
- Base URLs for Jellyfin/Plex
- User IDs for watch status tracking

### MCP Clients

Compatible with:
- **Claude Desktop**: Full native support
- **Claude.ai**: Via MCP integration
- **Custom MCP Clients**: Any client following MCP specification

## 🚀 Performance

- **Efficient Caching**: Service instances reused
- **Batch Operations**: Single API calls for collections
- **Streaming Resources**: Large collections handled efficiently
- **Configurable Limits**: Prevent overwhelming responses

## 🔒 Security

- **API Key Management**: Secure credential handling
- **Read-Only Operations**: No destructive actions
- **Local Network**: Designed for trusted LAN use
- **No Data Collection**: All processing local

## 📈 Future Enhancements

Potential additions based on MCP evolution:
- **Middleware**: Authentication, rate limiting, logging
- **Sampling**: Allow AI to request additional context
- **Elicitation**: Server-initiated user interactions
- **OAuth Integration**: Enhanced security model
- **Write Operations**: Add movies/series, manage downloads (with user confirmation)

## 🎓 Best Practices

### For Users

1. **Configure All Services**: Get full watch status by connecting both Jellyfin and Plex
2. **Use Filters**: Narrow results for faster, more relevant responses
3. **Leverage Prompts**: Use built-in prompts for common tasks
4. **Explore Resources**: Browse collections without specific queries

### For Developers

1. **Error Handling**: All tools return error information in responses
2. **Type Safety**: Pydantic models ensure data validation
3. **Logging**: Comprehensive logging for debugging
4. **Testing**: Test suite included for reliability

## 📚 Technical Stack

- **FastMCP 2.0+**: Modern MCP framework
- **Pydantic**: Data validation and settings
- **Requests**: HTTP client for API calls
- **Python 3.10+**: Modern Python features

## 🔗 API Coverage

### Radarr API v3
- `/api/v3/movie` - List all movies
- `/api/v3/movie/lookup` - Search movies
- `/api/v3/moviefile` - Movie files

### Sonarr API v3
- `/api/v3/series` - List all series
- `/api/v3/series/lookup` - Search series
- `/api/v3/episode` - Episode information

### Lidarr API v1
- `/api/v1/artist` - List all artists
- `/api/v1/artist/lookup` - Search artists
- `/api/v1/album` - List all albums
- `/api/v1/album/lookup` - Search albums
- `/api/v1/calendar` - Upcoming album releases
- `/api/v1/wanted/missing` - Missing albums

### Trakt API v2
- `/movies/trending` - Trending movies
- `/shows/trending` - Trending TV shows
- `/recommendations/movies` - Personalized movie recommendations
- `/recommendations/shows` - Personalized show recommendations
- `/sync/history` - Watch history
- `/users/stats` - User statistics

### Jellyfin API
- `/Users/{userId}/Items` - Search movies/series
- Episode and playback data

### Plex API
- `/library/search` - Search content
- `/library/metadata` - Item details

---

**Note**: This server is designed for read-only operations. No modifications are made to your Radarr, Sonarr, Lidarr, Jellyfin, Plex, or Trakt installations. All queries are non-destructive.
