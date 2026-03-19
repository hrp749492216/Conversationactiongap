"""OpenRouter API client for frontier model evaluation.

Uses only Python stdlib (urllib) to make API calls to OpenRouter,
providing access to Claude Sonnet 4, GPT-4o, and Gemini 2.5 Flash.
"""

import json
import os
import time
import urllib.request
import urllib.error


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterClient:
    """HTTP client for OpenRouter API (OpenAI-compatible format)."""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable."
            )
        self._call_count = 0
        self._total_tokens = 0

    def chat(self, model, messages, tools=None, tool_choice=None,
             temperature=0.0, max_tokens=1024, retries=3):
        """Send a chat completion request to OpenRouter.

        Returns the parsed JSON response dict, or None on failure.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice or "auto"

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/AutoResearchClaw",
            "X-Title": "XACT-Experiment",
        }

        for attempt in range(retries):
            try:
                req = urllib.request.Request(
                    OPENROUTER_BASE_URL, data=data, headers=headers, method="POST"
                )
                with urllib.request.urlopen(req, timeout=120) as resp:
                    result = json.loads(resp.read().decode("utf-8"))

                self._call_count += 1
                usage = result.get("usage", {})
                self._total_tokens += usage.get("total_tokens", 0)
                return result

            except urllib.error.HTTPError as e:
                body = ""
                try:
                    body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    pass

                if e.code == 429:
                    # Rate limited — exponential backoff
                    wait = (2 ** attempt) * 2
                    print(f"  Rate limited (429), waiting {wait}s... (attempt {attempt+1}/{retries})")
                    time.sleep(wait)
                    continue
                elif e.code in (500, 502, 503):
                    wait = (2 ** attempt) * 1
                    print(f"  Server error ({e.code}), retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    print(f"  HTTP {e.code} error for {model}: {body[:200]}")
                    return None

            except (urllib.error.URLError, OSError, TimeoutError) as e:
                wait = (2 ** attempt) * 1
                print(f"  Network error: {e}, retrying in {wait}s...")
                time.sleep(wait)
                continue

            except Exception as e:
                print(f"  Unexpected error: {e}")
                return None

        print(f"  All {retries} retries exhausted for {model}")
        return None

    def extract_response(self, result):
        """Extract text content and tool_calls from API response.

        Returns (text_content, tool_calls_list).
        """
        if result is None:
            return "", []

        choices = result.get("choices", [])
        if not choices:
            return "", []

        message = choices[0].get("message", {})
        text = message.get("content", "") or ""
        tool_calls = message.get("tool_calls", []) or []

        return text, tool_calls

    @property
    def stats(self):
        return {
            "total_calls": self._call_count,
            "total_tokens": self._total_tokens,
        }