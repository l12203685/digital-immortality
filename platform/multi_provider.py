"""
Multi-Provider LLM Interface — Survival Redundancy (Branch 6.4)
================================================================

Unified interface for calling LLMs across multiple providers.
If Anthropic is down, fall back to OpenAI, then Gemini.

Each provider is optional — only activated if its API key env var is set:
    ANTHROPIC_API_KEY  → Claude (primary)
    OPENAI_API_KEY     → GPT (fallback 1)
    GOOGLE_API_KEY     → Gemini (fallback 2)

Usage:
    from platform.multi_provider import call_llm

    response_text = call_llm(
        system_prompt="You are a recursive engine.",
        user_prompt="Pick the highest-derivative branch.",
    )
"""

import os
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Provider definitions
# ---------------------------------------------------------------------------

@dataclass
class ProviderConfig:
    name: str
    env_var: str
    default_model: str


PROVIDERS = [
    ProviderConfig("anthropic", "ANTHROPIC_API_KEY", "claude-sonnet-4-6"),
    ProviderConfig("openai",    "OPENAI_API_KEY",    "gpt-4o"),
    ProviderConfig("google",    "GOOGLE_API_KEY",    "gemini-2.0-flash"),
]


# ---------------------------------------------------------------------------
# Per-provider call implementations
# ---------------------------------------------------------------------------

def _call_anthropic(api_key: str, system_prompt: str, user_prompt: str, model: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return response.content[0].text


def _call_openai(api_key: str, system_prompt: str, user_prompt: str, model: str) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def _call_google(api_key: str, system_prompt: str, user_prompt: str, model: str) -> str:
    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=4096,
        ),
    )
    return response.text


_CALL_DISPATCH = {
    "anthropic": _call_anthropic,
    "openai":    _call_openai,
    "google":    _call_google,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def available_providers() -> list[str]:
    """Return names of providers whose API keys are set."""
    return [p.name for p in PROVIDERS if os.environ.get(p.env_var)]


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    providers: list[str] | None = None,
) -> str:
    """
    Call an LLM, trying providers in priority order until one succeeds.

    Args:
        system_prompt: System-level instructions.
        user_prompt:   User message / query.
        model:         Override model name. If set, applies to whichever provider
                       answers. Usually omit this and let each provider use its default.
        providers:     Override provider order. Default: all configured providers
                       in priority order (anthropic → openai → google).

    Returns:
        The response text from the first provider that succeeds.

    Raises:
        RuntimeError: If no provider is available or all providers fail.
    """
    if providers is not None:
        # Filter to requested providers that have keys set
        configs = []
        for name in providers:
            for p in PROVIDERS:
                if p.name == name and os.environ.get(p.env_var):
                    configs.append(p)
                    break
    else:
        configs = [p for p in PROVIDERS if os.environ.get(p.env_var)]

    if not configs:
        raise RuntimeError(
            "No LLM providers available. Set at least one of: "
            + ", ".join(p.env_var for p in PROVIDERS)
        )

    errors = []
    for provider in configs:
        call_fn = _CALL_DISPATCH[provider.name]
        use_model = model or provider.default_model
        api_key = os.environ[provider.env_var]

        try:
            logger.info(f"[multi_provider] Trying {provider.name} ({use_model})")
            result = call_fn(api_key, system_prompt, user_prompt, use_model)
            logger.info(f"[multi_provider] Success via {provider.name} ({len(result)} chars)")
            return result
        except Exception as e:
            msg = f"{provider.name} failed: {type(e).__name__}: {e}"
            logger.warning(f"[multi_provider] {msg}")
            errors.append(msg)
            continue

    raise RuntimeError(
        "All LLM providers failed.\n" + "\n".join(f"  - {e}" for e in errors)
    )
