"""
Warning Suppressor - Suppress Streamlit-related warnings
"""

import logging
import sys
from contextlib import contextmanager


class StreamlitWarningFilter(logging.Filter):
    """Log filter for filtering Streamlit-related warnings"""

    def filter(self, record):
        # Filter out Streamlit-related warnings
        if hasattr(record, "name"):
            if "streamlit" in record.name.lower():
                if "missing ScriptRunContext" in record.getMessage():
                    return False
                if "Session state does not function" in record.getMessage():
                    return False
        return True


class WarningSupressor:
    """Warning Suppressor"""

    @staticmethod
    def suppress_streamlit_warnings():
        """Suppress Streamlit-related warnings"""
        # Add log filter
        streamlit_filter = StreamlitWarningFilter()

        # Get all related loggers
        loggers_to_filter = [
            "streamlit.runtime.scriptrunner_utils.script_run_context",
            "streamlit.runtime.state.session_state_proxy",
            "streamlit",
            "root",
        ]

        for logger_name in loggers_to_filter:
            logger = logging.getLogger(logger_name)
            logger.addFilter(streamlit_filter)
            # Set log level to ERROR, filter WARNING
            logger.setLevel(logging.ERROR)

    @staticmethod
    def suppress_all_streamlit_warnings():
        """Completely suppress Streamlit warnings"""
        # Redirect stderr to capture warnings
        import io

        # Create a filter to ignore Streamlit warnings
        class StreamlitWarningFilter:
            def __init__(self, original_stderr):
                self.original_stderr = original_stderr
                self.buffer = io.StringIO()

            def write(self, text):
                # If not a Streamlit warning, write to original stderr
                if not any(
                    keyword in text
                    for keyword in [
                        "missing ScriptRunContext",
                        "Session state does not function",
                        "streamlit.runtime",
                    ]
                ):
                    self.original_stderr.write(text)
                return len(text)

            def flush(self):
                self.original_stderr.flush()

        # Apply filter
        sys.stderr = StreamlitWarningFilter(sys.stderr)


@contextmanager
def suppress_streamlit_warnings():
    """Context manager: temporarily suppress Streamlit warnings"""
    # Save original stderr
    original_stderr = sys.stderr

    # Create filter
    class FilteredStderr:
        def __init__(self, original):
            self.original = original

        def write(self, text):
            # Filter Streamlit warnings
            if not any(
                keyword in text
                for keyword in [
                    "missing ScriptRunContext",
                    "Session state does not function",
                    "streamlit.runtime",
                ]
            ):
                self.original.write(text)
            return len(text)

        def flush(self):
            self.original.flush()

        def __getattr__(self, name):
            return getattr(self.original, name)

    try:
        # Apply filter
        sys.stderr = FilteredStderr(original_stderr)
        WarningSupressor.suppress_streamlit_warnings()
        yield
    finally:
        # Restore original stderr
        sys.stderr = original_stderr
