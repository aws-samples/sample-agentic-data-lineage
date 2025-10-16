"""
Agent Factory Class - Responsible for creating various independent Agent instances
"""

from config import settings
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from utils.streamlit_context import StreamlitContext
from utils.time_tools import TIME_TOOLS

from .prompts.datacatalog_agent import (
    DATACATALOG_AGENT_PROMPT_EN,
    DATACATALOG_AGENT_PROMPT_ZH,
)
from .prompts.lineage_agent import LINEAGE_AGENT_PROMPT_EN, LINEAGE_AGENT_PROMPT_ZH

# Import prompts for each agent
from .prompts.metadata_agent import METADATA_AGENT_PROMPT_EN, METADATA_AGENT_PROMPT_ZH
from .prompts.orchestrator_agent import (
    ORCHESTRATOR_AGENT_PROMPT_EN,
    ORCHESTRATOR_AGENT_PROMPT_ZH,
)
from .prompts.specialist_agent import (
    SPECIALIST_AGENT_PROMPT_EN,
    SPECIALIST_AGENT_PROMPT_ZH,
)


class AgentFactory:
    """Agent Factory Class"""

    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self.current_language = "zh"  # Default to Chinese

    def set_language(self, language: str):
        """Set current language"""
        self.current_language = language

    def get_language_instruction(self) -> str:
        """Get language instruction"""
        if self.current_language == "en":
            return "Please respond in English."
        else:
            return "用中文回复用户。"

    def create_metadata_agent(self) -> Agent:
        """Create independent metadata agent"""
        # Get MCP tools (using shared MCP client)
        mcp_tools = self.mcp_client.list_tools_sync()

        # Merge MCP tools and time tools
        all_tools = mcp_tools + TIME_TOOLS

        if self.current_language == "en":
            system_prompt = METADATA_AGENT_PROMPT_EN
        else:
            system_prompt = METADATA_AGENT_PROMPT_ZH

        # Create Agent
        agent = Agent(
            tools=all_tools,
            model=BedrockModel(
                model_id=settings.get("BEDROCK_MODEL_ID"),
                max_tokens=settings.get("BEDROCK_MAX_TOKENS", 4000),
            ),
            system_prompt=system_prompt,
        )

        return agent

    def create_datacatalog_agent(self) -> Agent:
        """Create independent data catalog agent"""
        from utils.datacatalog_tools import DATACATALOG_TOOLS

        if self.current_language == "en":
            system_prompt = DATACATALOG_AGENT_PROMPT_EN
        else:
            system_prompt = DATACATALOG_AGENT_PROMPT_ZH

        # Create Agent
        agent = Agent(
            tools=DATACATALOG_TOOLS,
            model=BedrockModel(
                model_id=settings.get("BEDROCK_MODEL_ID"),
                max_tokens=settings.get("BEDROCK_MAX_TOKENS", 4000),
            ),
            system_prompt=system_prompt,
        )

        return agent

    def create_lineage_agent(self) -> Agent:
        """Create independent lineage agent"""
        # Get MCP tools (using shared MCP client)
        mcp_tools = self.mcp_client.list_tools_sync()

        # Merge MCP tools and time tools
        all_tools = mcp_tools + TIME_TOOLS

        if self.current_language == "en":
            system_prompt = LINEAGE_AGENT_PROMPT_EN
        else:
            system_prompt = LINEAGE_AGENT_PROMPT_ZH

        # Create Agent
        agent = Agent(
            tools=all_tools,
            model=BedrockModel(
                model_id=settings.get("BEDROCK_MODEL_ID"),
                max_tokens=settings.get("BEDROCK_MAX_TOKENS", 4000),
            ),
            system_prompt=system_prompt,
        )

        return agent

    def create_specialist_agent(self) -> Agent:
        """Create independent specialist agent"""

        if self.current_language == "en":
            system_prompt = SPECIALIST_AGENT_PROMPT_EN
        else:
            system_prompt = SPECIALIST_AGENT_PROMPT_ZH

        return Agent(
            tools=TIME_TOOLS,
            model=BedrockModel(
                model_id=settings.get("BEDROCK_MODEL_ID"),
                max_tokens=settings.get("BEDROCK_MAX_TOKENS", 4000),
            ),
            system_prompt=system_prompt,
        )

    def create_orchestrator_agent(self, agents_dict: dict) -> Agent:
        """Create independent orchestrator agent"""

        @tool
        def call_metadata_agent(query: str) -> str:
            """Call metadata agent"""
            try:
                # Update interface status (only in Streamlit environment)
                StreamlitContext.update_agent_status(
                    "metadata", "Metadata agent is processing query..."
                )

                result = agents_dict["metadata"](query)
                return f"Metadata agent reply:\n{result}"
            except Exception as e:
                return f"Failed to call metadata agent: {str(e)}"

        @tool
        def call_lineage_agent(query: str) -> str:
            """Call lineage agent"""
            try:
                # Update interface status (only in Streamlit environment)
                StreamlitContext.update_agent_status(
                    "lineage", "Lineage agent is analyzing data lineage..."
                )

                result = agents_dict["lineage"](query)
                return f"Lineage agent reply:\n{result}"
            except Exception as e:
                return f"Failed to call lineage agent: {str(e)}"

        @tool
        def call_specialist_agent(query: str) -> str:
            """Call specialist agent"""
            try:
                # Update interface status (only in Streamlit environment)
                StreamlitContext.update_agent_status(
                    "specialist", "Specialist agent is generating analysis report..."
                )

                result = agents_dict["specialist"](query)
                return f"Specialist agent reply:\n{result}"
            except Exception as e:
                return f"Failed to call specialist agent: {str(e)}"

        @tool
        def call_datacatalog_agent(query: str) -> str:
            """Call data catalog agent"""
            try:
                # Update interface status (only in Streamlit environment)
                StreamlitContext.update_agent_status(
                    "datacatalog", "Data catalog agent is querying data catalog..."
                )

                result = agents_dict["datacatalog"](query)
                return f"Data catalog agent reply:\n{result}"
            except Exception as e:
                return f"Failed to call data catalog agent: {str(e)}"

        if self.current_language == "en":
            system_prompt = ORCHESTRATOR_AGENT_PROMPT_EN
        else:
            system_prompt = ORCHESTRATOR_AGENT_PROMPT_ZH

        return Agent(
            tools=[
                call_metadata_agent,
                call_lineage_agent,
                call_specialist_agent,
                call_datacatalog_agent,
            ],
            model=BedrockModel(
                model_id=settings.get("BEDROCK_MODEL_ID"),
                max_tokens=settings.get("BEDROCK_MAX_TOKENS", 4000),
            ),
            system_prompt=system_prompt,
        )
