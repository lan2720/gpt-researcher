from __future__ import annotations

import json
import os
from fastapi import WebSocket
import time

import openai
from langchain.adapters import openai as lc_openai
from litellm import completion
from colorama import Fore, Style
from openai.error import APIError, RateLimitError

from agent.prompts import auto_agent_instructions
from config import Config

CFG = Config()

# TODO: 增加azure配置
openai.api_base = CFG.azure_api_base
openai.api_key = CFG.azure_api_key
openai.api_version = CFG.azure_api_version
openai.api_type = CFG.api_type

from typing import Optional
import logging

def create_chat_completion(
    messages: list,  # type: ignore
    model: Optional[str] = None,
    temperature: float = CFG.temperature,
    max_tokens: Optional[int] = None,
    stream: Optional[bool] = False,
    websocket: WebSocket | None = None,
) -> str:
    """Create a chat completion using the OpenAI API
    Args:
        messages (list[dict[str, str]]): The messages to send to the chat completion
        model (str, optional): The model to use. Defaults to None.
        temperature (float, optional): The temperature to use. Defaults to 0.9.
        max_tokens (int, optional): The max tokens to use. Defaults to None.
        stream (bool, optional): Whether to stream the response. Defaults to False.
    Returns:
        str: The response from the chat completion
    """

    # validate input
    if model is None:
        raise ValueError("Model cannot be None")
    if max_tokens is not None and max_tokens > 8001:
        raise ValueError(f"Max tokens cannot be more than 8001, but got {max_tokens}")
    if stream and websocket is None:
        raise ValueError("Websocket cannot be None when stream is True")

    # create response
    for attempt in range(10):  # maximum of 10 attempts
        response = send_chat_completion_request(
            messages, model, temperature, max_tokens, stream, websocket
        )
        return response

    logging.error("Failed to get response from OpenAI API")
    raise RuntimeError("Failed to get response from OpenAI API")


def send_chat_completion_request(
    messages, model, temperature, max_tokens, stream, websocket
):
    if not stream:
        result = completion(
            model=model, # Change model here to use different models
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            # api_version=os.getenv("AZURE_API_VERSION", "2023-07-01-preview"),
            custom_llm_provider=os.getenv("API_TYPE", "azure"),
            # api_type=os.getenv("API_TYPE", "azure"),
            # provider=CFG.llm_provider, # Change provider here to use a different API
        )
        return result["choices"][0]["message"]["content"]
    else:
        return stream_response(model, messages, temperature, max_tokens, websocket)


async def stream_response(model, messages, temperature, max_tokens, websocket):
    paragraph = ""
    response = ""
    print(f"streaming response...")

    # TODO: 此处stream=True, 暂时修改为False
    for chunk in completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            custom_llm_provider=os.getenv("API_TYPE", "azure"),
            # api_version=os.getenv("AZURE_API_VERSION", "2023-07-01-preview"),
            # api_type=os.getenv("API_TYPE", "azure"),
            # provider=CFG.llm_provider,
            stream=False,
    ):
        print(f"chunk: {chunk}")
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content is not None:
            response += content
            paragraph += content
            if "\n" in paragraph:
                await websocket.send_json({"type": "report", "output": paragraph})
                paragraph = ""
    print(f"streaming response complete")
    return response


def choose_agent(task: str) -> dict:
    """Determines what agent should be used
    Args:
        task (str): The research question the user asked
    Returns:
        agent - The agent that will be used
        agent_role_prompt (str): The prompt for the agent
    """
    try:
        response = create_chat_completion(
            model=CFG.smart_llm_model,
            messages=[
                {"role": "system", "content": f"{auto_agent_instructions()}"},
                {"role": "user", "content": f"task: {task}"}],
            temperature=0,
        )

        return json.loads(response)
    except Exception as e:
        print(f"{Fore.RED}Error in choose_agent: {e}{Style.RESET_ALL}")
        return {"agent": "Default Agent",
                "agent_role_prompt": "You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text."}


