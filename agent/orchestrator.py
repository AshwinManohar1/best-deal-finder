# agent/orchestrator.py

import re
from agent.prompts import USER_PROMPT, SYSTEM_PROMPT
from agent.tools import web_search, web_scraper, finish
from common.llm_client import get_llm_response
import json

from common.logger import get_logger


TOOL_REGISTRY = {
    "web_search": web_search,
    "web_scraper": web_scraper,
    "finish": finish,
}


def create_prompt(product_name: str, scratchpad: str) -> str:
    """Formats the master prompt for the LLM with a clear strategy and an example."""

    tool_names = list(TOOL_REGISTRY.keys())

    return USER_PROMPT.format(product_name=product_name, scratchpad=scratchpad, tool_names=tool_names)


def parse_llm_output(output: str):
    try:
        data = json.loads(output)
        return data["thought"], data["action"], data["action_input"]
    except Exception as e:
        print(f"DEBUG: Could not parse LLM output as JSON: {output}")
        return None

logger = get_logger(__name__)


class AgentOrchestrator:
    # No changes needed in the class logic, just the functions above
    def __init__(self, product_name: str):
        self.product_name = product_name
        self.scratchpad = ""
        self.max_loops = 5

    def run(self):
        for i in range(self.max_loops):
            tool_names = list(TOOL_REGISTRY.keys())

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT.format(product_name=self.product_name, scratchpad=self.scratchpad, tool_names=tool_names)},
            ]

            llm_output = get_llm_response(messages)
            
            parsed_output = parse_llm_output(llm_output)
            logger.info(f"Parsed output: {parsed_output}")
            if not parsed_output:
                self.scratchpad += f"Observation: My previous output was malformed. I must follow the format.\n"
                continue

            thought, action, action_input = parsed_output

            self.scratchpad += f"Thought: {thought}\n"
            
            if action not in TOOL_REGISTRY:
                observation = f"Error: Unknown tool '{action}'. You must use one of the following tools: {list(TOOL_REGISTRY.keys())}"
            else:
                
                if action == "finish":
                    return {"final_answer": action_input}
                
                tool_function = TOOL_REGISTRY[action]
                logger.info(f"Calling tool function: {tool_function}")
                observation = tool_function(action_input)
                
                self.scratchpad += f"Action: {action}\nAction Input: {action_input}\n"
            
            self.scratchpad += f"Observation: {observation}\n"

        return {"final_answer": "Agent reached max loops without finishing."}