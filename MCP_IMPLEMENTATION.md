# MCP Implementation Guide

## Overview

This document explains how this server implements the Model Context Protocol (MCP) using FastMCP 2.0+, following the latest MCP specifications (June 2025) and best practices.

## MCP Architecture

### What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. It provides a standardized way for AI assistants to:

1. **Execute Actions** via Tools
2. **Access Data** via Resources
3. **Use Templates** via Prompts

### Why FastMCP 2.0+?

We chose FastMCP 2.0+ because it:
- Provides the fastest, most Pythonic way to build MCP servers
- Handles all protocol complexity automatically
- Offers excellent type safety with Pydantic
- Supports latest MCP features (tools, resources, prompts)
- Has strong community adoption (10,000+ GitHub stars)

## Implementation Details

### 1. Server Initialization

```python
from fastmcp import FastMCP

mcp = FastMCP(
    "radarr-sonarr-mcp",
    dependencies=["fastmcp>=2.0.0", "requests>=2.28.0", "pydantic>=2.0.0"]
)
```

**Key Features:**
- Server name identifies the MCP server
- Dependencies ensure version compatibility
- Automatic protocol handling
- Built-in error handling

### 2. Tools Implementation

Tools are Python functions decorated with `@mcp.tool()`:

```python
@mcp.tool()
def get_available_movies(
    year: Optional[int] = Field(None, description="Filter by release year"),
    downloaded: Optional[bool] = Field(None, description="Filter by download status"),
    watched: Optional[bool] = Field(None, description="Filter by watched status"),
    actors: Optional[str] = Field(None, description="Filter by actor/actress name"),
    limit: int = Field(100, description="Maximum number of results", ge=1, le=1000),
) -> Dict[str, Any]:
    """
    Get a list of available movies from Radarr with optional filters.

    This tool retrieves your movie collection from Radarr and supports filtering.
    """
    # Implementation
```

**Best Practices Applied:**
- ✅ Clear, descriptive function names
- ✅ Comprehensive docstrings
- ✅ Type hints for all parameters
- ✅ Pydantic Field validators for constraints
- ✅ Detailed parameter descriptions
- ✅ Return type annotations
- ✅ Example usage in docstrings
- ✅ Error handling with try/except
- ✅ Structured return values

**Why This Matters:**
- FastMCP automatically generates JSON schemas from type hints
- Descriptions appear in MCP client UIs
- Validators ensure parameter validity
- Structured returns enable AI parsing

### 3. Resources Implementation

Resources provide read-only data access:

```python
@mcp.resource("radarr://movies")
def movies_resource() -> str:
    """
    Browse all available movies from Radarr.

    Returns a formatted list of all movies in your collection.
    """
    movies = radarr_service.get_all_movies()
    output = f"# Movies Collection ({len(movies)} total)\n\n"
    # Format movies in markdown
    return output
```

**URI Scheme Design:**
- `radarr://movies` - Custom URI scheme for Radarr resources
- `sonarr://series` - Custom URI scheme for Sonarr resources

**Best Practices Applied:**
- ✅ Descriptive URI schemes
- ✅ Human-readable output format (Markdown)
- ✅ Pagination/limiting for large collections
- ✅ Error handling
- ✅ Clear documentation

**Why Resources?**
- Browseable data without specific queries
- AI can explore collections naturally
- Perfect for discovery and exploration
- Efficient for large datasets

### 4. Prompts Implementation

Prompts are reusable interaction templates:

```python
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
```

**Best Practices Applied:**
- ✅ Task-specific prompts
- ✅ Clear instructions
- ✅ Structured output requests
- ✅ Contextual guidelines

**Why Prompts?**
- Standardize common tasks
- Better, more consistent AI responses
- Centralized prompt management
- Easier for users to discover capabilities

## MCP Specification Compliance

### Protocol Version

This implementation follows the **MCP June 2025 specification** (latest stable):
- Structured tool outputs ✅
- Resource URIs with custom schemes ✅
- Prompt templates ✅
- Error handling best practices ✅

### Future MCP Features

The November 2025 specification will add:
- **OAuth Authorization**: Enhanced security (we can add this later)
- **Elicitation**: Server-initiated interactions (future enhancement)
- **Sampling**: AI can request additional context (future enhancement)

Our implementation is designed to easily adopt these features when available.

## Data Flow

```
┌─────────────────┐
│   MCP Client    │
│ (Claude, etc.)  │
└────────┬────────┘
         │
         │ MCP Protocol
         │ (JSON-RPC)
         │
┌────────▼────────┐
│   FastMCP 2.0   │
│   Server Core   │
└────────┬────────┘
         │
         │ Decorators invoke
         │
┌────────▼────────┐
│  Our Functions  │
│ Tools/Resources │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│Radarr│  │Sonarr│
│Service│  │Service│
└───┬──┘  └──┬───┘
    │        │
┌───▼────────▼───┐
│  Radarr/Sonarr │
│   APIs (v3)    │
└────────────────┘
    │        │
┌───▼───┐ ┌──▼──────┐
│Jellyfin│ │  Plex   │
│  API   │ │   API   │
└────────┘ └─────────┘
```

## Configuration Management

### Environment Variables (Preferred)

```bash
export NAS_IP="10.0.0.23"
export RADARR_PORT="7878"
export SONARR_PORT="8989"
export RADARR_API_KEY="your_key"
export SONARR_API_KEY="your_key"
export JELLYFIN_BASE_URL="http://10.0.0.23:5055"
export JELLYFIN_API_KEY="your_key"
export JELLYFIN_USER_ID="your_id"
export PLEX_BASE_URL="http://10.0.0.23:32400"
export PLEX_TOKEN="your_token"
```

