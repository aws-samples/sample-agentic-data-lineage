#!/usr/bin/env python3
"""
Streamlit Web Interface Startup Script
Intelligent Data Lineage Analysis System - Web Interface
"""
import os
import subprocess
import sys

# Add src directory to Python path to support internationalization
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def main():
    """Start Streamlit application"""
    # Default to Chinese, can also be set via environment variable
    language = os.environ.get("LANGUAGE", "zh")

    try:
        from i18n import Translator

        translator = Translator(language)
        t = translator.t
    except ImportError:
        # If internationalization module is not available, use default Chinese text
        def t(key, **kwargs):
            fallback_texts = {
                "app.starting": "🚀 启动 Agentic Lineage For Lakehouse (Web界面)",
                "app.access_url": "📍 访问地址: http://localhost:8504",
                "app.web_interface": "🌐 ChatGPT风格的Web界面",
                "app.multi_agent": "🤖 支持多代理协作",
                "app.stopped": "👋 应用已停止",
                "app.start_failed": "❌ 启动失败: {error}",
            }
            return fallback_texts.get(key, key).format(**kwargs)

    print(t("app.starting"))
    print("=" * 60)
    print(t("app.access_url"))
    print(t("app.web_interface"))
    print(t("app.multi_agent"))
    print("=" * 60)

    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(os.path.dirname(__file__), "src")

    # Set environment configuration
    # Local development environment, set environment variable for EKS: ENV_FOR_DYNACONF=development
    if not env.get("ENV_FOR_DYNACONF"):
        env["ENV_FOR_DYNACONF"] = "local"

    # Start Streamlit application
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/streamlit_app_wrapper.py",
        "--server.port=8504",
        "--server.headless=true",
        "--browser.gatherUsageStats=false",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
    ]

    try:
        subprocess.run(cmd, env=env, check=True)
    except KeyboardInterrupt:
        print(f"\n{t('app.stopped')}")
    except Exception as e:
        print(t("app.start_failed", error=str(e)))
        sys.exit(1)


if __name__ == "__main__":
    main()
