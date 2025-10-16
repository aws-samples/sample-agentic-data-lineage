# Marquez MCP Server

A Marquez API server based on FastMCP, providing Model Context Protocol (MCP) interface to access the Marquez data lineage platform.

## Features

- 🚀 Built on FastMCP framework
- 📊 Complete Marquez OpenAPI specification support
- 🐳 Docker containerized deployment
- 🔧 Flexible configuration management (supports config files and environment variables)
- 📦 Optimized image size (56MB)

## Quick Start

### Local Development

1. Install dependencies:
```bash
uv venv --python 3.13.0
source .venv/bin/activate
uv sync --active
```

2. Configure settings:
```bash
# Edit settings.toml or set environment variables
export MARQUEZ_OPENAPI_URL="https://raw.githubusercontent.com/MarquezProject/marquez/main/spec/openapi.yml"
export MARQUEZ_API_BASE_URL="http://your-marquez-instance.com"
```

3. Run the server:
```bash
python server.py
```

### Using Docker

Build image:
```bash
docker build -t marquez-mcp .
```

Run container:
```bash
docker run -p 8000:8000 \
  -e MARQUEZ_OPENAPI_URL="https://raw.githubusercontent.com/MarquezProject/marquez/main/spec/openapi.yml" \
  -e MARQUEZ_API_BASE_URL="http://your-marquez-instance.com" \
  marquez-mcp
```

## Configuration

### Configuration File (settings.toml)

```toml
MARQUEZ_OPENAPI_URL = "https://raw.githubusercontent.com/MarquezProject/marquez/main/spec/openapi.yml"
MARQUEZ_API_BASE_URL = "http://marquez.example.com"
```

### Environment Variables

The project uses dynaconf for configuration management, supporting the following environment variables:

- `MARQUEZ_OPENAPI_URL`: URL of the Marquez OpenAPI specification
- `MARQUEZ_API_BASE_URL`: Base URL of the Marquez API

Environment variables will override settings in the configuration file.

## Project Structure

```
.
├── server.py              # Main server file
├── settings.py            # Configuration management
├── settings.toml          # Configuration file
├── client-stdio.py        # Client example
├── Dockerfile             # Docker build file
├── pyproject.toml         # Python project configuration
└── README.md              # Project documentation
```

## Development

### Dependency Management

```bash
# Install dependencies
uv venv --python 3.13.0
source .venv/bin/activate
uv sync --active

# Add new dependencies
uv add package-name
```

### Testing MCP Server

Use the built-in test client to verify MCP server functionality:

```bash
python client-stdio.py
```

**Expected Output:**
```
🔧 Testing MCP server...
✅ Connected to MCP server
✅ Session initialized
✅ Found 37 tools
   1. getNamespace
   2. putNamespace
   3. deleteNamespace
   ... and 34 more
🎉 MCP server test successful!
```

If you see the above output, it means the MCP server is running properly and has successfully loaded the Marquez OpenAPI specification and generated the corresponding tools.

## Architecture

### Component Description

- **FastMCP**: Provides MCP protocol support
- **Dynaconf**: Configuration management
- **HTTPX**: HTTP client for calling Marquez API
- **PyYAML**: YAML parsing for processing OpenAPI specifications

### Workflow

1. Server loads Marquez OpenAPI specification from configured URL at startup
2. Uses FastMCP to convert OpenAPI specification to MCP tools
3. Receives MCP requests and forwards them to Marquez API
4. Returns formatted responses

## Related Links

- [Marquez Project](https://github.com/MarquezProject/marquez)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Dynaconf Documentation](https://dynaconf.readthedocs.io/)## Li
cense

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file in the root directory for details.
