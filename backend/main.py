"""Main Flask application entry point"""
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', False) == 'True'
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)
