"""
Streamlit Application Wrapper - Handle context setup and system initialization
"""

import os
import sys

import streamlit as st
from core.multi_agent_system import TrueMultiAgentSystem
from i18n import t
from ui.streamlit_ui import StreamlitUI
from utils.streamlit_context import StreamlitContext
from utils.warning_suppressor import WarningSupressor

# Add src directory to Python path
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


class StreamlitAppWrapper:
    """Streamlit Application Wrapper"""

    def __init__(self):
        # Set Streamlit context
        StreamlitContext.set_in_streamlit_context(True)

        # Suppress unnecessary Streamlit warnings
        WarningSupressor.suppress_streamlit_warnings()

        # Initialize interface
        self.interface = StreamlitUI()

        # Initialize system state
        self.initialize_system()

    def initialize_system(self):
        """Initialize multi-agent system"""
        if not st.session_state.system_initialized:
            try:
                with st.spinner(t("system.initializing")):
                    # Get current language setting
                    current_language = getattr(st.session_state, "language", "zh")

                    # Create multi-agent system (non-CLI mode)
                    system = TrueMultiAgentSystem(
                        use_cli_interface=False, language=current_language
                    )

                    # Save to session state
                    st.session_state.agents = system.agents
                    st.session_state.system = system
                    st.session_state.system_initialized = True

                    # Initialize tool call history
                    if "tool_calls" not in st.session_state:
                        st.session_state.tool_calls = []

                    # Use session state to persist success message
                    st.session_state.init_success = True

            except Exception as e:
                st.error(t("system.init_failed", error=str(e)))
                st.session_state.system_initialized = False

    def run(self):
        """Run Streamlit application"""
        # Show page header
        self.interface.show_header()

        # Show sidebar
        self.interface.show_sidebar()

        # Show chat interface
        self.interface.show_chat_interface()

        # Show help section
        self.interface.show_help_section()


def main():
    """Main function"""
    app = StreamlitAppWrapper()
    app.run()


if __name__ == "__main__":
    main()
