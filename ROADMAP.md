# Radarr-Sonarr MCP Server - Feature Roadmap

## 🎯 Current Implementation (v2.0.0)

### ✅ Completed Features
- 9 Tools (3 movies, 6 series)
- 2 Resources (browseable collections)
- 4 Prompts (recommendations, binge-finding, stats, actor search)
- Watch status integration (Jellyfin, Plex)
- Comprehensive error handling
- Full MCP specification compliance

---

## 🚀 Proposed Additional Features

Based on Radarr/Sonarr API capabilities and user needs, here are valuable additions:

### 1. 📅 Calendar & Upcoming Content

**Tools to Add:**

```python
@mcp.tool()
def get_upcoming_movies(
    days_ahead: int = Field(30, description="Days to look ahead", ge=1, le=365)
) -> Dict[str, Any]:
    """
    Get movies releasing in the next N days (in cinemas or digital).

    Useful for:
    - "What movies are coming out this month?"
    - "Show me upcoming releases in the next 7 days"
    - Planning what to watch
    """
    # Uses Radarr's /api/v3/calendar endpoint

@mcp.tool()
def get_upcoming_episodes(
    days_ahead: int = Field(7, description="Days to look ahead", ge=1, le=365),
    unmonitored: bool = Field(False, description="Include unmonitored series")
) -> Dict[str, Any]:
    """
    Get TV episodes airing in the next N days.

    Useful for:
    - "What new episodes are coming this week?"
    - "Show me upcoming episodes for my series"
    - Stay up-to-date with shows
    """
    # Uses Sonarr's /api/v3/calendar endpoint
```

**Prompt to Add:**
```python
@mcp.prompt()
def whats_new_this_week() -> str:
    """Check what's new in movies and TV this week"""
    return """Please show me what's new this week:
1. Movies releasing in cinemas or digital
2. New TV episodes for series I'm watching
3. Highlight anything from my favorite actors/shows
4. Any highly anticipated releases"""
```

**User Benefit**: Stay informed about new content without manually checking

---

### 2. 🎬 Missing & Wanted Content

**Tools to Add:**

```python
@mcp.tool()
def get_missing_movies(
    limit: int = Field(50, ge=1, le=500)
) -> Dict[str, Any]:
    """
    Get movies in your library that haven't been downloaded yet.

    Useful for:
    - "What movies am I missing?"
    - "Show me my wishlist that hasn't downloaded"
    - Track your wanted content
    """
    # Filter movies where hasFile=False and monitored=True

@mcp.tool()
def get_missing_episodes(
    series_id: Optional[int] = None,
    limit: int = Field(100, ge=1, le=1000)
) -> Dict[str, Any]:
    """
    Get episodes that haven't been downloaded yet.

    Useful for:
    - "What episodes am I missing?"
    - "Show missing episodes for Breaking Bad"
    - Complete your series
    """
    # Uses Sonarr's /api/v3/wanted/missing endpoint
```

**User Benefit**: Easily identify gaps in your collection

---

### 3. 📊 Quality Management

**Tools to Add:**

```python
@mcp.tool()
def get_quality_profiles() -> Dict[str, Any]:
    """
    Get available quality profiles for movies and series.

    Useful for:
    - "What quality profiles do I have?"
    - Understanding download settings
    """
    # Radarr: /api/v3/qualityprofile
    # Sonarr: /api/v3/qualityprofile

@mcp.tool()
def get_movies_by_quality(
    quality_profile: str,
    limit: int = Field(100, ge=1, le=1000)
) -> Dict[str, Any]:
    """
    Find movies using a specific quality profile.

    Useful for:
    - "Show me all 4K movies"
    - "What's in my 1080p collection?"
    """
```

**User Benefit**: Manage quality settings and understand your collection's quality distribution

---

### 4. 🏷️ Tags & Organization

**Tools to Add:**

```python
@mcp.tool()
def get_all_tags() -> Dict[str, Any]:
    """
    Get all tags defined in Radarr/Sonarr.

    Useful for:
    - "What tags do I have?"
    - Understanding your organization system
    """
    # /api/v3/tag

@mcp.tool()
def get_movies_by_tag(
    tag_name: str,
    limit: int = Field(100, ge=1, le=1000)
) -> Dict[str, Any]:
    """
    Find content with a specific tag.

    Useful for:
    - "Show me movies tagged 'family'"
    - "What's in my 'classics' collection?"
    - Organize by custom categories
    """

@mcp.tool()
def add_tag_to_movie(
    movie_id: int,
    tag_name: str
) -> Dict[str, Any]:
    """
    Add a tag to a movie (requires user confirmation).

    Useful for:
    - "Tag this as a favorite"
    - Build custom collections
    """
```

**User Benefit**: Better organization and custom categorization

---

### 5. 🌟 Recommendations & Discovery

**Tools to Add:**

