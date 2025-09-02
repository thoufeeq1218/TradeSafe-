import streamlit as st
import tempfile
from pathlib import Path
from Agents import *

st.set_page_config(page_title="Broker Risk Chat", layout="wide")

st.title("💬 Broker Risk Chat Assistant")

# Session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display previous messages
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# File uploader
uploaded_file = st.file_uploader("📂 Upload chat screenshot, receipt, audio or video", type=["png","jpg","jpeg","mp3","wav","mp4"])

# Chat input
if prompt := st.chat_input("Ask me about broker risk..."):
    # Show user message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Handle uploaded file if any
    response_text = ""
    if uploaded_file:
        suffix = Path(uploaded_file.name).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())

        if suffix in [".png", ".jpg", ".jpeg"]:
            b64_image = encode_image_as_data_uri(tmp.name)
            state = app.invoke({"b64_image": b64_image})
            response_text += f"**Detected Type:** {state['doc_type']}\n\n"
            response_text += f"**Extracted Data:**\n```json\n{state['extracted_data']}\n```\n"

        else:
            response_text += "⚡ Audio/Video support can be integrated here with transcription."

    # Add model reply (risk scoring via Gemini)
    msg = HumanMessage(content=[
        {"type": "text", "text": f"User said: {prompt}. Analyze extracted data and return a risk assessment."}
    ])
    llm_resp = llm.invoke([msg])
    response_text += f"\n\n**Risk Assessment:**\n{llm_resp.content}"

    # Show assistant reply
    st.session_state["messages"].append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
