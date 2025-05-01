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
from ollama import Client, GenerateResponse, ListResponse

logger = logging.getLogger(__name__)


class OllamaCodeGenerator:
    """
    Generate Python code based on user instructions.

    This class uses Ollama to generate Python code based on user instructions.

    Args:
        ollama_model (str): Name of the Ollama model to use for code generation. Defaults to 'llama3.2:1b'.
        ollama_host (Optional[str]): Hostname of the Ollama server. Defaults to None.
        prompt_function (Optional[Callable]): Function to use for generating prompts, it overrides the default.
            Must accept two arguments: user_instruction (str) and user_code (str) and return str. Defaults to None.
        generate_kwargs (Optional[dict[str, Any]]): Additional keyword arguments to pass to the generate() method.

    Methods:
        from_config: Create a new instance of OllamaCodeGenerator
            from a configuration dictionary.
        generate_code: Generates a Python code
        check_availability: Check if the Ollama service is available.
    """

    DEFAULT_MODEL: str = 'llama3.2:1b'
    PYTHON_START_TOKEN: str = '```python\n'
    CODE_TOKEN: str = '```'

    def __init__(
            self,
            ollama_model: Optional[str] = None,
            ollama_host: Optional[str] = None,
            prompt_function: Optional[Callable[[str, str], str]] = None,
            generate_kwargs: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the OllamaCodeGenerator class.

        Args:
            ollama_model (str): Name of the Ollama model to use for code generation.
            ollama_host (Optional[str]): Hostname of the Ollama server. Defaults to None.
            prompt_function (Optional[Callable]): Function to use for generating prompts, it overrides the default.
                Must accept two arguments: user_instruction (str) and user_code (str) and return str. Defaults to None.
            generate_kwargs (Optional[dict[str, Any]]): Additional keyword arguments to pass to the generate() method.
        """
        self._default_ollama_model: str = self.DEFAULT_MODEL
        if not ollama_model:
            ollama_model = self.DEFAULT_MODEL
        logger.info('Initializing OllamaCodeGenerator with model: %s', ollama_model)
        self._ollama_model: str = ollama_model
        self._is_model_initialized: bool = False
        self._client: Client = Client(host=ollama_host)
        self._custom_prompt_fn: Optional[Callable[[str, str], str]] = prompt_function
        self._generate_kwargs: dict = (generate_kwargs or dict())

        if self.is_service_available():
            self._is_model_initialized = self._init_model()

    def _init_model(self) -> bool:
        if self.is_model_available(self._ollama_model):
            return True

        if self._ollama_model == self.DEFAULT_MODEL:
            return False

        logger.warning('Falling back to default model %s', self.DEFAULT_MODEL)
        if self.is_model_available(self.DEFAULT_MODEL):
            self._ollama_model = self.DEFAULT_MODEL
            return True

        return False

    @classmethod
    def from_config(cls, generator_config: dict[str, Any]) -> "OllamaCodeGenerator":
        """Creates a new instance of OllamaCodeGenerator from a configuration dictionary.

        Args:
            generator_config (dict[str, Any]): Configuration dictionary containing model name and other options.

        Returns:
            OllamaCodeGenerator: New instance of OllamaCodeGenerator.
        """
        config: dict[str, Any] = generator_config.copy()
        return cls(**config)

    @staticmethod
    def _default_prompt_fn(user_instruction:str, user_code: str) -> str:
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

    def _get_prompt(self, user_instruction: str, user_code: str) -> str:
        """
        Generate a prompt for code generation.

        Args:
            user_instruction (str): Instructions to generate code from.
            user_code (str): Code to use as input.

        Returns:
            str: Prompt to use for generating code.
        """
        if self._custom_prompt_fn:
            try:
                return self._custom_prompt_fn(user_instruction, user_code)
            except Exception as e:
                logger.error('Error in custom prompt function: %s', e)
                logger.error('Falling back to default prompt')

        return self._default_prompt_fn(user_instruction, user_code)

    def _extract_code(self, response_text: str) -> str:
        """
        Extracts code from markdown-formatted text that contains code blocks.

        Args:
            response_text (str): String containing markdown-formatted text with possible code blocks

        Returns:
            str: Extracted code with leading/trailing whitespace removed
        """
        output_code: str = response_text
        if output_code.count(self.CODE_TOKEN) < 2:
            return output_code

        if self.PYTHON_START_TOKEN in output_code:
            output_code = output_code.split(self.PYTHON_START_TOKEN)[1].split(self.CODE_TOKEN)[0]
        else:
            output_code = output_code.split(self.CODE_TOKEN)[1].split(self.CODE_TOKEN)[0]

        if output_code.startswith("\n"):
            output_code = output_code[1:]

        return output_code

    def generate_code(
            self,
            user_instruction: str,
            user_code: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Generate a Python code based on the provided instructions.

        Args:
            user_instruction (str): Instructions to generate code from.
            user_code (Optional[str]): Code to use as input. Defaults to '(no code provided)'.

        Returns:
            str: Generated Python code.
        """
        if not self._is_model_initialized:
            self._init_model()

        user_code = (user_code or "(no code provided)")
        ollama_response: GenerateResponse = self._client.generate(
            model=self._ollama_model,
            prompt=self._get_prompt(user_instruction, user_code),
            stream=False,
            **self._generate_kwargs,
        )
        logger.debug('Ollama response: %s', ollama_response)

        response_text: str = ollama_response.response
        logger.debug('Response text: %s', response_text)

        output_code: str = self._extract_code(response_text)
        logger.debug('Generated code: %s', output_code)

        return response_text, output_code

    def _get_available_models(self) -> ListResponse:
        """

        """
        return self._client.list()

    def get_available_model_names(self) -> list[str]:
        """
        Retrieves a list of available model names from Ollama service.

        Returns:
            list[str]: List of available model names.
        """
        available_models: ListResponse = self._get_available_models()
        available_model_names: list[str] = [model.model for model in available_models.models]
        return available_model_names

    def get_current_model_name(self) -> str:
        """
        Retrieves the name of the current model.

        Returns:
            str: The name of the current model.
        """
        return self._ollama_model

    def is_service_available(self) -> bool:
        """
        Check if the Ollama service is available.

        Returns:
            bool: True if the service is available, False otherwise.
        """
        try:
            _ = self._get_available_models()
        except ConnectionError as e:
            logger.error('Ollama connection error: %s', e)
            return False
        except Exception as e:
            logger.error('Ollama service is not available: %s', e)
            return False

        return True

    def is_model_available(self, model_name: str) -> bool:
        """Check if a specified model is available."""
        available_model_names: list[str] = self.get_available_model_names()
        if model_name in available_model_names:
            logger.info('Model %s found in available models', model_name)
            return True

        logger.warning('Model %s not found, attempting to pull from repository', model_name)
        try:
            self._client.pull(model_name)
            logger.info('Model %s successfully pulled', model_name)
            return True
        except Exception as e:
            logger.error('Failed to pull model %s: %s', model_name, e)
            return False

    def set_model(self, model_name: str) -> bool:
        """Set the active model for code generation."""
        if not self.is_model_available(model_name):
            return False

        self._ollama_model = model_name
        self._is_model_initialized = True
        logger.info('Model set to %s', model_name)
        return True
