import asyncio
import logging

import httpx
import yaml
from fastmcp import FastMCP
from fastmcp.server.openapi import MCPType, RouteMap
from settings import settings
from starlette.requests import Request
from starlette.responses import JSONResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_openapi_spec(spec):
    """Fix common OpenAPI spec issues for FastMCP compatibility and disable output validation"""
    if not isinstance(spec, dict):
        return spec

    # Fix response codes - they should be strings, not integers
    # Also remove response schemas to disable output validation
    if "paths" in spec:
        for path_data in spec["paths"].values():
            if isinstance(path_data, dict):
                for method_data in path_data.values():
                    if isinstance(method_data, dict) and "responses" in method_data:
                        responses = method_data["responses"]
                        if isinstance(responses, dict):
                            # Convert integer response codes to strings and remove schemas
                            fixed_responses = {}
                            for code, response_data in responses.items():
                                if isinstance(response_data, dict):
                                    # Keep only description, remove schema/content for validation bypass
                                    fixed_response = {
                                        "description": response_data.get(
                                            "description", "Response"
                                        )
                                    }
                                    fixed_responses[str(code)] = fixed_response
                                else:
                                    fixed_responses[str(code)] = response_data
                            method_data["responses"] = fixed_responses

    return spec


async def load_openapi_spec():
    """Load OpenAPI spec with proper error handling"""
    try:
        logger.info(f"🔄 Loading OpenAPI specification: {settings.MARQUEZ_OPENAPI_URL}")

        async with httpx.AsyncClient() as client:
            response = await client.get(settings.MARQUEZ_OPENAPI_URL)
            response.raise_for_status()

            logger.info(
                f"✅ OpenAPI specification loaded successfully, status code: {response.status_code}"
            )

            # Check if it's YAML or JSON based on content type or URL
            content = response.text
            if settings.MARQUEZ_OPENAPI_URL.endswith(
                ".yml"
            ) or settings.MARQUEZ_OPENAPI_URL.endswith(".yaml"):
                spec = yaml.safe_load(content)
                logger.info("📋 Parsed as YAML format")
            else:
                spec = response.json()
                logger.info("📋 Parsed as JSON format")

            # Fix common compatibility issues
            fixed_spec = fix_openapi_spec(spec)
            logger.info("🔧 OpenAPI specification fix completed")
            return fixed_spec

    except httpx.RequestError as e:
        logger.error(f"❌ Failed to fetch OpenAPI specification: {e}")
        raise RuntimeError(f"Failed to fetch OpenAPI spec: {e}")
    except (yaml.YAMLError, ValueError) as e:
        logger.error(f"❌ Failed to parse OpenAPI specification: {e}")
        raise RuntimeError(f"Failed to parse OpenAPI spec: {e}")
    except Exception as e:
        logger.error(f"❌ Error processing OpenAPI specification: {e}")
        raise RuntimeError(f"Failed to parse OpenAPI spec: {e}")


class LoggingHTTPClient:
    """HTTP client wrapper for logging requests and responses"""

    def __init__(self, base_url=None):
        self.client = httpx.AsyncClient(base_url=base_url)

    async def request(self, method, url, **kwargs):
        """Send HTTP request and log detailed information"""
        # Log request information
        full_url = (
            str(self.client.base_url) + str(url) if self.client.base_url else str(url)
        )
        logger.info(f"🚀 Sending request: {method.upper()} {full_url}")

        # Log request parameters
        if kwargs.get("params"):
            logger.info(f"📋 Query parameters: {kwargs['params']}")
        if kwargs.get("json"):
            logger.info(f"📦 Request body (JSON): {kwargs['json']}")
        if kwargs.get("data"):
            logger.info(f"📦 Request body (Data): {kwargs['data']}")
        if kwargs.get("headers"):
            logger.info(f"📋 Request headers: {kwargs['headers']}")

        try:
            # Send request
            response = await self.client.request(method, url, **kwargs)

            # Log response information
            logger.info(f"✅ Response status: {response.status_code}")
            logger.info(f"📋 Response headers: {dict(response.headers)}")

            # Log response content
            try:
                response_text = response.text
                if response_text:
                    # Try to parse as JSON for formatted output
                    try:
                        import json

                        response_json = response.json()
                        logger.info(
                            f"📄 Response content (JSON): {json.dumps(response_json, indent=2, ensure_ascii=False)}"
                        )
                    except Exception:
                        # If not JSON, output text directly
                        logger.info(f"📄 Response content (Text): {response_text}")
                else:
                    logger.info("📄 Response content: (empty)")
            except Exception as e:
                logger.warning(f"⚠️ Unable to read response content: {e}")

            return response

        except Exception as e:
            logger.error(f"❌ Request failed: {e}")
            raise

    async def get(self, url, **kwargs):
        return await self.request("GET", url, **kwargs)

    async def post(self, url, **kwargs):
        return await self.request("POST", url, **kwargs)

    async def put(self, url, **kwargs):
        return await self.request("PUT", url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self.request("DELETE", url, **kwargs)

    async def patch(self, url, **kwargs):
        return await self.request("PATCH", url, **kwargs)

    async def head(self, url, **kwargs):
        return await self.request("HEAD", url, **kwargs)

    async def options(self, url, **kwargs):
        return await self.request("OPTIONS", url, **kwargs)


async def create_server():
    """Create MCP server with proper async initialization"""
    # Load OpenAPI spec
    openapi_spec = await load_openapi_spec()

    # Use configured API base URL or extract from OpenAPI spec
    base_url = getattr(settings, "MARQUEZ_API_BASE_URL", None)

    # Create HTTP client for API calls to the actual Marquez server with logging
    client = LoggingHTTPClient(base_url=base_url)

    # Create the MCP server
    mcp = FastMCP.from_openapi(
        openapi_spec=openapi_spec,
        route_maps=[RouteMap(mcp_type=MCPType.TOOL)],
        client=client,
        name="Marquez API Server",
        host="0.0.0.0",
        port=8000,
    )

    # @mcp.custom_route("/", methods=["GET"])
    # async def liveness(request: Request) -> JSONResponse:
    #     return JSONResponse({"status": "alive"}, status_code=200)

    return mcp


if __name__ == "__main__":
    transport = settings.TRANSPORT
    # transport = "stdio"

    logger.info("🚀 Starting Marquez MCP server...")
    server = asyncio.run(create_server())

    if transport == "stdio":
        logger.info("📡 Running server with stdio transport")
        server.run(transport="stdio")
    elif transport == "streamable-http":
        logger.info("🌐 Running server with Streamable HTTP transport (0.0.0.0:8000)")
        server.run(transport="streamable-http")
    else:
        logger.error(f"❌ Unknown transport method: {transport}")
        raise ValueError(f"Unknown transport: {transport}")
