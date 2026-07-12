#!/usr/bin/env python3
"""
LLM Client — unified interface to multiple LLM providers.

Supports Google Gemini, OpenAI, and Ollama (local). The agent code
talks to this abstraction and never imports provider-specific SDKs
directly.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from models.audit_result import AgentResponse

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Abstract LLM client."""

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
    ) -> AgentResponse:
        ...


# ─────────────────────────────────────────────────────────────────
# Google Gemini
# ─────────────────────────────────────────────────────────────────

class GeminiClient(BaseLLMClient):
    """Client for Google Gemini API."""

    def __init__(self, model: str = "gemini-2.0-flash", api_key: str | None = None):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Install google-generativeai: pip install google-generativeai")
        if api_key:
            genai.configure(api_key=api_key)
        self._genai = genai
        self._model_name = model

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
    ) -> AgentResponse:
        model = self._genai.GenerativeModel(
            self._model_name,
            generation_config={"temperature": temperature},
        )

        # Convert messages to Gemini format
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] in ("user", "system") else "model"
            history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=history)
        last_message = messages[-1]["content"] if messages else ""

        try:
            response = chat.send_message(last_message)
            text = response.text

            # Check for function calls in response
            has_tool_call = False
            tool_name = None
            tool_args = {}

            if hasattr(response, "candidates") and response.candidates:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        has_tool_call = True
                        tool_name = part.function_call.name
                        tool_args = dict(part.function_call.args) if part.function_call.args else {}
                        text = ""
                        break

            return AgentResponse(
                content=text,
                has_tool_call=has_tool_call,
                tool_name=tool_name,
                tool_args=tool_args,
            )
        except Exception as e:
            logger.error("Gemini API error: %s", e)
            return AgentResponse(content=f"LLM error: {e}")


# ─────────────────────────────────────────────────────────────────
# OpenAI
# ─────────────────────────────────────────────────────────────────

class OpenAIClient(BaseLLMClient):
    """Client for OpenAI API."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai")
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
    ) -> AgentResponse:
        kwargs: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
        }
        if tools:
            kwargs["tools"] = tools

        try:
            response = self._client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            message = choice.message

            has_tool_call = bool(message.tool_calls)
            tool_name = None
            tool_args = {}

            if has_tool_call:
                tc = message.tool_calls[0]
                tool_name = tc.function.name
                tool_args = json.loads(tc.function.arguments) if tc.function.arguments else {}

            return AgentResponse(
                content=message.content or "",
                has_tool_call=has_tool_call,
                tool_name=tool_name,
                tool_args=tool_args,
                finish_reason=choice.finish_reason,
            )
        except Exception as e:
            logger.error("OpenAI API error: %s", e)
            return AgentResponse(content=f"LLM error: {e}")


# ─────────────────────────────────────────────────────────────────
# Ollama (local)
# ─────────────────────────────────────────────────────────────────

class OllamaClient(BaseLLMClient):
    """Client for Ollama (local LLM)."""

    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self._model = model
        self._base_url = base_url

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
    ) -> AgentResponse:
        import requests

        payload: Dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if tools:
            payload["tools"] = tools

        try:
            resp = requests.post(f"{self._base_url}/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            message = data.get("message", {})
            content = message.get("content", "")

            has_tool_call = False
            tool_name = None
            tool_args = {}

            tool_calls = message.get("tool_calls", [])
            if tool_calls:
                has_tool_call = True
                tc = tool_calls[0]
                tool_name = tc.get("function", {}).get("name")
                tool_args = tc.get("function", {}).get("arguments", {})

            return AgentResponse(
                content=content,
                has_tool_call=has_tool_call,
                tool_name=tool_name,
                tool_args=tool_args,
            )
        except Exception as e:
            logger.error("Ollama API error: %s", e)
            return AgentResponse(content=f"LLM error: {e}")


# ─────────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────────

class LLMClient:
    """Factory that creates the right client based on provider name."""

    @staticmethod
    def create(
        provider: str = "google",
        model: str | None = None,
        api_key: str | None = None,
    ) -> BaseLLMClient:
        provider = provider.lower()
        if provider == "google":
            return GeminiClient(model=model or "gemini-2.0-flash", api_key=api_key)
        elif provider == "openai":
            return OpenAIClient(model=model or "gpt-4o-mini", api_key=api_key)
        elif provider == "ollama":
            return OllamaClient(model=model or "llama3.1")
        else:
            raise ValueError(f"Unknown LLM provider: {provider}. Use: google, openai, ollama")
