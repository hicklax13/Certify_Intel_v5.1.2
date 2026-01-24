#!/usr/bin/env python3
"""
Certify Intel Backend - Entry Point for PyInstaller

This module serves as the entry point when the backend is bundled
with PyInstaller for desktop app distribution.

Usage:
    Development: python -m backend (from project root)
    Production:  certify_backend.exe (bundled executable)
"""
import sys
import os

def get_bundle_dir():
    """Get the directory where the bundled application is running from."""
    if getattr(sys, 'frozen', False):
        # Running as a PyInstaller bundle
        # sys._MEIPASS is the temp folder where PyInstaller extracts files
        return sys._MEIPASS
    else:
        # Running as a normal Python script
        return os.path.dirname(os.path.abspath(__file__))

def setup_environment():
    """Set up the environment for the backend to run correctly."""
    bundle_dir = get_bundle_dir()

    # Add bundle directory to Python path
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

    # Set working directory to bundle dir for relative file access
    os.chdir(bundle_dir)

    # Set environment variable to indicate we're running bundled
    if getattr(sys, 'frozen', False):
        os.environ['CERTIFY_BUNDLED'] = 'true'

    return bundle_dir

def main():
    """Main entry point for the Certify Intel backend."""
    bundle_dir = setup_environment()

    print(f"Certify Intel Backend Starting...")
    print(f"Bundle directory: {bundle_dir}")
    print(f"Python version: {sys.version}")
    print(f"Frozen: {getattr(sys, 'frozen', False)}")

    # Import uvicorn and the FastAPI app
    try:
        import uvicorn
        from main import app

        # Configuration for the server
        config = {
            "host": "127.0.0.1",
            "port": 8000,
            "log_level": "info",
            "access_log": True,
        }

        # In production (frozen), disable reload
        if not getattr(sys, 'frozen', False):
            config["reload"] = True

        print(f"Starting server on http://{config['host']}:{config['port']}")

        # Run the server
        uvicorn.run(app, **config)

    except ImportError as e:
        print(f"Error importing dependencies: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
