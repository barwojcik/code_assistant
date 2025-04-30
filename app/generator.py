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
        ollama_model (str): Name of the Ollama model to use for code generation. Defdefaults to 'llama3.2:1b'.
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
        logger.info('Initializing OllamaCodeGenerator with model: %s', ollama_model)
        self._default_ollama_model: str = 'llama3.2:1b'
        if not ollama_model:
            ollama_model = self._default_ollama_model
        self._ollama_model: str = ollama_model
        self._client: Client = Client(host=ollama_host)
        if prompt_function:
            self._get_prompt: Callable[[str, str], str] = prompt_function
        self._generate_kwargs: dict = (generate_kwargs or dict())

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

    @staticmethod
    def _get_code(response_text: str) -> str:
        """
        Extracts code from markdown-formatted text that contains code blocks.

        Args:
            response_text (str): String containing markdown-formatted text with possible code blocks

        Returns:
            str: Extracted code with leading/trailing whitespace removed
        """
        output_code: str = response_text
        if output_code.count("```") < 2:
            return output_code

        if "```python\n" in output_code:
            output_code = output_code.split("```python\n")[1].split("```")[0]
        else:
            output_code = output_code.split("```")[1].split("```")[0]

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

        output_code: str = self._get_code(response_text)
        logger.debug('Generated code: %s', output_code)

        return response_text, output_code

    def _get_available_models(self) -> ListResponse:
        """

        """
        return self._client.list()

    def get_available_model_names(self) -> list[str]:
        available_models: ListResponse = self._get_available_models()
        available_model_names: list[str] = [model.model for model in available_models.models]
        return available_model_names

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
        available_model_names: list[str] = self.get_available_model_names()
        if model_name not in available_model_names:
            logger.warning('Model %s not found in available models %s', model_name, available_model_names)
            logger.warning('Attempting to pull model %s from remote repository', model_name)
            try:
                self._client.pull(model_name)
                logger.info('Model %s successfully pulled from remote repository', model_name)
            except Exception as e:
                logger.error('Failed to pull model %s from remote repository: %s', model_name, e)
                return False

        logger.info('Model %s found in available models %s', model_name, available_model_names)
        return True

    def set_model(self, model_name: str) -> bool:
        if not self.is_model_available(model_name):
            return False

        self._ollama_model = model_name
        logger.info('Model set to %s', model_name)
        return True
