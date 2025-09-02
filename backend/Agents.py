import base64
import os
from typing import TypedDict, Dict
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# ----------- STATE -------------
class State(TypedDict):
    b64_image: str   # holds base64 encoded image (data URI)
    doc_type: str    # "chat" or "receipt"
    extracted_data: Dict


KEY ="AIzaSyDd4jlrhKC03mt7GgwdbUThz2UdWKBHBec"
# ----------- GEMINI MODEL -------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=KEY
)

# ----------- HELPERS -------------
def encode_image_as_data_uri(image_path: str) -> str:
    """Read local image and return base64 data URI string"""
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"   # use image/jpeg if JPG

# ----------- NODES -------------
def detect_doc_type(state: State):
    message = HumanMessage(content=[
        {"type": "text", "text": "Classify this image as 'chat' or 'receipt'."},
        {"type": "image_url", "image_url": state["b64_image"]}
    ])
    resp = llm.invoke([message])
    if "chat" in resp.content.strip().lower():
        result = "chat"
    elif "receipt" in resp.content.strip().lower():
        result = "receipt"
    else:
        result = "receipt"
    return {"doc_type": result}

def extract_chat(state: State):
    message = HumanMessage(content=[
        {"type": "text", "text": """Extract structured JSON:
        {
          "messages": [
            {"sender": "", "receiver": "", "datetime": "", "message": ""}
          ]
        }"""},
        {"type": "image_url", "image_url": state["b64_image"]}
    ])
    resp = llm.invoke([message])
    return {"extracted_data": resp.content}

def extract_receipt(state: State):
    message = HumanMessage(content=[
        {"type": "text", "text": """Extract structured JSON:
        {
          "broker_name": "",
          "registration_number": "",
          "date": "",
          "stock_details": [],
          "total_amount": ""
        }"""},
        {"type": "image_url", "image_url": state["b64_image"]}
    ])
    resp = llm.invoke([message])
    return {"extracted_data": resp.content}

# ----------- BUILD GRAPH -------------
graph = StateGraph(State)
graph.add_node("detect_doc_type", detect_doc_type)
graph.add_node("extract_chat", extract_chat)
graph.add_node("extract_receipt", extract_receipt)

graph.set_entry_point("detect_doc_type")

graph.add_conditional_edges(
    "detect_doc_type",
    lambda state: state["doc_type"],  # branching logic
    {
        "chat": "extract_chat",
        "receipt": "extract_receipt"
    }
)

graph.set_finish_point("extract_chat")
graph.set_finish_point("extract_receipt")

app = graph.compile()

# ----------- RUN TEST -------------
if __name__ == "__main__":
    image_path = "DELETE.png"   # your WhatsApp chat or receipt image

    b64_image = encode_image_as_data_uri(image_path)

    state = app.invoke({"b64_image": b64_image})

    print("\n=== RESULTS ===")
    print("Detected Type:", state["doc_type"])
    print("Extracted Data:", state["extracted_data"])
