"""
Streamlit UI Manager - Unified interface with internationalization support
"""

from datetime import datetime

import streamlit as st
from i18n import t

try:
    from utils.language_manager import LanguageManager
except ImportError:
    LanguageManager = None


class StreamlitUI:
    """Unified Streamlit UI Manager"""

    def __init__(self):
        self.initialize_session_state()
        self.setup_page_config()

    def initialize_session_state(self):
        """Initialize session state"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "current_agent" not in st.session_state:
            st.session_state.current_agent = "orchestrator"
        if "system_initialized" not in st.session_state:
            st.session_state.system_initialized = False
        if "agents" not in st.session_state:
            st.session_state.agents = {}
        if "init_success_count" not in st.session_state:
            st.session_state.init_success_count = 0
        if "language" not in st.session_state:
            # Get saved language setting from language manager
            if LanguageManager is not None:
                try:
                    language_manager = LanguageManager()
                    st.session_state.language = language_manager.get_language()
                except Exception:
                    st.session_state.language = "zh"  # Default to Chinese
            else:
                st.session_state.language = "zh"  # Default to Chinese

    def setup_page_config(self):
        """Setup page configuration and styles"""
        # Add custom CSS styles
        st.markdown(
            """
        <style>
        /* Hide top-right menu and toolbar */
        #MainMenu {visibility: hidden !important;}
        .stDeployButton {display: none !important;}
        .stDecoration {display: none !important;}
        header[data-testid="stHeader"] {display: none !important;}
        .stToolbar {display: none !important;}

        /* Hide footer */
        footer {visibility: hidden !important;}

        /* Hide "Made with Streamlit" */
        .viewerBadge_container__1QSob {display: none !important;}

        /* Optimize main container */
        .main .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            max-width: 100%;
        }

        /* Reduce container spacing */
        .element-container {
            margin-bottom: 0.5rem !important;
        }

        /* Reduce title spacing */
        h1 {
            margin-bottom: 1rem !important;
        }

        /* Chat message styles */
        .stChatMessage {
            margin-bottom: 1rem;
            border-radius: 10px;
        }

        /* Optimize sidebar */
        .css-1d391kg {
            padding-top: 2rem;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

    def show_header(self):
        """Show page header"""
        # Deploy button and settings button styles are already set in setup_page_config

        # Show title (optimized display)
        st.title("🏛️ Agentic Lineage")
        st.markdown("**For Lakehouse**")
        st.markdown(t("app.subtitle"))

        # Only show success message during initialization
        if hasattr(st.session_state, "init_success") and st.session_state.init_success:
            # Show initialization success message
            st.success(t("system.init_success"))
            st.session_state.init_success = False

        # Show language update success message
        if (
            hasattr(st.session_state, "language_update_success")
            and st.session_state.language_update_success
        ):
            st.success(t("agents.language_updated"))
            st.session_state.language_update_success = False

        st.divider()

    def show_sidebar(self):
        """Show sidebar"""
        with st.sidebar:
            # Language selector
            st.subheader(t("ui.language_selector"))
            language = st.selectbox(
                "选择语言 / Select Language",
                options=["zh", "en"],
                format_func=lambda x: "🇨🇳 中文" if x == "zh" else "🇺🇸 English",
                index=0 if st.session_state.language == "zh" else 1,
                key="language_selector",
                label_visibility="collapsed",  # Hide label since we already have subheader
            )
            if language != st.session_state.language:
                st.session_state.language = language
                # Save language selection
                if LanguageManager is not None:
                    try:
                        language_manager = LanguageManager()
                        language_manager.set_language(language)
                    except Exception:
                        pass

                # Update agent system language settings
                if hasattr(st.session_state, "system") and st.session_state.system:
                    try:
                        with st.spinner(t("system.initializing")):
                            st.session_state.system.set_language(language)
                            st.session_state.agents = st.session_state.system.agents
                        # Show success message
                        st.session_state.language_update_success = True
                    except Exception as e:
                        st.error(t("agents.language_update_failed") + f": {e}")

                st.rerun()

            st.divider()
            st.header(t("ui.system_status"))

            # Show system running status
            if st.session_state.system_initialized:
                st.success(t("system.running"))
                st.info(t("system.agent_count", count=len(st.session_state.agents)))
            else:
                st.warning(t("system.initializing_status"))

            # Show current active agent and tool calls
            if (
                hasattr(st.session_state, "current_active_agent")
                and st.session_state.current_active_agent
            ):
                st.info(
                    t(
                        "system.current_agent",
                        agent=self.get_agent_display_name(
                            st.session_state.current_active_agent
                        ),
                    )
                )

            if (
                hasattr(st.session_state, "current_thinking")
                and st.session_state.current_thinking
            ):
                st.info(t("system.status", status=st.session_state.current_thinking))

            # Show recent tool calls
            if hasattr(st.session_state, "tool_calls") and st.session_state.tool_calls:
                st.divider()
                st.subheader(t("ui.tool_calls_history"))
                # Only show recent 5 tool calls
                recent_calls = st.session_state.tool_calls[-5:]
                for call in reversed(recent_calls):
                    st.caption(
                        f"[{call.get('timestamp', '')}] {call.get('tool_name', '')} -> {self.get_agent_display_name(call.get('agent_name', ''))}"
                    )

            st.divider()

            # Action buttons
            if st.button(t("ui.clear_chat"), key="clear_chat"):
                st.session_state.messages = []
                if hasattr(st.session_state, "tool_calls"):
                    st.session_state.tool_calls = []
                st.rerun()

            if st.button(t("ui.reinit_system"), key="reinit_system"):
                st.session_state.system_initialized = False
                st.session_state.agents = {}
                st.session_state.messages = []
                if hasattr(st.session_state, "tool_calls"):
                    st.session_state.tool_calls = []
                st.rerun()

    def show_chat_interface(self):
        """Show chat interface"""
        # If no messages, show welcome message
        if not st.session_state.messages:
            self.show_welcome_message()

        # Show chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "timestamp" in message:
                    st.caption(t("ui.timestamp", time=message["timestamp"]))

        # Chat input
        if prompt := st.chat_input(t("ui.chat_input_placeholder")):
            self.handle_user_input(prompt)

    def handle_user_input(self, prompt: str):
        """Handle user input"""
        # Add user message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append(
            {"role": "user", "content": prompt, "timestamp": timestamp}
        )

        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(t("ui.timestamp", time=timestamp))

        # Process agent response
        if st.session_state.system_initialized and st.session_state.agents:
            self.process_agent_response(prompt)
        else:
            with st.chat_message("assistant"):
                st.error(t("system.not_initialized"))

    def process_agent_response(self, prompt: str):
        """Process agent response"""
        # Use orchestrator agent (fixed)
        current_agent = "orchestrator"
        agent_name = self.get_agent_display_name(current_agent)

        # Show thinking status
        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()
            thinking_placeholder.info(t("ui.thinking", agent=agent_name))

            try:
                # Call agent
                agent = st.session_state.agents[current_agent]
                response = agent(prompt)

                # Handle AgentResult object
                if hasattr(response, "content"):
                    content = response.content
                elif hasattr(response, "text"):
                    content = response.text
                else:
                    content = str(response)

                # Clear thinking status, show response
                thinking_placeholder.empty()
                st.success(t("ui.agent_reply", agent=agent_name))
                st.markdown(content)

                # Add to message history
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"{t('ui.agent_reply_label', agent=agent_name)}\n\n{content}",
                        "timestamp": timestamp,
                    }
                )

            except Exception as e:
                thinking_placeholder.empty()
                st.error(t("ui.processing_error", error=str(e)))
                st.caption(t("ui.retry_message"))

    def show_welcome_message(self):
        """Show welcome message"""
        if st.session_state.language == "en":
            welcome_text = """
            👋 **Welcome to Agentic Lineage For Lakehouse!**

            This is a true multi-agent architecture where each agent is an independent Agent instance:

            - 🎯 **Orchestrator Agent**: Automatically routes requests to appropriate specialized agents
            - 📊 **Metadata Agent**: Statistics of assets and jobs (via MCP tools)
            - 📈 **Lineage Agent**: Query field lineage sources (via MCP tools)
            - 🗂️ **Data Catalog Agent**: Query AWS Glue and Redshift data catalogs
            - 🔍 **Specialist Agent**: Generate data health reports

            **Example Functions:**
            - Query namespaces: How many namespaces are in Marquez?
            - Query field lineage: Please query the lineage source of field user_id
            - Impact analysis: Analyze the impact of field changes
            - Generate reports: Generate data health report

            Please enter your question below to start the conversation!
            """
        else:
            welcome_text = """
            👋 **欢迎使用 Agentic Lineage For Lakehouse！**

            这是一个真正的多代理架构，每个代理都是独立的Agent实例：

            - 🎯 **协调器代理**: 自动路由请求到合适的专业代理
            - 📊 **元数据代理**: 统计资产和作业数量（通过MCP工具）
            - 📈 **血缘代理**: 查询字段血缘来源（通过MCP工具）
            - 🗂️ **数据目录代理**: 查询AWS Glue和Redshift数据目录
            - 🔍 **专家代理**: 生成血缘健康报告

            **功能示例：**
            - 查询命名空间：marquez有多少命名空间？
            - 查询字段血缘：请查询字段 user_id 的血缘来源
            - 影响分析：分析字段变更的影响
            - 生成报告：生成血缘健康报告

            请在下方输入您的问题开始对话！
            """

        st.info(welcome_text)

    def show_help_section(self):
        """Show help section"""
        # Don't show help section, keep interface clean

    def get_agent_display_name(self, agent_key: str) -> str:
        """Get agent display name"""
        return t(f"agents.{agent_key}")
