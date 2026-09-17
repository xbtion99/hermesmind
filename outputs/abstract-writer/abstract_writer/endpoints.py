"""Pick the endpoint and model that match the key you actually have.

The key alone should be enough. Someone who pastes an OpenAI key into the key
file should not also have to know that the default endpoint is OpenRouter and
that `anthropic/claude-sonnet-4.5` is not an OpenAI model name. Both of those
would surface as a bare 401, which says nothing useful on a phone.

So the endpoint is inferred from where the key came from and what it looks
like. An explicitly chosen endpoint always wins: a value only counts as
inferable while it is still the shipped default.
"""

from __future__ import annotations

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
OPENROUTER_MODEL = "anthropic/claude-sonnet-4.5"
OPENAI_BASE = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-4o"

PROFILES = {
    "openrouter": (OPENROUTER_BASE, OPENROUTER_MODEL),
    "openai": (OPENAI_BASE, OPENAI_MODEL),
}

DEFAULT_BASE_URL = OPENROUTER_BASE
DEFAULT_MODEL = OPENROUTER_MODEL


def infer_profile(key: str | None, var: str | None = None) -> str:
    """Name the provider a key belongs to. Falls back to openrouter."""
    if var == "OPENAI_API_KEY":
        return "openai"
    if not key:
        return "openrouter"
    if key.startswith("sk-or-"):          # OpenRouter's own prefix
        return "openrouter"
    if key.startswith("sk-"):             # OpenAI, including sk-proj-
        return "openai"
    return "openrouter"


def profile_of_base(base_url: str) -> str:
    for name, (base, _model) in PROFILES.items():
        if base_url.rstrip("/") == base.rstrip("/"):
            return name
    return "custom"


def resolve(base_url: str | None, model: str | None,
            key: str | None, var: str | None = None) -> tuple[str, str]:
    """Return the (base_url, model) to use.

    `base_url` and `model` are whatever the caller was given, from a flag or an
    environment variable. Either one is treated as chosen only when it differs
    from the shipped default, so a stale key file that still carries the
    original defaults does not defeat the inference.
    """
    profile = infer_profile(key, var)
    inferred_base, _ = PROFILES[profile]

    chosen_base = base_url if base_url and base_url.rstrip("/") != OPENROUTER_BASE else None
    final_base = chosen_base or inferred_base

    chosen_model = model if model and model != OPENROUTER_MODEL else None
    if chosen_model:
        final_model = chosen_model
    else:
        final_model = PROFILES.get(profile_of_base(final_base), PROFILES["openrouter"])[1]
    return final_base, final_model
