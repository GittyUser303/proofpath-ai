from __future__ import annotations

import json
from typing import Any

import httpx

from app.config.settings import Settings, get_settings


class LLMClient:
    """Small HTTP client for optional LLM-powered agent reasoning."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def configured_provider(self) -> str | None:
        provider = (self.settings.llm_provider or "").strip().lower()
        if provider:
            if provider == "gemini" and self.settings.gemini_api_key:
                return provider
            if provider == "openai" and self.settings.openai_api_key:
                return provider
            if provider == "anthropic" and self.settings.anthropic_api_key:
                return provider
            return None
        if self.settings.gemini_api_key:
            return "gemini"
        if self.settings.openai_api_key:
            return "openai"
        if self.settings.anthropic_api_key:
            return "anthropic"
        return None

    def is_configured(self) -> bool:
        return self.configured_provider is not None

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.1,
    ) -> dict[str, Any]:
        """Call the configured LLM and parse a JSON object response."""
        provider = self.configured_provider
        if provider == "gemini":
            text = await self._gemini(system_prompt, user_prompt, temperature)
        elif provider == "openai":
            text = await self._openai(system_prompt, user_prompt, temperature)
        elif provider == "anthropic":
            text = await self._anthropic(system_prompt, user_prompt, temperature)
        else:
            raise RuntimeError("No LLM provider is configured.")
        return self._parse_json(text)

    async def _gemini(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        if not self.settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini.")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-1.5-flash:generateContent?key={self.settings.gemini_api_key}"
        )
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json",
            },
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _openai(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when LLM_PROVIDER=openai.")
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                json=payload,
            )
            response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _anthropic(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        if not self.settings.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic.")
        payload = {
            "model": "claude-3-5-haiku-latest",
            "max_tokens": 900,
            "temperature": temperature,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                },
                json=payload,
            )
            response.raise_for_status()
        data = response.json()
        return data["content"][0]["text"]

    def _parse_json(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.removeprefix("json").strip()
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RuntimeError("The LLM returned non-JSON output.") from exc
        if not isinstance(parsed, dict):
            raise RuntimeError("The LLM returned JSON, but not an object.")
        return parsed
