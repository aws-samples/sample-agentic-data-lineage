"""
Streamlit Context Manager - Handles Streamlit environment detection and state management
"""

import threading
from typing import Any


class StreamlitContext:
    """Streamlit Context Manager"""

    _local = threading.local()

    @classmethod
    def is_streamlit_available(cls) -> bool:
        """Check if running in Streamlit environment"""
        try:
            import streamlit as st

            # Check if there's an active Streamlit session
            return hasattr(st, "session_state") and st.session_state is not None
        except Exception:
            return False

    @classmethod
    def safe_session_state_access(cls, key: str, default: Any = None) -> Any:
        """Safely access Streamlit session state"""
        if not cls.is_streamlit_available():
            return default

        try:
            import streamlit as st

            return getattr(st.session_state, key, default)
        except Exception:
            return default

    @classmethod
    def safe_session_state_set(cls, key: str, value: Any) -> bool:
        """Safely set Streamlit session state"""
        if not cls.is_streamlit_available():
            return False

        try:
            import streamlit as st

            setattr(st.session_state, key, value)
            return True
        except Exception:
            return False

    @classmethod
    def update_agent_status(cls, agent_name: str, status: str, timestamp: str = None):
        """Update agent status (only in Streamlit environment)"""
        if not cls.is_streamlit_available():
            return

        try:
            from datetime import datetime

            import streamlit as st

            if not hasattr(st.session_state, "tool_calls"):
                st.session_state.tool_calls = []

            st.session_state.current_active_agent = agent_name
            st.session_state.current_thinking = status

            if timestamp is None:
                timestamp = datetime.now().strftime("%H:%M:%S")

            st.session_state.tool_calls.append(
                {
                    "tool_name": f"call_{agent_name}_agent",
                    "agent_name": agent_name,
                    "timestamp": timestamp,
                    "status": status,
                }
            )
        except Exception:
            # Silent failure, doesn't affect main functionality
            pass

    @classmethod
    def set_in_streamlit_context(cls, value: bool = True):
        """Set whether current thread is in Streamlit context"""
        cls._local.in_streamlit = value

    @classmethod
    def is_in_streamlit_context(cls) -> bool:
        """Check if current thread is in Streamlit context"""
        return getattr(cls._local, "in_streamlit", False)
