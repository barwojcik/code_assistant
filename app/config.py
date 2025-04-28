"""
Code Assistant configuration file.
For Flask configuration, see: https://flask.palletsprojects.com/en/2.2.x/config/
"""
import logging

DEBUG = True
TESTING = True
LOG_LEVEL = logging.INFO
OLLAMA=dict(
    ollama_host='http://localhost:11434',
    ollama_model='llama3.2:1b'
)