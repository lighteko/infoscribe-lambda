import logging
from typing import Dict, Any
from src.app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize application
app = create_app()


def lambda_handler(event: Dict[str, Any], context: Any) -> None:
    app.handle(event, context)
