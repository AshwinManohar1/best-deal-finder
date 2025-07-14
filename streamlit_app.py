import streamlit as st
import requests

st.set_page_config(page_title="AI Shopping Agent", layout="wide")
st.title("🤖 AI Shopping Agent Demo")
st.markdown("This demo calls the backend API to find the best price for your product.")

if "running" not in st.session_state:
    st.session_state.running = False
    st.session_state.final_result = ""

with st.sidebar:
    st.header("Start a New Search")
    product_name_input = st.text_input(
        "Enter a product name:", 
        "DJI Mini 4 Pro Drone",
        disabled=st.session_state.running
    )
    start_button = st.button("Find Best Price", disabled=st.session_state.running)

final_answer_placeholder = st.empty()
error_placeholder = st.empty()

if start_button and product_name_input:
    st.session_state.running = True
    st.session_state.final_result = ""
    final_answer_placeholder.empty()
    error_placeholder.empty()

    with st.spinner("🤖 Agent is thinking..."):
        try:
            # Call the FastAPI endpoint
            response = requests.post(
                "http://localhost:8001/agent/best-deal/start",
                json={"product_name": product_name_input},
                timeout=120  # adjust as needed
            )
            if response.status_code == 200:
                data = response.json()
                final_answer = data.get("final_answer", "No answer returned.")
                st.session_state.final_result = final_answer
                final_answer_placeholder.success(f"**Final Answer:** {final_answer}")
            else:
                st.session_state.final_result = ""
                error_placeholder.error(f"API Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.session_state.final_result = ""
            error_placeholder.error(f"Request failed: {e}")

    st.session_state.running = False

if st.session_state.final_result:
    final_answer_placeholder.success(f"**Final Answer:** {st.session_state.final_result}")