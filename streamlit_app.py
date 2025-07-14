# streamlit_app.py

import streamlit as st
import time

# --- Direct Imports from your Agent Logic ---
# Make sure your agent and tools directories are structured correctly
from agent.orchestrator import AgentOrchestrator

# --- Streamlit UI ---

st.set_page_config(page_title="AI Shopping Agent", layout="wide")
st.title("🤖 AI Shopping Agent Demo")
st.markdown("This demo runs the AI agent directly within Streamlit. Enter a product and watch its thought process live.")

# Initialize session state to prevent the UI from resetting during reruns
if "running" not in st.session_state:
    st.session_state.running = False
    st.session_state.log = []
    st.session_state.final_result = ""

# --- Sidebar for Input ---
with st.sidebar:
    st.header("Start a New Search")
    product_name_input = st.text_input(
        "Enter a product name:", 
        "DJI Mini 4 Pro Drone",
        disabled=st.session_state.running
    )
    
    start_button = st.button("Find Best Price", disabled=st.session_state.running)

# --- Main Display Area ---
log_placeholder = st.expander("Agent's Thought Process", expanded=True)
with log_placeholder:
    log_container = st.empty()

final_answer_placeholder = st.empty()

# The core logic when the button is pressed
if start_button and product_name_input:
    # --- Reset UI for a new run ---
    st.session_state.running = True
    st.session_state.log = []
    st.session_state.final_result = ""
    log_container.empty()
    final_answer_placeholder.empty()

    # --- THIS IS THE KEY: The UI Updater Function ---
    # This function will be passed to the agent.
    # The agent will call it every time it has an update.
    def ui_updater(key, value):
        if key == "intermediate_steps":
            # Format the step for better display
            if "Thought:" in value:
                formatted_step = f"🤔 **{value.replace('Thought:', 'Thought:')}**"
            elif "Action:" in value:
                formatted_step = f"⚡ **{value.replace('Action:', 'Action:')}**"
            elif "Observation:" in value:
                formatted_step = f"👀 _{value.replace('Observation:', 'Observation:')}_"
            else:
                formatted_step = value

            # Append the new step to our log and redraw the log container
            st.session_state.log.append(formatted_step)
            log_container.markdown("\n\n---\n\n".join(st.session_state.log))
    
    # Run the agent in a spinner to show it's working
    with st.spinner("🤖 Agent is thinking..."):
        try:
            # Instantiate the agent directly, passing our UI updater function
            agent = AgentOrchestrator(
                product_name=product_name_input,
                job_updater=ui_updater
            )
            # This is a blocking call. The agent runs to completion.
            result = agent.run()
            
            # Store the final result
            st.session_state.final_result = result.get("final_answer", "Agent did not provide a final answer.")

        except Exception as e:
            st.session_state.final_result = f"An error occurred: {e}"
            st.error(st.session_state.final_result)

    # Display the final result
    final_answer_placeholder.success(f"**Final Answer:** {st.session_state.final_result}")
    st.session_state.running = False
    st.balloons()

# Keep the log displayed after the run is complete
log_container.markdown("\n\n---\n\n".join(st.session_state.log))
if st.session_state.final_result:
    final_answer_placeholder.success(f"**Final Answer:** {st.session_state.final_result}")