import logging
import requests
from typing import Dict, Optional
from ollama import Client

logger = logging.getLogger(__name__)


class OllamaCodeGenerator:
    def __init__(self, ollama_url: str, ollama_model: str):
        """
        Initialize the Ollama code generator.

        Args:
            ollama_url (str): URL of the Ollama API.
            ollama_model (str): Model name for the Ollama API.
        """
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model

    @classmethod
    def from_config(cls, generator_config: Dict) -> "OllamaCodeGenerator":
        return cls(generator_config['OLLAMA_URL'], generator_config['OLLAMA_MODEL'])

    @staticmethod
    def _get_prompt(user_instruction:str, user_code: Optional[str] = str):
        return (
            f'Based on this instructions:\n{user_instruction}\n and provided python code:\n'
            f'{user_code or "(no code provided)"}\n generate python code.'
        )

    def generate_code(self, user_instruction: str, user_code: Optional[str] = None) -> str:
        """
        Generate a Python code based on the provided instructions.

        Args:
            user_instruction (str): Instructions to generate code from.
            user_code (Optional[str]): Code to use as input. Defaults to '(no code provided)'.

        Returns:
            str: Generated Python code.
        """
        response = requests.post(
            self.ollama_url,
            json={
                'prompt': self._get_prompt(user_instruction, user_code),
                'model': self.ollama_model,
                'stream': False,
            },
        )
        logger.info('Ollama response: %s', response)

        response_text = response.json()['response']
        logger.info('Response text: %s', response_text)

        output_code = response_text.split("```python\n")[1].split("```")[0]
        logger.info('Generated code: %s', output_code)

        return output_code
