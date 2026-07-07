#!/usr/bin/env python3
"""
Google API key management for seo-agents.

Loads and validates the API key used by the PageSpeed Insights and CrUX
clients (pagespeed_check.py, crux_history.py). Reads the config file first,
falls back to environment variables.

Usage:
    python google_auth.py --check    # Check whether an API key is configured
    python google_auth.py --setup    # Show setup instructions
"""

import argparse
import json
import os
import sys
from typing import Optional

CONFIG_PATH = os.path.expanduser("~/.config/seo-agents/google-api.json")


def load_config() -> dict:
    """
    Load configuration from the config file with environment fallbacks.

    Reads ~/.config/seo-agents/google-api.json first; a missing api_key is
    filled from the GOOGLE_API_KEY environment variable.

    Returns:
        Dictionary with at least the key ``api_key`` (None if unconfigured).
    """
    config = {"api_key": None}

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                file_config = json.load(f)
            config.update({k: v for k, v in file_config.items() if v})
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not read config file: {e}", file=sys.stderr)

    if not config["api_key"]:
        config["api_key"] = os.environ.get("GOOGLE_API_KEY")

    return config


def get_api_key() -> Optional[str]:
    """
    Get the Google API key from config or environment.

    Returns:
        API key string, or None if not configured.
    """
    return load_config().get("api_key")


def validate_url(url: str) -> bool:
    """
    Validate a URL for use with Google APIs. Rejects private/loopback addresses.

    Back-compat wrapper around :func:`url_safety.validate_url`. The shared
    module is the canonical implementation and adds DNS-rebinding-safe
    helpers (``validate_url_strict``, ``safe_requests_get``) that
    ``fetch_page.py`` and ``render_page.py`` use before opening sockets.
    """
    # Lazy import keeps the import graph one-directional.
    _scripts_dir = os.path.dirname(os.path.abspath(__file__))
    if _scripts_dir not in sys.path:
        sys.path.insert(0, _scripts_dir)
    from url_safety import validate_url as _validate_url

    return _validate_url(url)


SETUP_INSTRUCTIONS = f"""\
Google API key setup (needed only for pagespeed_check.py / crux_history.py)

1. Create a key in Google Cloud Console:
   https://console.cloud.google.com/apis/credentials
   Enable "PageSpeed Insights API" and "Chrome UX Report API" for the project.

2. Save it either as an environment variable:
   export GOOGLE_API_KEY="your-key"

   ...or in the config file:
   mkdir -p ~/.config/seo-agents
   Save to {CONFIG_PATH}:
   {{"api_key": "your-key"}}
"""


def main():
    parser = argparse.ArgumentParser(description="Google API key management for seo-agents")
    parser.add_argument("--check", action="store_true", help="Check whether an API key is configured")
    parser.add_argument("--setup", action="store_true", help="Show setup instructions")
    parser.add_argument("--json", action="store_true", help="JSON output for --check")
    args = parser.parse_args()

    if args.setup:
        print(SETUP_INSTRUCTIONS)
        return

    key = get_api_key()
    if args.json:
        print(json.dumps({"api_key_configured": bool(key), "config_path": CONFIG_PATH}))
    elif key:
        print(f"API key configured ({'config file' if os.path.exists(CONFIG_PATH) else 'environment'}).")
    else:
        print("No API key found. Run with --setup for instructions.")
        sys.exit(1)


if __name__ == "__main__":
    main()
