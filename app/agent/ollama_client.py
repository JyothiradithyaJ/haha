"""Reusable Ollama client for local LLM operations (Qwen3.5 4B)."""
from __future__ import annotations

import json
import re
import httpx
from typing import Any
from app.config import config


class OllamaError(Exception):
    """Base exception for Ollama interactions."""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when the Ollama server cannot be reached."""
    pass


class OllamaModelNotFoundError(OllamaError):
    """Raised when the requested model is not found in the local Ollama instance."""
    pass


class OllamaTimeoutError(OllamaError):
    """Raised when generation times out."""
    pass


class OllamaClient:
    """Client for local Ollama API."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
    ):
        raw_url = (base_url or config.OLLAMA_BASE_URL).rstrip("/")
        if "://localhost" in raw_url:
            raw_url = raw_url.replace("://localhost", "://127.0.0.1")
        self.base_url = raw_url
        self.model = model or config.OLLAMA_MODEL
        self.timeout = timeout or config.OLLAMA_TIMEOUT
        self._is_available: bool | None = None

    def check_health(self) -> dict[str, Any]:
        """Check if Ollama is running and the designated model is installed.

        DO NOT auto-download models. Raise clear actionable error if missing.
        """
        tags_url = f"{self.base_url}/api/tags"
        try:
            with httpx.Client(timeout=httpx.Timeout(5.0, connect=1.5)) as client:
                resp = client.get(tags_url)
                if resp.status_code != 200:
                    self._is_available = False
                    raise OllamaConnectionError(
                        f"Ollama server at {self.base_url} returned HTTP {resp.status_code}. "
                        "Please verify your local Ollama installation."
                    )
                data = resp.json()
        except (httpx.ConnectError, httpx.NetworkError) as err:
            self._is_available = False
            raise OllamaConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                f"Please ensure Ollama is installed and running (e.g., run 'ollama serve' or open the Ollama desktop app).\n"
                f"Underlying error: {err}"
            ) from err
        except httpx.TimeoutException as err:
            self._is_available = False
            raise OllamaTimeoutError(
                f"Connection to Ollama at {self.base_url} timed out. "
                "Please verify the Ollama service is responsive."
            ) from err

        self._is_available = True

        models = data.get("models", [])
        model_names = [m.get("name", "") for m in models]
        
        # Check if model name or prefix matches
        target = self.model
        has_model = any(
            target == name or target in name or name.startswith(target)
            for name in model_names
        )

        if not has_model:
            raise OllamaModelNotFoundError(
                f"Required model '{self.model}' is not available in local Ollama.\n"
                f"Available local models: {model_names or 'None'}\n"
                f"To install the model, open your terminal and run:\n"
                f"    ollama pull {self.model}\n"
                "The application will not download models automatically."
            )

        return {"status": "ok", "base_url": self.base_url, "model": self.model, "models": model_names}

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.2,
        format_json: bool = False,
    ) -> str:
        """Call Ollama /api/generate with specified prompts and options."""
        url = f"{self.base_url}/api/generate"
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt
        if format_json:
            payload["format"] = "json"

        if self._is_available is False:
            raise OllamaConnectionError(f"Ollama server at {self.base_url} is unreachable.")

        try:
            with httpx.Client(timeout=httpx.Timeout(self.timeout, connect=1.5)) as client:
                resp = client.post(url, json=payload)
                if resp.status_code == 404:
                    raise OllamaModelNotFoundError(
                        f"Ollama returned 404: model '{self.model}' not found. "
                        f"Run 'ollama pull {self.model}' first."
                    )
                resp.raise_for_status()
                data = resp.json()
                self._is_available = True
                return data.get("response", "").strip()
        except (httpx.ConnectError, httpx.NetworkError) as err:
            self._is_available = False
            raise OllamaConnectionError(
                f"Failed to connect to Ollama at {self.base_url}: {err}"
            ) from err
        except httpx.TimeoutException as err:
            self._is_available = False
            raise OllamaTimeoutError(
                f"Ollama generation or connection timed out for model {self.model} at {self.base_url}."
            ) from err

    def generate_json(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.1,
    ) -> dict[str, Any] | list[Any]:
        """Generate structured JSON from Ollama with robust parsing and markdown cleaning."""
        # Append instruction to ensure valid JSON
        json_instruction = "\nIMPORTANT: Return ONLY a valid JSON object or array. Do not output markdown fences or explanatory text outside the JSON."
        full_system = (system_prompt + json_instruction) if system_prompt else json_instruction
        
        raw_text = self.generate(
            prompt=prompt,
            system_prompt=full_system,
            temperature=temperature,
            format_json=True,
        )

        # Attempt direct parse
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            pass

        # Try stripping markdown code fences ```json ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_text)
        if fence_match:
            try:
                return json.loads(fence_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding the first '{' and last '}' or '[' and ']'
        brace_match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", raw_text)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"Failed to parse valid JSON from LLM output. Raw output was:\n{raw_text[:500]}"
        )