### Config File (Alternative)

```json
{
  "nasConfig": {"ip": "10.0.0.23"},
  "radarrConfig": {
    "apiKey": "your_key",
    "basePath": "/api/v3",
    "port": "7878",
    "nasIp": "10.0.0.23"
  },
  "sonarrConfig": {
    "apiKey": "your_key",
    "basePath": "/api/v3",
    "port": "8989",
    "nasIp": "10.0.0.23"
  },
  "jellyfinConfig": {
    "baseUrl": "http://10.0.0.23:5055",
    "apiKey": "your_key",
    "userId": "your_id"
  },
  "plexConfig": {
    "baseUrl": "http://10.0.0.23:32400",
    "token": "your_token"
  }
}
```

## Error Handling Strategy

### Tool Errors

All tools return structured errors:

```python
try:
    # Operation
    return {"count": 10, "movies": [...]}
except Exception as e:
    logger.error(f"Error: {e}")
    return {"error": str(e), "count": 0, "movies": []}
```

**Benefits:**
- AI can handle errors gracefully
- Errors don't crash the server
- Detailed logging for debugging
- Structured error responses

### Service Errors

Service layer handles API errors:

```python
try:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()
except requests.RequestException as e:
    logging.error(f"API error: {e}")
    raise Exception(f"Failed to fetch data: {e}")
```

### Watch Status Fallbacks

```python
# Try Jellyfin
try:
    jellyfin = JellyfinService(config)
    statuses.append(jellyfin.is_movie_watched(title))
except Exception as e:
    logger.debug(f"Jellyfin unavailable: {e}")
    # Continue without Jellyfin

# Try Plex
try:
    plex = PlexService(config)
    statuses.append(plex.is_movie_watched(title))
except Exception as e:
    logger.debug(f"Plex unavailable: {e}")
    # Continue without Plex

# Use any available status
return any(statuses) if statuses else False
```

## Performance Optimizations

### 1. Service Reuse

Services are instantiated once at startup:

```python
radarr_service = RadarrService(radarr_config)
sonarr_service = SonarrService(sonarr_config)
```

### 2. Result Limiting

All tools support limits:

```python
limit: int = Field(100, description="Max results", ge=1, le=1000)
filtered_movies = filtered_movies[:limit]
```

### 3. Efficient Filtering

Filter in Python, not via multiple API calls:

```python
all_movies = radarr_service.get_all_movies()  # One API call
filtered = [m for m in all_movies if m.year == 2023]  # Filter locally
```

### 4. Resource Pagination

Resources limit output to prevent overwhelming responses:

```python
for movie in movies[:100]:  # First 100 only
    # Format movie

if len(movies) > 100:
    output += f"\n... and {len(movies) - 100} more movies\n"
```

## Testing Strategy

### Unit Tests

Test individual services:

```python
def test_radarr_service():
    service = RadarrService(config)
    movies = service.get_all_movies()
    assert isinstance(movies, list)
```

### Integration Tests

Test MCP tools:

```python
def test_get_available_movies():
    result = get_available_movies(year=2023, limit=10)
    assert "movies" in result
    assert result["count"] <= 10
```

### Mock External APIs

Use pytest fixtures to mock Radarr/Sonarr APIs.

## Deployment

### Local Development

```bash
python radarr_sonarr_mcp/server.py
```

### Production with UV

```bash
uv run radarr_sonarr_mcp/server.py
```

### MCP Client Configuration (Claude Desktop)

```json
{
  "mcpServers": {
    "radarr_sonarr": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/radarr-sonarr-mcp",
        "run", "radarr_sonarr_mcp/server.py"
      ],
      "env": {
        "NAS_IP": "10.0.0.23",
        "RADARR_PORT": "7878",
        "SONARR_PORT": "8989",
        "RADARR_API_KEY": "your_key",
        "SONARR_API_KEY": "your_key"
      }
    }
  }
}
```

## Code Quality

### Type Safety

- All functions have type hints
- Pydantic models for data validation
- Runtime type checking via Field validators

### Documentation

- Comprehensive docstrings
- Example usage in tool descriptions
- Architecture documentation
- API reference

### Logging

```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Code Style

- Black formatter (line length: 100)
- Ruff linter
- MyPy type checker
- Pytest for testing

## Future Enhancements

### Planned Features

1. **Write Operations** (with user confirmation)
   - Add movies to Radarr
   - Add series to Sonarr
   - Manage download queue

2. **Advanced Filtering**
   - Quality profiles
   - Release dates
   - Custom lists

3. **Statistics Tools**
   - Collection analytics
   - Storage reports
   - Download history

4. **Middleware** (FastMCP 2.0 feature)
   - Authentication
   - Rate limiting
   - Request logging
   - Caching

5. **OAuth Integration** (MCP Nov 2025)
   - Secure authorization
   - Token management
   - Multi-user support

## Contributing

When adding new features:

1. Follow existing patterns
2. Add comprehensive docstrings
3. Include type hints
4. Handle errors gracefully
5. Write tests
6. Update documentation

## References

- [MCP Specification](https://modelcontextprotocol.io/specification/latest)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Radarr API Docs](https://radarr.video/docs/api/)
- [Sonarr API Docs](https://sonarr.tv/docs/api/)
