import os

from langchain_openai import ChatOpenAI


DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo"


def get_chat_model(*, temperature: float) -> ChatOpenAI:
    model_name = os.getenv("GRAPHMASAL_OPENAI_MODEL") or os.getenv("OPENAI_CHAT_MODEL") or DEFAULT_OPENAI_MODEL
    return ChatOpenAI(model=model_name, temperature=temperature)


def describe_chat_model() -> str:
    model_name = os.getenv("GRAPHMASAL_OPENAI_MODEL") or os.getenv("OPENAI_CHAT_MODEL") or DEFAULT_OPENAI_MODEL
    return f"{model_name} (OpenAI)"