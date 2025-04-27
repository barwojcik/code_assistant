"""
Code Assistant
"""
from flask import Flask, render_template, request, jsonify
from flask.wrappers import Response
from flask_cors import CORS

# Initialize Flask app and CORS
app = Flask (__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config.from_object('config')
cfg = app.config
app.logger.setLevel(cfg['LOG_LEVEL'])

# Define the route for the index page
@app.route('/', methods=['GET'])
def index() -> str:
    """Render the index page for the chatbot."""
    return render_template('index.html')  # Render the index.html template

# Run the Flask app
if __name__ == "__main__":
    app.run()