import os

# Import the create_app function from your app.py
from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    print("🚀 Starting TruthCheck System...")
    print("📊 Flask Backend: http://127.0.0.1:5000") # Updated to 127.0.0.1 for local access

    # Run the Flask application
    # debug=True enables reloader and debugger, useful during development
    # host='0.0.0.0' makes the server accessible from other devices on the network
    # port=5000 is the default Flask port
    # Create the database in a writable location if needed (e.g., /tmp/history.db for read-only systems)
    # For now, we keep it local, but ensure the folder is writable in Docker
    port = int(os.environ.get("PORT", 7860))
    app.run(debug=False, host='0.0.0.0', port=port)
