"""
Code Assistant Application Module

This module provides the basic structure for creating a Flask application with routing for different endpoints.
It also includes helper functions to manage history entries.

Classes:
    CodeAssistantApp: Initializes the Code Assistant application.
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

    Methods:
        create_app: Initializes and configures the Flask application.
        run: Runs the Flask application.
    """
    def __init__(self) -> None:
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

        if 'LOG_LEVEL' in cfg.keys():
            self.app.logger.setLevel(cfg['LOG_LEVEL'])
        self.app.logger.info('Initialized Flask application')

        if 'OLLAMA' in cfg.keys():
            self.code_generator = OllamaCodeGenerator.from_config(cfg['OLLAMA'])
        else:
            self.code_generator = OllamaCodeGenerator()

        if 'MAX_HISTORY_LENGTH' in cfg.keys():
            self.history = HistoryHandler(max_length=cfg['MAX_HISTORY_LENGTH'])
        else:
            self.history = HistoryHandler()

        self._init_routes()
        return self.app

    def _init_routes(self) -> None:
        """
        Initializes all route handlers for the application.

        Returns:
            None
        """
        # Main page route
        self.app.add_url_rule(
            '/',
            endpoint='index',
            view_func=self._index,
            methods=['GET'],
        )
        self.app.logger.info('Initialized routes for main page')

        # API routes
        self.app.add_url_rule(
            '/process-instruction',
            endpoint='process_instruction',
            view_func=self._process_instruction,
            methods=['POST'],
        )
        self.app.logger.info('Initialized route for processing instructions')

        self.app.add_url_rule(
            '/get-history',
            endpoint='get_history',
            view_func=self._get_history,
            methods=['GET'],
        )
        self.app.logger.info('Initialized route for retrieving history')

        # Health check endpoint for monitoring
        self.app.add_url_rule(
            '/health',
            endpoint='health_check',
            view_func=self._health_check,
            methods=['GET'],
        )
        self.app.logger.info('Initialized route for health check')

    def _index(self) -> str:
        """
        Render the index page for the application.

        Returns:
            str: Rendered HTML template

        Raises:
            TemplateNotFound: If the template file is missing
        """
        try:
            self.app.logger.info('Rendering index page')
            return render_template('index.html')
        except Exception as e:
            self.app.logger.error('Error rendering index page: %s', e)
            # Return a minimal error page if template rendering fails
            return """
            <!DOCTYPE html>
            <html>
            <head><title>Code Assistant - Error</title></head>
            <body>
                <h1>Error loading application</h1>
                <p>The application encountered an error. Please check server logs.</p>
            </body>
            </html>
            """

    def _process_instruction(self) -> tuple[Response, int]:
        """
        Handle the process instruction endpoint logic

        Returns:
            tuple[Response, int]: JSON response and HTTP status code
        """
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
            self.app.logger.info('Added new history entry')

            return jsonify({
                'output': output_code,
                'raw_response': response_text,
            }), 200

        except KeyError as e:
            self.app.logger.error('Missing key in request data: %s', e)
            return jsonify({'error': f'Missing required field: {str(e)}'}), 400
        except ConnectionError as e:
            self.app.logger.error('Connection error: %s', e)
            return jsonify({'error': 'Ollama service is not available'}), 503
        except Exception as e:
            self.app.logger.error('Error processing message: %s', e)
            return jsonify({'error': 'Internal server error'}), 500

    def _get_history(self) -> tuple[Response, int]:
        """
        Handle the get history endpoint logic

        Returns:
            tuple[Response, int]: JSON response with history data and HTTP status code
        """
        try:
            history_entries = self.history.get_history()
            history_data = [asdict(entry) for entry in history_entries]
            self.app.logger.info('Retrieved %d history entries', len(history_data))
            return jsonify({"success": True, "history": history_data}), 200
        except Exception as e:
            self.app.logger.error('Error retrieving history: %s', e)
            return jsonify({"success": False, "error": "Failed to retrieve history"}), 500

    def _health_check(self) -> tuple[Response, int]:
        """
        Health check endpoint to verify service status

        Returns:
            tuple[Response, int]: JSON response with service status and HTTP status code
        """
        if self.code_generator.is_service_available():
            return jsonify({
                "status": "healthy",
                "services": {
                    "ollama": "up",
                },
                "version": "1.0.0"
            }), 200
        else:
            return jsonify({
                "status": "degraded",
                "services": {
                    "ollama": "down"
                },
                "error": "Ollama service is not available"
            }), 503

    def run(self, **kwargs):
        """
        Runs the Flask application.

        Args:
            **kwargs: Additional keyword arguments to be passed to the Flask application.

        Raises:
            RuntimeError: If the application hasn't been initialized.
        """
        if not self.app:
            raise RuntimeError("Application not initialized. Call create_app() first.")
        self.app.run(**kwargs)
        self.app.logger.info('Application running')
