"""
Configuration Validator - Responsible for validating system configuration
"""

from config import settings


class ConfigValidator:
    """Configuration validator"""

    @staticmethod
    def validate_config() -> tuple[bool, list]:
        """Validate system configuration

        Returns:
            tuple: (validation passed, list of missing configurations)
        """
        print("🔧 Checking system configuration...")

        required_configs = ["MARQUEZ_MCP_URL", "BEDROCK_MODEL_ID"]

        missing_configs = []
        for config in required_configs:
            if not hasattr(settings, config) or not getattr(settings, config):
                missing_configs.append(config)

        if missing_configs:
            print(f"❌ Missing required configurations: {', '.join(missing_configs)}")
            print("Please check config/settings.toml file")
            return False, missing_configs

        print("✅ Configuration check passed")
        return True, []
