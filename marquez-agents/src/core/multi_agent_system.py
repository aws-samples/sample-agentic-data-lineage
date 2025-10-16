"""
AWS Strands True Multi-Agent System Core Class
True multi-agent architecture implementation
"""

from agents.agent_factory import AgentFactory
from config import settings
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp.mcp_client import MCPClient
from ui.interface_manager import InterfaceManager
from utils.warning_suppressor import WarningSupressor


class TrueMultiAgentSystem:
    """True multi-agent system"""

    def __init__(self, use_cli_interface=True, language="zh"):
        # Suppress Streamlit warnings (if not in Streamlit environment)
        if not use_cli_interface:
            WarningSupressor.suppress_streamlit_warnings()

        self.agents = {}
        self.mcp_client = None
        self.use_cli_interface = use_cli_interface
        self.current_language = language

        if use_cli_interface:
            self.interface = InterfaceManager()

        self._initialize_mcp_client()
        self._initialize_agents()

        if use_cli_interface:
            print("🚀 Agentic Lineage For Lakehouse started")
            print("=" * 60)
            self.interface.show_welcome_message()

    def _initialize_mcp_client(self):
        """Initialize MCP client"""
        self.mcp_client = MCPClient(
            lambda: streamablehttp_client(settings.MARQUEZ_MCP_URL)
        )
        # Start MCP client connection
        self.mcp_client.__enter__()

    def _initialize_agents(self):
        """Initialize all independent Agent instances"""
        factory = AgentFactory(self.mcp_client)
        factory.set_language(self.current_language)

        # 1. Create specialized agents
        metadata_agent = factory.create_metadata_agent()
        lineage_agent = factory.create_lineage_agent()
        specialist_agent = factory.create_specialist_agent()
        datacatalog_agent = factory.create_datacatalog_agent()

        # 2. Create agent dictionary (orchestrator needs to reference other agents)
        self.agents = {
            "metadata": metadata_agent,
            "lineage": lineage_agent,
            "specialist": specialist_agent,
            "datacatalog": datacatalog_agent,
        }

        # 3. Create orchestrator agent (needs access to other agents)
        orchestrator_agent = factory.create_orchestrator_agent(self.agents)
        self.agents["orchestrator"] = orchestrator_agent

    def set_language(self, language: str):
        """Set language and reinitialize agents"""
        if language != self.current_language:
            self.current_language = language
            self._initialize_agents()  # Recreate agents to use new language

    def run(self):
        """Run interactive system (CLI mode only)"""
        if not self.use_cli_interface:
            raise RuntimeError("run() method is only available in CLI mode")

        current_agent = "orchestrator"

        while True:
            try:
                agent_name = self.interface.get_agent_display_name(current_agent)
                user_input = self.interface.get_user_input(agent_name)

                if not user_input:
                    continue

                # Handle system commands
                if user_input.lower() in ["quit", "exit", "退出"]:
                    self.interface.show_goodbye()
                    break

                elif user_input.lower() in ["help", "帮助"]:
                    self.interface.show_help()
                    continue

                elif user_input.lower() in ["agents", "代理"]:
                    self.interface.show_agents_status(self.agents)
                    continue

                elif user_input.lower().startswith("switch "):
                    agent_name_input = user_input[7:].strip()
                    if agent_name_input in self.agents:
                        current_agent = agent_name_input
                        self.interface.show_switch_success(agent_name_input)
                    else:
                        self.interface.show_switch_error(
                            agent_name_input, list(self.agents.keys())
                        )
                    continue

                # Handle user questions
                self.interface.show_thinking(agent_name)

                try:
                    response = self.agents[current_agent](user_input)
                    self.interface.show_response(agent_name, response)

                except Exception as e:
                    self.interface.show_error(str(e))

            except KeyboardInterrupt:
                self.interface.show_goodbye()
                break
            except Exception as e:
                self.interface.show_system_error(str(e))

        # Clean up resources
        self.cleanup()

    def query_agent(self, agent_name: str, query: str) -> str:
        """Query specified agent (for API calls)"""
        if agent_name not in self.agents:
            raise ValueError(
                f"Agent '{agent_name}' not found. Available agents: {list(self.agents.keys())}"
            )

        try:
            return self.agents[agent_name](query)
        except Exception as e:
            raise RuntimeError(f"Error querying agent '{agent_name}': {str(e)}") from e

    def cleanup(self):
        """Clean up resources"""
        if self.mcp_client:
            try:
                self.mcp_client.__exit__(None, None, None)
            except Exception:
                pass