```python
@mcp.tool()
def get_similar_movies(
    movie_id: int,
    limit: int = Field(10, ge=1, le=50)
) -> Dict[str, Any]:
    """
    Find movies similar to a given movie.

    Useful for:
    - "Show me movies like Inception"
    - Discover similar content
    """
    # Can use TMDB integration via Radarr

@mcp.tool()
def get_popular_movies(
    limit: int = Field(20, ge=1, le=100)
) -> Dict[str, Any]:
    """
    Get currently popular/trending movies.

    Useful for:
    - "What movies are popular right now?"
    - Discover new content
    """
    # Uses Radarr's discover/lists features

@mcp.tool()
def get_recommendations_based_on_watched() -> Dict[str, Any]:
    """
    Get personalized recommendations based on what you've watched.

    Analyzes your watched content and suggests similar movies/shows.
    """
```

**Prompts to Add:**
```python
@mcp.prompt()
def discover_new_content() -> str:
    """Discover new movies and shows to add"""
    return """Based on my collection and watch history, recommend:
1. 5 movies I should add to my library
2. 3 TV series I might enjoy
3. Hidden gems in my preferred genres
4. Popular content I'm missing"""
```

**User Benefit**: Smart content discovery and recommendations

---

### 6. 📈 Statistics & Analytics

**Tools to Add:**

```python
@mcp.tool()
def get_collection_statistics() -> Dict[str, Any]:
    """
    Get comprehensive statistics about your entire collection.

    Returns:
    - Total movies/series count
    - Total storage used
    - Watched vs unwatched breakdown
    - Genre distribution
    - Quality distribution
    - Average ratings
    - Completion percentages
    """

@mcp.tool()
def get_genre_breakdown(
    media_type: str = Field("movies", description="'movies' or 'series'")
) -> Dict[str, Any]:
    """
    Get detailed genre statistics.

    Useful for:
    - "What genres do I watch most?"
    - Understanding your preferences
    """

@mcp.tool()
def get_storage_report() -> Dict[str, Any]:
    """
    Get storage usage report.

    Shows:
    - Total storage used
    - Breakdown by movies/series
    - Largest files
    - Storage growth over time
    """
```

**User Benefit**: Understand your collection patterns and manage storage

---

### 7. 🔍 Advanced Search

**Tools to Add:**

```python
@mcp.tool()
def search_by_imdb_id(
    imdb_id: str
) -> Dict[str, Any]:
    """
    Find content by IMDb ID.

    Useful for:
    - Precise movie/show identification
    - Cross-reference with other services
    """

@mcp.tool()
def search_by_genre(
    genre: str,
    media_type: str = Field("movies", description="'movies' or 'series'"),
    min_rating: Optional[float] = None,
    limit: int = Field(50, ge=1, le=500)
) -> Dict[str, Any]:
    """
    Search for content by genre with optional rating filter.

    Useful for:
    - "Show me top-rated sci-fi movies"
    - "Find comedy series above 8.0 rating"
    """

@mcp.tool()
def search_by_release_date_range(
    start_year: int,
    end_year: int,
    media_type: str = Field("movies")
) -> Dict[str, Any]:
    """
    Find content released in a date range.

    Useful for:
    - "Show me movies from the 1990s"
    - "Find 2020-2023 releases"
    """
```

**User Benefit**: More powerful and flexible searching

---

### 8. 🎭 Collections & Lists

**Tools to Add:**

```python
@mcp.tool()
def get_movie_collections() -> Dict[str, Any]:
    """
    Get all movie collections (e.g., Marvel Cinematic Universe).

    Useful for:
    - "What collections do I have?"
    - Browse related movies together
    """
    # Uses Radarr's /api/v3/collection endpoint

@mcp.tool()
def get_collection_details(
    collection_id: int
) -> Dict[str, Any]:
    """
    Get detailed information about a specific collection.

    Shows all movies in the collection and completion status.
    """

@mcp.tool()
def get_custom_lists() -> Dict[str, Any]:
    """
    Get custom lists configured in Radarr/Sonarr.

    Useful for integrating with Trakt, IMDb lists, etc.
    """
```

**User Benefit**: Better organization of related content

---

### 9. 📥 Download Management (Read-Only Initially)

**Tools to Add:**

```python
@mcp.tool()
def get_download_queue() -> Dict[str, Any]:
    """
    View current download queue.

    Shows:
    - What's currently downloading
    - Download progress
    - ETA for completion
    """
    # Uses /api/v3/queue endpoint

@mcp.tool()
def get_download_history(
    limit: int = Field(50, ge=1, le=200)
) -> Dict[str, Any]:
    """
    Get recent download history.

    Shows:
    - Recently completed downloads
    - Failed downloads
    - Import status
    """
    # Uses /api/v3/history endpoint
```

**User Benefit**: Monitor downloads without opening Radarr/Sonarr UI

---

### 10. 🎯 Smart Filters & Saved Searches

**Tools to Add:**

```python
@mcp.tool()
def create_smart_filter(
    name: str,
    filters: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a saved filter for quick access.

    Example: "Create a filter for unwatched sci-fi from 2020+"
    """

@mcp.tool()
def apply_saved_filter(
    filter_name: str
) -> Dict[str, Any]:
    """
    Apply a previously saved filter.
    """
```

