from src.app import create_app
app = create_app()

def lambda_handler(event, context):
    """
    AWS Lambda handler function that processes API Gateway events
    """
    # The app instance should handle the event and return a response
    app.handle(event)
