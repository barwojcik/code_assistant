"""
Code Assistant configuration file.
For Flask configuration, see: https://flask.palletsprojects.com/en/2.2.x/config/
For Ollama, see: https://github.com/ollama/ollama/blob/main/docs/api.md
"""

import logging

DEBUG = True
TESTING = True
LOG_LEVEL = logging.DEBUG
SERVER_NAME='0.0.0.0:5000'
OLLAMA=dict(
    ollama_host='http://localhost:11434',
    ollama_model='llama3.2:1b'
)
MAX_HISTORY_LENGTH = 10
