# agent/orchestrator.py

import re
from typing import Callable
from llm_client import get_llm_response
from tools import functions as tool_functions

TOOL_REGISTRY = {
    "web_search": tool_functions.web_search,
    "web_scraper": tool_functions.web_scraper,
    "finish": tool_functions.finish,
}

# --- FIX 3: ADDING A FEW-SHOT EXAMPLE ---
# agent/orchestrator.py

# ... (imports and TOOL_REGISTRY) ...

def create_prompt(product_name: str, scratchpad: str) -> str:
    """Formats the master prompt for the LLM with a clear strategy and an example."""
    
    # --- New, highly directive tool descriptions ---
    tool_docs = (
        "- web_search(query: str): Search the web for information. Returns a summary and a list of source URLs.\n"
        "- web_scraper(url: str): Get the full text content of a specific URL. Use this to investigate a URL found via web_search.\n"
        "- finish(answer: str): CRITICAL! Use this tool as your very final step. The input MUST be a summary of the best price and MUST include the URL of the source."
    )
    tool_names = list(TOOL_REGISTRY.keys())

    return f"""
You are an expert shopping assistant finding the best price for: {product_name}.

**CRITICAL RULE: You MUST end your work by using the `finish` tool.** Do not just state the answer in a thought. You will fail if you do not use the `finish` tool as your final action.

**STRATEGY:**
1.  Use `web_search` to find prices and retailer URLs.
2.  Review the `Observation` from the search. If you have found a clear price and a source URL, you have enough information.
3.  Your final step MUST be to call the `finish` tool with a summary including the price and the source URL.

**EXAMPLE OF YOUR TASK:**
Here is an example of a successful run for a different product.
---
Thought: I need to find the price for the 'GoPro HERO12'. I will start with a web search.
Action: web_search
Action Input: GoPro HERO12 price
Observation: Summary: The GoPro HERO12 Black is priced at $399.99 on the official GoPro website. It is also available at retailers like Best Buy and Amazon for a similar price.
Sources:
- GoPro Official Site: https://gopro.com/en/us/shop/cameras/hero12-black/CHDHX-121-master.html
- Best Buy: https://www.bestbuy.com/site/gopro-hero12-black-action-camera-black/6557372.p?skuId=6557372
Thought: I have found a clear price of $399.99 and the official URL. This is enough information to finish the task.
Action: finish
Action Input: The best price for the GoPro HERO12 is $399.99, available at the official GoPro store: https://gopro.com/en/us/shop/cameras/hero12-black/CHDHX-121-master.html
---

**YOUR CURRENT TASK:**

**History of your work so far:**
{scratchpad}

Your turn! Follow the format from the example EXACTLY.
Thought: [Your reasoning based on the history and strategy]
Action: [{', '.join(tool_names)}]
Action Input: [The input for the chosen tool]
"""

# The rest of your orchestrator.py file (parse_llm_output, AgentOrchestrator class) can remain the same.
# The fixes we made to them previously are still valid and good.

# --- FIX 2: MORE RESILIENT PARSER ---
def parse_llm_output(output: str) -> tuple[str, str, str] | None:
    """Parses the LLM's 'Thought: Action: Action Input:' response."""
    thought_match = re.search(r"Thought:\s*(.*?)\s*Action:", output, re.DOTALL)
    action_match = re.search(r"Action:\s*(\w+)", output)
    action_input_match = re.search(r"Action Input:\s*(.*)", output, re.DOTALL)

    if not (thought_match and action_match and action_input_match):
        print(f"DEBUG: Could not parse LLM output: {output}")
        return None

    thought = thought_match.group(1).strip()
    action = action_match.group(1).strip()
    action_input = action_input_match.group(1).strip().strip('"')
    
    return thought, action, action_input


class AgentOrchestrator:
    # No changes needed in the class logic, just the functions above
    def __init__(self, product_name: str, job_updater: Callable):
        self.product_name = product_name
        self.scratchpad = ""
        self.max_loops = 10 
        self.job_updater = job_updater

    def run(self):
        for i in range(self.max_loops):
            prompt = create_prompt(self.product_name, self.scratchpad)
            llm_output = get_llm_response(prompt)
            
            parsed_output = parse_llm_output(llm_output)
            if not parsed_output:
                self.job_updater("intermediate_steps", f"Loop {i+1}: LLM output was malformed. I will try again, following the format exactly.")
                self.scratchpad += f"Observation: My previous output was malformed. I must follow the format.\n"
                continue

            thought, action, action_input = parsed_output

            self.job_updater("intermediate_steps", f"Loop {i+1} | Thought: {thought}")
            self.scratchpad += f"Thought: {thought}\n"
            
            if action not in TOOL_REGISTRY:
                observation = f"Error: Unknown tool '{action}'. You must use one of the following tools: {list(TOOL_REGISTRY.keys())}"
            else:
                self.job_updater("intermediate_steps", f"Loop {i+1} | Action: {action}('{action_input}')")
                
                if action == "finish":
                    return {"final_answer": action_input}
                
                tool_function = TOOL_REGISTRY[action]
                observation = tool_function(action_input)
                
                self.scratchpad += f"Action: {action}\nAction Input: {action_input}\n"
            
            self.job_updater("intermediate_steps", f"Loop {i+1} | Observation: {str(observation)[:500]}...")
            self.scratchpad += f"Observation: {observation}\n"

        return {"final_answer": "Agent reached max loops without finishing."}