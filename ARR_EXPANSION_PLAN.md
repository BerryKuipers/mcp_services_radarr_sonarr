# *arr Apps Expansion Plan

## Research Summary

### ✅ Lidarr (Music Management) - **RECOMMENDED**
- **Status**: Active, well-maintained
- **API**: v1 (primary), v3 (exists but not dominant)
- **Purpose**: Music collection manager (Sonarr for music)
- **User Base**: Large, active community
- **Integration Value**: HIGH - Natural extension of current media coverage

### ❌ Readarr (Ebook/Audiobook Management) - **NOT RECOMMENDED**
- **Status**: **RETIRED in 2025**
- **Reason**: Unusable metadata, lack of development time
- **Recommendation**: Skip integration, project is deprecated

### ⚠️ Prowlarr (Indexer Manager) - **MEDIUM PRIORITY**
- **Status**: Active, essential tool for *arr ecosystem
- **API**: Full API support
- **Purpose**: Centralized indexer management for all *arr apps
- **User Base**: Growing, technical users
- **Integration Value**: MEDIUM - More administrative than content-focused

## Recommended Integration Order

### Phase 1: Lidarr Integration (HIGH PRIORITY)

**Why Lidarr First:**
1. Completes the core media trilogy (Movies, TV, Music)
2. Large active user base
3. Similar API to Radarr/Sonarr (easy to implement)
4. High user value - music is major media type

**Lidarr Tools to Implement:**
1. `get_available_albums` - Browse music collection
2. `get_available_artists` - Browse artists
3. `lookup_album` - Search for albums to add
4. `lookup_artist` - Search for artists
5. `get_album_details` - Detailed album info
6. `get_artist_details` - Detailed artist info
7. `get_upcoming_albums` - New releases calendar
8. `get_missing_albums` - Wanted albums not downloaded
9. `get_music_collection_statistics` - Stats for music library

**Lidarr Resources:**
- `lidarr://albums` - Browse all albums
- `lidarr://artists` - Browse all artists

**Integration Benefits:**
- Watch status via Last.fm/ListenBrainz integration
- Complete media management (Movies + TV + Music)
- Genre/mood-based recommendations
- Smart playlists and discovery

### Phase 2: Prowlarr Integration (OPTIONAL)

**Why Prowlarr:**
1. Centralized indexer management
2. Useful for troubleshooting download issues
3. Health monitoring for indexers

**Prowlarr Tools to Implement:**
1. `get_indexer_stats` - Indexer health and statistics
2. `get_indexer_list` - All configured indexers
3. `search_indexers` - Cross-indexer search
4. `get_indexer_history` - Recent indexer activity

**Use Cases:**
- "Which indexers are having issues?"
- "Search all indexers for X"
- "Show me indexer statistics"

**Priority**: Lower than Lidarr, more niche audience

## Implementation Plan for Lidarr

### 1. Create LidarrService

Similar to RadarrService/SonarrService:

```python
# radarr_sonarr_mcp/services/lidarr_service.py

@dataclass
class Album:
    id: int
    title: str
    artist: str
    release_date: str
    monitored: bool
    has_file: bool
    statistics: Optional[AlbumStatistics]
    data: Dict[str, Any]

@dataclass
class Artist:
    id: int
    name: str
    monitored: bool
    album_count: int
    statistics: Optional[ArtistStatistics]
    data: Dict[str, Any]

class LidarrService:
    def __init__(self, config: LidarrConfig):
        self.config = config

    def get_all_artists(self) -> List[Artist]:
        """Fetch all artists from Lidarr."""

    def get_artist(self, artist_id: int) -> Artist:
        """Fetch single artist by ID."""

    def get_all_albums(self) -> List[Album]:
        """Fetch all albums from Lidarr."""

    def get_album(self, album_id: int) -> Album:
        """Fetch single album by ID."""

    def lookup_artist(self, term: str) -> List[Artist]:
        """Search for artists."""

    def lookup_album(self, term: str) -> List[Album]:
        """Search for albums."""
```

### 2. Add Configuration

```python
# radarr_sonarr_mcp/config.py

@dataclass
class LidarrConfig:
    """Configuration for Lidarr API."""
    api_key: str
    base_path: str = "/api/v1"
    port: str = "8686"
    nas_ip: str = "10.0.0.23"

    @property
    def base_url(self) -> str:
        return f"http://{self.nas_ip}:{self.port}{self.base_path}"
```

