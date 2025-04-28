"""
Code Assistant
"""
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from generator import OllamaCodeGenerator

# Initialize Flask app and CORS
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config.from_object('config')
cfg = app.config
app.logger.setLevel(cfg['LOG_LEVEL'])

code_generator = OllamaCodeGenerator.from_config(cfg['OLLAMA'])

# Define the route for the index page
@app.route('/', methods=['GET'])
def index() -> str:
    """Render the index page for the application."""
    app.logger.info('Rendering index page')
    return render_template('index.html')  # Render the index.html template

# Define the route for processing instructions
@app.route('/process-instruction', methods=['POST'])
def process_instruction_route():
    """
        Process an instruction by generating Python code based on user input.

        This function takes in two JSON parameters:
            - 'userInstruction': The text of the instruction provided by the user.
            - 'userCode': A snippet of Python code that is expected to be used as input for this process.

        It then sends a POST request to an OLLAMA model endpoint with the instructions and generates a response
        from the server. The response is the generated Python code followed by any additional context or feedback
        from the server.
    """
    try:
        # Extract the user's inputs
        user_instruction = request.json['userInstruction']
        user_code = request.json['userCode']
        app.logger.info('User instruction: %s for code: %s', user_instruction, user_code)

        # Generate Python code
        response_text, output_code = code_generator.generate_code(user_instruction, user_code)
        app.logger.info('Output code: %s', output_code)

        # Return response as JSON
        return jsonify({
            'output': output_code,
            'raw_response': response_text,
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