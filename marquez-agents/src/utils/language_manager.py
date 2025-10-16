"""
Language Manager for handling language preferences
"""

import json
import os


class LanguageManager:
    """Language Manager class"""

    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), "..", "..", "config")
        self.config_file = os.path.join(self.config_dir, "language.json")
        self.ensure_config_dir()

    def ensure_config_dir(self):
        """Ensure configuration directory exists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

    def get_language(self) -> str:
        """Get current language setting"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("language", "zh")
        except Exception:
            pass
        return "zh"  # Default to Chinese

    def set_language(self, language: str):
        """Set language"""
        try:
            config = {"language": language}
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save language preference: {e}")

    def get_supported_languages(self) -> dict:
        """Get supported languages list"""
        return {"zh": "中文", "en": "English"}
