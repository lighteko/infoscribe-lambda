import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Deferred import to prevent circular references
def get_app():
    from src.app import create_app
    return create_app()

# Initialize application lazily when needed
app = None

def lambda_handler(event: Dict[str, Any], context: Any) -> None:
    global app
    if app is None:
        app = get_app()
    app.handle(event, context)
