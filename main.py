import logging
from typing import Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables at the very beginning
dotenv_path = Path(__file__).parent / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
    print(f"Loaded environment variables from {dotenv_path}")
else:
    print(f"Environment file not found at {dotenv_path}")

# Configure logging
# logging.basicConfig(
#     level=print,
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# Deferred import to prevent circular references


def get_app():
    print("LAMBDA DEBUG: Starting app initialization")
    try:
        from src.app import create_app
        print("LAMBDA DEBUG: Successfully imported create_app")
        app = create_app()
        print("LAMBDA DEBUG: App created successfully")
        return app
    except Exception as e:
        print(f"LAMBDA DEBUG: Error initializing app: {str(e)}")
        raise


# Initialize application lazily when needed
app = None


def lambda_handler(event: Dict[str, Any], context: Any) -> None:
    print("LAMBDA DEBUG: Lambda handler started")
    global app
    if app is None:
        print("LAMBDA DEBUG: App not initialized, initializing now")
        app = get_app()
        print("LAMBDA DEBUG: App initialization completed")

    print(f"LAMBDA DEBUG: Processing event: {event}")
    try:
        for record in event['Records']:
            app.handle(record, context)
        print("LAMBDA DEBUG: Event handling completed successfully")
    except Exception as e:
        print(f"LAMBDA DEBUG: Error handling event: {str(e)}")
        raise


if __name__ == "__main__":
    lambda_handler({
        "source": "aws.events",
        "detail": {
            "eventType": "collect",
            "providerId": "630b991e-9ebb-4536-93b2-8f4573d618ff",
            "locale": "en-US",
            "tags": [
                "ai",
                "economy"
            ]
        }
    }, {})
