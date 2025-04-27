"""
Code Assistant
"""
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Initialize Flask app and CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config.from_object('config')
cfg = app.config
app.logger.setLevel(cfg['LOG_LEVEL'])

OLLAMA_URL = 'http://localhost:11434/api/generate'
OLLAMA_MODEL = 'llama3.2:1b'

# Define the route for the index page
@app.route('/', methods=['GET'])
def index() -> str:
    """Render the index page for the chatbot."""
    return render_template('index.html')  # Render the index.html template

# Define the route for processing instructions
@app.route('/process-instruction', methods=['POST'])
def process_instruction_route():
    """Process user messages and return chatbot responses."""
    try:
        # Extract the user's inputs
        user_instruction = request.json['userInstruction']
        user_code = request.json['userCode']
        app.logger.info('User instruction: %s for code: %s', user_instruction, user_code)

        response = requests.post(
            OLLAMA_URL,
            json={
                'prompt': f'Based on this instruction: {user_instruction} and provided python code: {user_code}. Generate a python code.',
                'model': OLLAMA_MODEL,
                'stream': False,
            },
        )
        app.logger.info('Response from a server: %s', response.json())
        response_text = response.json()['response']
        output_code = response_text.split("```python\n")[1].split("```")[0]

        # Return response as JSON
        return jsonify({
            'output': output_code,
        }), 200

    except KeyError as e:
        app.logger.error('Missing key in request data: %s', e)
        return jsonify({'error': 'Missing key in request data.'}), 400

    except Exception as e:
        app.logger.error('Error processing message: %s', e)
        return jsonify({'error': 'Failed to process message.'}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run()