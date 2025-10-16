"""
AWS Strands True Multi-Agent System Main Entry
"""

import os
import sys

from core.multi_agent_system import TrueMultiAgentSystem
from i18n import t
from utils.config_validator import ConfigValidator

# Add necessary paths
sys.path.insert(0, os.path.dirname(__file__))


def main():
    """Main function"""
    try:
        # Validate configuration
        is_valid, missing_configs = ConfigValidator.validate_config()
        if not is_valid:
            return

        # Start system
        system = TrueMultiAgentSystem()
        system.run()

    except ImportError as e:
        print(t("errors.import_error", error=str(e)))
        print(t("errors.install_dependencies"))
    except Exception as e:
        print(t("errors.startup_failed", error=str(e)))
        print(t("errors.check_config"))


if __name__ == "__main__":
    main()
