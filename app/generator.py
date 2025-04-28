"""
This module contains the OllamaCodeGenerator class for generating Python code based on user instructions.

The OllamaCodeGenerator class uses Ollama to generate Python code based on user instructions.

Example usage:
generator = OllamaCodeGenerator(ollama_model='llama3.2:1b')
output_code = generator.generate_code(user_instruction='Write a function to calculate the area of a circle.',
                                      user_code='def circle_area(radius):')
print(output_code)
"""
import logging
from typing import Any, Optional, Callable
from ollama import Client, GenerateResponse

logger = logging.getLogger(__name__)


class OllamaCodeGenerator:
    """
    Generate Python code based on user instructions.

    This class uses Ollama to generate Python code based on user instructions.

    Attributes:
        ollama_model (str): Name of the Ollama model to use for code generation.
        _client (Client): Ollama client instance.
        generate_kwargs (dict[str, Any]): Additional keyword arguments to pass to the generate() method.

    Args:
        ollama_model (str): Name of the Ollama model to use for code generation.
        ollama_host (Optional[str]): Hostname of the Ollama server. Defaults to None.
        prompt_function (Optional[Callable]): Function to use for generating prompts, it overrides the default.
            Must accept two arguments: user_instruction (str) and user_code (str) and return str. Defaults to None.
        generate_kwargs (Optional[dict[str, Any]]): Additional keyword arguments to pass to the generate() method.

    Methods:
        from_config(cls, generator_config: dict[str, Any]): Create a new instance of OllamaCodeGenerator
            from a configuration dictionary.
        _get_prompt(user_instruction:str, user_code: str): Generate a prompt for code generation.
        generate_code(self, user_instruction: str, user_code: Optional[str] = None): Generates a Python code
    """
    def __init__(
            self,
            ollama_model: str,
            ollama_host: Optional[str] = None,
            prompt_function: Optional[Callable] = None,
            generate_kwargs: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize the OllamaCodeGenerator class.

        Args:
            ollama_model (str): Name of the Ollama model to use for code generation.
            ollama_host (Optional[str]): Hostname of the Ollama server. Defaults to None.
            prompt_function (Optional[Callable]): Function to use for generating prompts, it overrides the default.
                Must accept two arguments: user_instruction (str) and user_code (str) and return str. Defaults to None.
            generate_kwargs (Optional[dict[str, Any]]): Additional keyword arguments to pass to the generate() method.
        """
        logger.info('Initializing OllamaCodeGenerator with model: %s', ollama_model)
        self.ollama_model = ollama_model
        self._client = Client(host=ollama_host)
        if prompt_function:
            self._get_prompt = prompt_function
        self.generate_kwargs = (generate_kwargs or dict())

    @classmethod
    def from_config(cls, generator_config: dict[str, Any]) -> "OllamaCodeGenerator":
        """Creates a new instance of OllamaCodeGenerator from a configuration dictionary.

        Args:
            generator_config (dict[str, Any]): Configuration dictionary containing model name and other options.
                Must contain 'ollama_model' key.

        Returns:
            OllamaCodeGenerator: New instance of OllamaCodeGenerator.

        Raises:
            KeyError: If 'ollama_model' key is missing from the configuration dictionary.
        """
        config: dict[str, Any] = generator_config.copy()

        if 'ollama_model' not in config.keys():
            raise KeyError("Missing required 'ollama_model' key in configuration")

        model_id: str = config.pop('ollama_model')
        return cls(model_id, **config)

    @staticmethod
    def _get_prompt(user_instruction:str, user_code: str) -> str:
        """
        Generate a prompt for code generation.

        Args:
            user_instruction (str): Instructions to generate code from.
            user_code (str): Code to use as input.

        Returns:
            str: Prompt to use for generating code.
        """
        return (
            f'Based on this instructions:\n{user_instruction}\n and provided python code:\n'
            f'{user_code}\n generate python code.'
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
        user_code = (user_code or "(no code provided)")
        ollama_response: GenerateResponse = self._client.generate(
            model=self.ollama_model,
            prompt=self._get_prompt(user_instruction, user_code),
            stream=False,
            **self.generate_kwargs,
        )
        logger.debug('Ollama response: %s', ollama_response)

        response_text: str = ollama_response.response
        logger.debug('Response text: %s', response_text)

        output_code: str = response_text.split("```python\n")[1].split("```")[0]
        logger.debug('Generated code: %s', output_code)

        return output_code
