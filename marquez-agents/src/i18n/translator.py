"""
Translator module for internationalization
"""

import json
import os

import streamlit as st


class Translator:
    """Translator class"""

    def __init__(self, language: str = "zh"):
        self.language = language
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        """Load translation files"""
        translations_dir = os.path.join(os.path.dirname(__file__), "translations")
        translation_file = os.path.join(translations_dir, f"{self.language}.json")

        if os.path.exists(translation_file):
            with open(translation_file, encoding="utf-8") as f:
                self.translations = json.load(f)
        else:
            # If translation file doesn't exist, use default empty translations
            self.translations = {}

    def t(self, key: str, **kwargs) -> str:
        """
        Translation function
        Args:
            key: Translation key
            **kwargs: Format parameters
        Returns:
            Translated text
        """
        # Support nested keys like "ui.header.title"
        keys = key.split(".")
        value = self.translations

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                # If translation not found, return the key itself
                return key

        if isinstance(value, str):
            try:
                return value.format(**kwargs)
            except (KeyError, ValueError):
                return value
        else:
            return key

    def set_language(self, language: str):
        """Set language"""
        self.language = language
        self.load_translations()


# Global translator instance
_translator = None


def get_translator() -> Translator:
    """Get translator instance"""
    global _translator

    # Get language setting from Streamlit session state
    if hasattr(st, "session_state") and "language" in st.session_state:
        language = st.session_state.language
    else:
        # Try to get from language manager
        try:
            from utils.language_manager import LanguageManager

            language_manager = LanguageManager()
            language = language_manager.get_language()
        except ImportError:
            language = "zh"  # Default to Chinese

    if _translator is None or _translator.language != language:
        _translator = Translator(language)

    return _translator


def t(key: str, **kwargs) -> str:
    """Convenient translation function"""
    return get_translator().t(key, **kwargs)
