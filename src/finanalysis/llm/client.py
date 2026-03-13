# src/finanalysis/llm/client.py
import logging
from typing import List, Dict, Optional
from openai import OpenAI

from ..config import Settings

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM client wrapper for OpenAI-compatible APIs"""

    def __init__(
        self,
        settings: Settings,
        system_prompt: Optional[str] = None
    ):
        """Initialize LLM client

        Args:
            settings: Application settings
            system_prompt: Optional system prompt for all requests
        """
        self.settings = settings
        self.model = settings.llm_model
        self.system_prompt = system_prompt

        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )

        logger.info(f"Initialized LLM client with model {self.model}")

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Complete a chat conversation

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Model response text
        """
        # Add system prompt if configured
        full_messages = []
        if self.system_prompt:
            full_messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        full_messages.extend(messages)

        # Use provided values or defaults
        temp = temperature if temperature is not None else self.settings.llm_temperature
        tokens = max_tokens if max_tokens is not None else self.settings.llm_max_tokens

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temp,
                max_tokens=tokens,
            )

            content = response.choices[0].message.content
            logger.debug(f"LLM response: {content[:100]}...")
            return content

        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise

    def extract_json(
        self,
        prompt: str,
        temperature: Optional[float] = None,
    ) -> Dict:
        """Extract structured JSON from prompt

        Args:
            prompt: Prompt text
            temperature: Override default temperature

        Returns:
            Parsed JSON dict
        """
        import json

        # Add JSON formatting instruction
        full_prompt = f"{prompt}\n\nRespond with valid JSON only."

        response = self.complete(
            messages=[{"role": "user", "content": full_prompt}],
            temperature=temperature or 0.0,  # Use low temp for structured output
        )

        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if response.startswith("```"):
                lines = response.split("\n")
                # Remove first and last lines (```json and ```)
                response = "\n".join(lines[1:-1])

            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}\nResponse: {response}")
            raise ValueError(f"Invalid JSON response: {e}")
