# Trakt.tv Integration Guide

## Overview

This MCP server now includes comprehensive Trakt.tv integration for enhanced watch tracking, trending content discovery, and personalized recommendations.

## What is Trakt?

[Trakt.tv](https://trakt.tv) is a platform that:
- **Tracks what you watch** across all devices and streaming services
- **Provides recommendations** based on your viewing history
- **Shows trending content** - what people are watching worldwide
- **Syncs watch history** across multiple platforms (Plex, Jellyfin, Kodi, etc.)
- **Offers social features** - see what friends are watching

## Features Added

### 1. Enhanced Watch Status Tracking

Trakt is now the **primary source** for watch status, providing more accurate and reliable tracking than Plex/Jellyfin alone.

**Priority Order:**
1. **Trakt** - Most reliable, works across all platforms
2. Jellyfin - Local media server tracking
3. Plex - Local media server tracking

If any service reports content as watched, it's considered watched.

### 2. New MCP Tools (6 Total)

#### Trending Content
- `get_trakt_trending_movies` - What movies are hot right now
- `get_trakt_trending_shows` - What TV shows people are binge-watching

#### Personalized Recommendations
- `get_trakt_recommendations_movies` - AI-powered movie suggestions
- `get_trakt_recommendations_shows` - AI-powered TV show suggestions

#### User Data
- `get_trakt_user_stats` - Your comprehensive watch statistics
- `get_trakt_watch_history` - Recent watch history across all platforms

### 3. TraktService Module

Complete service layer with:
- OAuth authentication support
- Watch history APIs
- Trending/Popular content
- Personalized recommendations
- User stats and ratings
- Search functionality
- Custom lists and watchlists

## Setup

### Step 1: Create a Trakt Application

1. Go to https://trakt.tv/oauth/applications
2. Click "New Application"
3. Fill in the details:
   - **Name**: "Radarr-Sonarr MCP Server" (or your choice)
   - **Redirect URI**: `urn:ietf:wg:oauth:2.0:oob` (for manual token)
4. Click "Save App"
5. You'll receive:
   - **Client ID** (required for all features)
   - **Client Secret** (optional, for OAuth)

### Step 2: Configure the MCP Server

#### Option A: Environment Variables (Recommended)

```bash
export TRAKT_CLIENT_ID="your_client_id_here"
export TRAKT_ACCESS_TOKEN="your_access_token_here"  # Optional
export TRAKT_CLIENT_SECRET="your_client_secret_here"  # Optional
```

#### Option B: config.json

```json
{
  "traktConfig": {
    "clientId": "your_client_id_here",
    "accessToken": "your_access_token_here",
    "clientSecret": "your_client_secret_here"
  }
}
```

### Step 3: Get Access Token (For Personalized Features)

**Required for:**
- Recommendations
- Watch history
- User statistics
- Ratings
- Custom lists

**Steps:**

1. **Manual Token (Easiest)**:
   - Go to https://trakt.tv/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=urn:ietf:wg:oauth:2.0:oob
   - Replace `YOUR_CLIENT_ID` with your actual client ID
   - Authorize the application
   - Copy the code shown
   - Exchange for access token:
     ```bash
     curl -X POST https://api.trakt.tv/oauth/token \
       -H "Content-Type: application/json" \
       -d '{"code":"CODE_FROM_ABOVE","client_id":"YOUR_CLIENT_ID","client_secret":"YOUR_CLIENT_SECRET","redirect_uri":"urn:ietf:wg:oauth:2.0:oob","grant_type":"authorization_code"}'
     ```
   - Save the `access_token` from the response

2. **Use Python Helper** (Coming Soon):
   ```python
   python -m radarr_sonarr_mcp.utils.trakt_auth
   ```

## Features Breakdown

### Public Features (Client ID Only)

No access token required:

- ✅ Enhanced watch status detection
- ✅ Trending movies
- ✅ Trending TV shows
- ✅ Popular content
- ✅ Search

### Personalized Features (Access Token Required)

Requires authentication:

- 🔐 Personalized recommendations
- 🔐 Watch history
- 🔐 User statistics
- 🔐 Ratings
- 🔐 Custom lists
- 🔐 Watchlist

## Usage Examples

### Check Trending Content

**Query:** "What movies are trending on Trakt?"

**Result:**
```json
{
  "count": 10,
  "movies": [
    {
      "title": "Dune: Part Two",
      "year": 2024,
      "watchers": 15234,
      "rating": 8.9,
      "genres": ["Sci-Fi", "Adventure"]
    }
  ]
}
```

### Get Personalized Recommendations

**Query:** "What movies does Trakt recommend for me?"

**Result:** Based on your watch history, Trakt suggests movies you'll likely enjoy.

### View Watch History

**Query:** "What have I watched recently on Trakt?"

**Result:** Shows recent watch activity across all platforms (Plex, Jellyfin, Kodi, web, mobile, etc.)

### Check Your Stats

**Query:** "Show me my Trakt stats"

**Result:**
```json
{
  "movies": {
    "watched": 842,
    "collected": 523,
    "ratings": 156,
    "comments": 23
  },
  "shows": {
    "watched": 124,
    "collected": 89,
    "ratings": 67
  },
  "episodes": {
    "watched": 5234,
    "collected": 3421
  }
}
```

## Benefits of Trakt Integration

### 1. **Universal Watch Tracking**

Unlike Plex/Jellyfin which only track local viewing:
- Works across ALL platforms (Netflix, HBO, etc.)
- Mobile apps automatically scrobble
- Browser extensions track web viewing
- Kodi, VLC, and other players supported

### 2. **Better Recommendations**

Trakt's recommendation engine considers:
- Your entire watch history (not just Plex/Jellyfin)
- Ratings and reviews
- Similar users' preferences
- Trending data

### 3. **Social Features**

- See what friends are watching
- Share recommendations
- Join watch parties
- Discover through community lists

### 4. **Cross-Platform Sync**

Watch on any device, track everywhere:
- Start on Plex, continue on Netflix
- Watch on phone, mark as watched on all devices
- Single source of truth for watch status

## Architecture

### Watch Status Check Flow

```
Query: "Is 'Inception' watched?"
    ↓
1. Check Trakt
   ↓ (if configured)
   Found? → Return True
   ↓ (if not found or error)
2. Check Jellyfin
   ↓ (if configured)
   Found? → Return True
   ↓ (if not found or error)
3. Check Plex
   ↓ (if configured)
   Found? → Return True
   ↓ (if not found)
Return False
```

### TraktService Methods

```python
# Watch Status
is_movie_watched(title, year)
is_show_watched(title)
get_watched_movies()
get_watched_shows()
get_history(media_type, limit)

# Recommendations
get_recommended_movies(limit, ignore_collected)
get_recommended_shows(limit, ignore_collected)

# Trending/Popular
get_trending_movies(limit)
get_trending_shows(limit)
get_popular_movies(limit)
get_popular_shows(limit)

# User Data
get_user_stats(username)
get_user_ratings(media_type, rating)
get_user_lists()
get_watchlist_movies()
get_watchlist_shows()

# Search
search(query, search_type, extended)
```

## Troubleshooting

### "Trakt not configured" Error

**Solution:** Set `TRAKT_CLIENT_ID` environment variable or add to `config.json`

### "Access token required" Error

**Solution:** Some features need authentication. Follow Step 3 above to get an access token.

### Watch Status Not Syncing

**Possible causes:**
1. Title mismatch - Trakt uses exact titles
2. Year mismatch - Provide correct year for movies
3. Not scrobbled - Content must be marked as watched in Trakt

**Solutions:**
- Use Trakt scrobbling tools for Plex/Jellyfin
- Manually mark as watched in Trakt
- Check title/year matching

### Rate Limiting

Trakt API limits:
- **1000 requests per hour** for authenticated users
- **1000 requests per day** for unauthenticated

**Solution:** Use access token for higher limits and better features.

## Privacy & Security

### What Data is Sent to Trakt?

**With Client ID only:**
- API requests for public data (trending, popular)
- No personal data

**With Access Token:**
- Requests for your personal data (history, stats)
- Data stays between you and Trakt
- This MCP server doesn't store any Trakt data

### Security Best Practices

1. **Never share your access token** - it's like a password
2. **Use environment variables** for credentials (not config.json in repos)
3. **Revoke old tokens** at https://trakt.tv/oauth/authorized_applications
4. **Use read-only scopes** if possible (when generating tokens)

## Advanced Features (Coming Soon)

### Planned Additions

1. **Scrobbling** - Auto-mark as watching/watched
2. **List Management** - Create and manage custom lists
3. **Rating Sync** - Sync ratings between Trakt and Radarr/Sonarr
4. **Collection Sync** - Auto-add Trakt watchlist to Radarr/Sonarr
5. **Friends Activity** - See what friends are watching
6. **Watch Together** - Shared viewing sessions

### Integration with Existing Features

Trakt data will enhance:
- `media_stats_summary` prompt - Include Trakt stats
- `recommend_unwatched_movies` - Use Trakt recommendations
- `whats_new_this_week` - Show trending from Trakt

## API Reference

### Public Endpoints (No Auth)

```
GET /movies/trending
GET /movies/popular
GET /shows/trending
GET /shows/popular
GET /search/{type}
```

### Authenticated Endpoints (Access Token Required)

```
GET /sync/watched/movies
GET /sync/watched/shows
GET /sync/history
GET /recommendations/movies
GET /recommendations/shows
GET /users/me/stats
GET /sync/ratings
GET /sync/watchlist
```

## Resources

- **Trakt Website**: https://trakt.tv
- **API Documentation**: https://trakt.docs.apiary.io
- **OAuth Apps**: https://trakt.tv/oauth/applications
- **Python SDK (unofficial)**: https://github.com/fuzeman/trakt.py
- **Scrobbler Tools**: https://github.com/iamkroot/trakt-scrobbler

## Support

### Common Questions

**Q: Do I need a Trakt VIP subscription?**
A: No! All features in this integration work with free Trakt accounts.

**Q: Will this slow down my MCP server?**
A: No, Trakt checks happen in parallel with Plex/Jellyfin and are cached.

**Q: Can I use multiple Trakt accounts?**
A: Yes, configure different access tokens per user.

**Q: Does this work offline?**
A: Trakt features require internet, but the server gracefully falls back to Plex/Jellyfin if Trakt is unavailable.

---

**Trakt integration is now live! Enjoy better recommendations and watch tracking! 🎬📺**
