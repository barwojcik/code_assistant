"""
Code Assistant
"""
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from dataclasses import asdict
from typing import Optional
from history import HistoryHandler, HistoryEntry
from generator import OllamaCodeGenerator

class CodeAssistantApp:
    """
    Initializes the Code Assistant application.

    Attributes:
        app: Optional Flask application instance.
        code_generator: Optional OllamaCodeGenerator instance.
        history: Optional HistoryHandler instance.
    """
    def __init__(self):
        self.app: Optional[Flask] = None
        self.code_generator: Optional[OllamaCodeGenerator] = None
        self.history: Optional[HistoryHandler] = None

    def create_app(self) -> Flask:
        """
        Initializes and configures the Flask application.

        Returns:
            Flask application instance.
        """
        self.app = Flask(__name__)
        CORS(self.app, resources={r"/*": {"origins": "*"}})

        self.app.config.from_object('config')
        cfg = self.app.config
        self.app.logger.setLevel(cfg['LOG_LEVEL'])

        # Initialize services
        self.code_generator = OllamaCodeGenerator.from_config(cfg['OLLAMA'])
        self.history = HistoryHandler(max_length=cfg['MAX_HISTORY_LENGTH'])

        self._init_routes()
        return self.app

    def _init_routes(self) -> None:
        """
        Initializes all route handlers for the application.

        Returns:
            None
        """
        @self.app.route('/', methods=['GET'])
        def index() -> str:
            """Render the index page for the application."""
            self.app.logger.info('Rendering index page')
            return render_template('index.html')

        @self.app.route('/process-instruction', methods=['POST'])
        def process_instruction_route():
            """
            Handles the process instruction endpoint.

            Returns:
                Response: The generated code response.
            """
            return self._handle_process_instruction()

        @self.app.route('/get-history', methods=['GET'])
        def get_history_endpoint() -> tuple[Response, int]:
            """
            Handles the get history endpoint.

            Returns:
                Response: A JSON response with the generated code and log messages.
            """
            return self._handle_get_history()

    def _handle_process_instruction(self):
        """Handle the process instruction endpoint logic"""
        try:
            user_instruction = request.json['userInstruction']
            user_code = request.json['userCode']
            self.app.logger.info('User instruction: %s for code: %s', 
                               user_instruction, user_code)

            response_text, output_code = self.code_generator.generate_code(
                user_instruction, user_code)
            self.app.logger.info('Output code: %s', output_code)

            history_entry = HistoryEntry(
                user_instruction, user_code, output_code, response_text)
            self.history.add_new_entry(history_entry)
            self.app.logger.info('Added to the history: %s', history_entry)

            return jsonify({
                'output': output_code,
                'raw_response': response_text,
            }), 200

        except KeyError as e:
            self.app.logger.error('Missing key in request data: %s', e)
            return jsonify({'error': 'Missing key in request data.'}), 400
        except Exception as e:
            self.app.logger.error('Error processing message: %s', e)
            return jsonify({'error': 'Failed to process message.'}), 500

    def _handle_get_history(self) -> tuple[Response, int]:
        """Handle the get history endpoint logic"""
        try:
            history_entries = self.history.get_history()
            history_data = [asdict(entry) for entry in history_entries]
            return jsonify({"success": True, "history": history_data}), 200
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    def run(self, **kwargs):
        """
        Runs the Flask application.

        Args:
            **kwargs: Additional keyword arguments to be passed to the Flask application.
        """
        if not self.app:
            raise RuntimeError("Application not initialized. Call create_app() first.")
        self.app.run(**kwargs)

def main():
    """Initialize and run the application"""
    app = CodeAssistantApp()
    app.create_app()
    app.run()

if __name__ == "__main__":
    main()