### 3. Environment Variables

```bash
LIDARR_API_KEY="your_lidarr_api_key"
LIDARR_PORT="8686"
# NAS_IP already configured
```

### 4. MCP Tools

Add 9 new tools for music management, bringing total to **29 tools**.

### 5. Integration with Existing Features

**Watch Status:**
- Integrate Last.fm scrobbling data
- Or ListenBrainz for open-source alternative
- Similar pattern to Trakt for movies/TV

**Collection Statistics:**
- Extend `get_collection_statistics` to include music
- Total artists, albums, tracks
- Storage usage for music
- Genre distribution

**Prompts:**
- `discover_new_music` - Find new albums/artists
- `music_stats_summary` - Music collection analytics
- `plan_music_marathon` - Curated listening sessions

## Benefits of Full *arr Integration

### For Users

1. **Complete Media Management**
   - Movies (Radarr)
   - TV Shows (Sonarr)
   - Music (Lidarr)
   - All in one MCP server!

2. **Unified Interface**
   - Single AI assistant for all media
   - Consistent commands across media types
   - Integrated statistics and recommendations

3. **Cross-Media Insights**
   - "What new media do I have this week?" (movies + TV + music)
   - "Show me all content from 2023"
   - "What's taking up most storage?"

### For the Project

1. **Market Leader**
   - Most comprehensive *arr MCP integration
   - Unique offering in MCP ecosystem
   - Attracts more users

2. **Ecosystem Completion**
   - Covers all major media types
   - Natural progression from current features
   - Sets standard for media MCP servers

3. **Future-Proof**
   - Extensible architecture
   - Easy to add more features
   - Community contributions welcome

## Technical Considerations

### API Compatibility

| App | API Version | Compatibility |
|-----|-------------|---------------|
| Radarr | v3 | ✅ Implemented |
| Sonarr | v3 | ✅ Implemented |
| **Lidarr** | v1 | 🔄 To implement |
| Prowlarr | v1 | ⏳ Future |
| Readarr | v1 | ❌ Deprecated app |

### Code Reusability

- 80% code reuse from Radarr/Sonarr services
- Same patterns: Movies → Albums, TV Shows → Artists
- Configuration handling identical
- Tool structure mirrors existing tools

### Performance

- Same optimization strategies
- Direct API calls for single items
- Batch operations for collections
- Caching opportunities

## Migration Path

### Step 1: Lidarr Core (Now)
- Service layer
- Basic tools (browse, search, details)
- Configuration

### Step 2: Lidarr Advanced (Next)
- Watch status integration (Last.fm/ListenBrainz)
- Calendar and upcoming releases
- Missing albums tracking
- Collection statistics

### Step 3: Prowlarr (Optional)
- Only if user demand exists
- Administrative/technical focus
- Health monitoring

### Step 4: Cross-App Features
- Unified statistics
- Cross-media search
- Integrated recommendations
- Storage analytics

## Estimated Effort

### Lidarr Integration
- **Service Layer**: 2 hours (similar to Radarr/Sonarr)
- **MCP Tools**: 3 hours (9 tools)
- **Documentation**: 1 hour
- **Testing**: 1 hour
- **Total**: ~7 hours

### Prowlarr Integration (Optional)
- **Service Layer**: 1 hour (simpler)
- **MCP Tools**: 2 hours (4-5 tools)
- **Documentation**: 1 hour
- **Total**: ~4 hours

## Success Metrics

1. **Tool Count**: 20 → 29 (+9 music tools)
2. **Media Coverage**: 2 types → 3 types (movies, TV, music)
3. **User Queries**: "What new music..." "Show me albums from..."
4. **Statistics**: Comprehensive cross-media analytics

## Recommendation

**Proceed with Lidarr integration immediately.**

- High user value
- Natural extension
- Relatively easy implementation
- Completes core media trilogy
- Positions project as market leader

**Skip Readarr** - project is retired.

**Consider Prowlarr later** based on user feedback.

---

**Next Steps:**
1. Implement LidarrService
2. Add 9 music management tools
3. Update documentation
4. Test with real Lidarr instance
5. Release as v2.1.0

**Total Tools After Lidarr**: 29
- 3 movies (Radarr)
- 6 TV series (Sonarr)
- 9 music (Lidarr)
- 5 calendar/stats
- 6 Trakt

**The most comprehensive media MCP server available!**