**User Benefit**: Quick access to frequently used searches

---

### 11. 🔔 Notifications & Monitoring

**Tools to Add:**

```python
@mcp.tool()
def get_system_status() -> Dict[str, Any]:
    """
    Get Radarr/Sonarr system status.

    Shows:
    - System health
    - Disk space
    - Indexer status
    - Any warnings/errors
    """
    # Uses /api/v3/system/status and /api/v3/health

@mcp.tool()
def get_indexer_statistics() -> Dict[str, Any]:
    """
    Get statistics about configured indexers.

    Shows which indexers are most successful.
    """
```

**User Benefit**: Monitor system health and performance

---

## 📋 Implementation Priority

### Phase 1 (High Priority - Next Release)
1. ✅ **Calendar & Upcoming Content** - High user value, easy to implement
2. ✅ **Missing & Wanted Content** - Essential for collection management
3. ✅ **Collection Statistics** - Users love analytics

### Phase 2 (Medium Priority)
4. **Quality Management** - Important for power users
5. **Tags & Organization** - Better organization
6. **Download Queue/History** - Read-only monitoring

### Phase 3 (Future Enhancements)
7. **Recommendations & Discovery** - Requires TMDB/TVDB integration
8. **Collections & Lists** - Nice to have
9. **Advanced Search** - Enhance existing search
10. **Smart Filters** - Power user feature

### Phase 4 (Advanced Features)
11. **Write Operations** (with user confirmation)
    - Add movies/series
    - Trigger manual searches
    - Manage tags
    - Update quality profiles

---

## 🎨 Enhanced Prompts

Additional useful prompts:

```python
@mcp.prompt()
def plan_movie_marathon() -> str:
    """Plan a themed movie marathon"""
    return """Help me plan a movie marathon:
1. Suggest a theme (director, genre, franchise)
2. Find 4-6 movies in my collection that fit
3. Order them for best viewing experience
4. Estimate total runtime
5. Suggest snack pairings!"""

@mcp.prompt()
def catch_up_on_series() -> str:
    """Find series that need catching up"""
    return """Show me series I should catch up on:
1. Series with new downloaded episodes I haven't watched
2. Series I started but didn't finish
3. Priority order based on what's popular/ending soon"""

@mcp.prompt()
def weekend_watch_suggestions() -> str:
    """Get weekend viewing suggestions"""
    return """Plan my weekend watching:
Friday night: 1 movie (suggest based on mood: action, comedy, drama)
Saturday: 1 movie marathon or binge-worthy series
Sunday: Light entertainment or comfort viewing"""

@mcp.prompt()
def collection_audit() -> str:
    """Audit collection for issues"""
    return """Audit my collection:
1. Missing movies from popular franchises
2. Incomplete TV series
3. Low quality files that should be upgraded
4. Duplicate content
5. Content I'll never watch (suggest removal)"""
```

---

## 🔌 Integration Opportunities

### Potential Integrations

1. **TMDB/TVDB**
   - Enhanced metadata
   - Better recommendations
   - Similar content suggestions

2. **Trakt.tv**
   - Watch history sync
   - Social features
   - Better recommendations

3. **OpenAI**
   - Natural language queries
   - Smart summaries
   - Personalized descriptions

4. **YouTube**
   - Trailer links
   - Review compilation

---

## 💡 User-Requested Features

Based on common use cases:

### Family Features
```python
@mcp.tool()
def get_family_friendly_content(
    max_rating: str = "PG-13"
) -> Dict[str, Any]:
    """Find family-friendly movies and shows"""

@mcp.tool()
def create_kids_profile_filter() -> Dict[str, Any]:
    """Filter content appropriate for children"""
```

### Party/Social Features
```python
@mcp.prompt()
def group_watch_suggestions(
    group_size: int = 4,
    genre_preference: Optional[str] = None
) -> str:
    """Suggest movies perfect for group watching"""
```

### Seasonal Features
```python
@mcp.tool()
def get_seasonal_content(
    season: str = Field(..., description="'halloween', 'christmas', 'summer', etc.")
) -> Dict[str, Any]:
    """Find seasonal/holiday themed content"""
```

---

## 🎯 Success Metrics

For prioritizing features:

1. **User Value**: How many users benefit?
2. **Implementation Effort**: How complex is it?
3. **API Support**: Does the API support it well?
4. **Uniqueness**: Can users easily do this elsewhere?

---

## 🚦 Next Steps

1. **Community Feedback**: Gather user requests
2. **Phase 1 Implementation**: Calendar, Missing Content, Statistics
3. **Testing**: Ensure reliability
4. **Documentation**: Update docs for new features
5. **Release**: v2.1.0 with Phase 1 features

---

## 📝 Contributing

Users can request features by:
1. Opening GitHub issues
2. Voting on existing feature requests
3. Contributing pull requests

**Most Wanted Features** will be prioritized!

---

**This roadmap is a living document and will be updated based on user feedback and API capabilities.**
