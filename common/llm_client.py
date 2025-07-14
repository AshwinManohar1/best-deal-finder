# agent/llm_client.py

from typing import Any
import openai

# This is the client that will connect to our local vLLM server.
# The `api_key` is required by the library but not used by vLLM.
client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed",
)

# This is the model name we used to launch vLLM.
MODEL_NAME = "Qwen/Qwen1.5-1.8B-Chat"

def get_llm_response(messages: list[Any]) -> str:
    """
    Sends a full prompt to the local vLLM server and returns the raw response.
    This version uses a "user" role for the entire prompt, suitable for ReAct-style agents.
    """
    try:
        response: Any = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1,
            max_tokens=500,
            stop=["Observation:"]
        )
        return response.choices[0].message.content.strip()
    except openai.APIConnectionError as e:
        print("🔴 Error connecting to vLLM server.")
        print(f"🔴 Please make sure the vLLM server is running and accessible at {client.base_url}")
        # In a real app, you might want to raise this exception or handle it more gracefully
        return "Error: Could not connect to the language model."
    except Exception as e:
        print(f"🔴 An unexpected error occurred: {e}")
        return "Error: An unexpected error occurred while communicating with the language model."