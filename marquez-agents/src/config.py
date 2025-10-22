"""
Dynaconf Configuration Module
"""

from pathlib import Path

from dynaconf import Dynaconf

# Get project root directory
project_root = Path(__file__).parent.parent
config_dir = project_root / "config"

# Initialize dynaconf settings
settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=[
        str(config_dir / "settings.toml"),
        str(config_dir / "settings.local.toml"),
        str(config_dir / "settings.development.toml"),
        str(config_dir / ".secrets.toml"),
    ],
    environments=True,
    load_dotenv=True,
    env_switcher="ENV_FOR_DYNACONF",
)
