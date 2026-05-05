from typing import Any

from openai import OpenAI


def build_openai_client() -> Any:
    return OpenAI()
