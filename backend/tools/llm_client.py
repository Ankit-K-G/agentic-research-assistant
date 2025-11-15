# backend/tools/llm_client.py
import os
import asyncio
import json
import requests

# Read OpenRouter key from env var
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def generate(
    prompt: str,
    model: str = "deepseek/deepseek-r1",
    max_tokens: int = 512,
    temperature: float = 0.2,
) -> str:
    """
    Simple OpenRouter HTTP client using requests run in a threadpool.
    Returns the assistant text (string) or "" on error.
    """
    if not OPENROUTER_API_KEY:
        print("❌ ERROR: OPENROUTER_API_KEY not set")
        return ""

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    # NOTE: this must be a regular function (not async) so run_in_executor executes it
    def _call():
        try:
            return requests.post(url, headers=headers, json=payload, timeout=20)
        except Exception as e:
            return e

    resp = await asyncio.get_event_loop().run_in_executor(None, _call)

    # If exception occurred inside _call, resp will be an Exception instance
    if isinstance(resp, Exception):
        print("\n=== OPENROUTER REQUEST ERROR ===")
        print(resp)
        print("================================\n")
        return ""

    # Ensure we have a requests.Response
    try:
        status = resp.status_code
        raw_text = resp.text
    except Exception as e:
        print("\n=== OPENROUTER RESPONSE INVALID ===")
        print("repr(resp):", repr(resp)[:1000])
        print("error:", e)
        print("==================================\n")
        return ""

    # Debug: print beginning of response body
    print("\n===== RAW OPENROUTER RESPONSE (truncated) =====")
    print(raw_text[:2000])
    print("==============================================\n")

    if status != 200:
        print("\n=== OPENROUTER HTTP ERROR ===")
        print("Status:", status)
        print(raw_text)
        print("================================\n")
        return ""

    # Parse JSON safely
    try:
        data = resp.json()
    except Exception as e:
        print("❌ Failed to parse JSON from OpenRouter:", e)
        return ""

    # Extract assistant content
    try:
        # typical structure: data["choices"][0]["message"]["content"]
        content = data["choices"][0]["message"]["content"]
    except Exception:
        # Try a few fallback shapes
        if isinstance(data, dict):
            # sometimes text sits under top-level 'text' or choices->text
            content = data.get("text") or (
                data.get("choices") and data["choices"][0].get("text")
            )
        else:
            content = None

    if content is None:
        print("❌ OpenRouter response did not contain assistant content. Full response:")
        print(json.dumps(data)[:3000])
        return ""

    if not isinstance(content, str):
        try:
            content = str(content)
        except Exception:
            content = ""

    return content.strip()
