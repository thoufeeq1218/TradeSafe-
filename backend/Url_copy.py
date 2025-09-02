import streamlit as st
import plotly.express as px
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

st.set_page_config(page_title="Broker Risk Dashboard", layout="wide")

# Sidebar Upload
st.sidebar.header("📎 Upload Conversation")
uploaded_file = st.sidebar.file_uploader("Upload audio/video/chat file", type=["png","jpg","jpeg","mp3","wav","mp4","txt"])

# Floating Chat Window (CSS + HTML injection)
st.markdown("""
<style>
.floating-window {
    position: fixed; bottom: 20px; right: 20px;
    width: 350px; height: 500px;
    background: white; border: 2px solid #ccc;
    border-radius: 12px; box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    z-index: 9999; overflow: hidden;
}
.floating-header { background: #4CAF50; color: white;
    padding: 8px; cursor: pointer; font-weight: bold; text-align: center; }
.floating-content { padding: 10px; height: 440px; overflow-y: auto; display: block; }
.collapsed .floating-content { display: none; }
</style>
<script>
function toggleWindow() {
    var win = document.getElementById("floatWin");
    if (win.classList.contains("collapsed")) { win.classList.remove("collapsed"); }
    else { win.classList.add("collapsed"); }
}
</script>
<div id="floatWin" class="floating-window">
  <div class="floating-header" onclick="toggleWindow()">💬 Broker Risk Assistant</div>
  <div class="floating-content">
    <p>Ask your compliance assistant...</p>
  </div>
</div>
""", unsafe_allow_html=True)

# Fake extracted data for demo
data = [
    {"datetime": "2025-03-12", "message": "Low-risk investment", "risk": "Low"},
    {"datetime": "2025-04-13", "message": "High returns guaranteed!", "risk": "High"},
    {"datetime": "2025-05-01", "message": "This stock is safe", "risk": "Medium"}
]
df = pd.DataFrame(data)

# Risk Card
risk_score = "High"  # <-- Normally from your model
color_map = {"Low":"#4CAF50", "Medium":"#FF9800", "High":"#F44336"}
st.markdown(f"""
<div style='padding:20px; border-radius:12px; background:{color_map[risk_score]};
     color:white; text-align:center; font-size:28px; font-weight:bold;'>
    Risk Level: {risk_score}
</div>
""", unsafe_allow_html=True)

# Show Timeline if risk is high
if risk_score == "High":
    st.subheader("📅 Risk Timeline")
    fig = px.scatter(
        df, x="datetime", y=["risk"], text="message", color="risk",
        color_discrete_map={"Low":"green","Medium":"orange","High":"red"}
    )
    fig.update_traces(textposition="top center")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🔗 Conversation Graph")
    G = nx.DiGraph()
    for i in range(len(data)-1):
        G.add_node(i, label=data[i]["message"], risk=data[i]["risk"])
        G.add_edge(i, i+1)

    colors = ["red" if d["risk"]=="High" else "orange" if d["risk"]=="Medium" else "green"
              for _, d in G.nodes(data=True)]

    pos = nx.spring_layout(G)
    plt.figure(figsize=(6,4))
    nx.draw(G, pos, with_labels=False, node_color=colors, node_size=2000, arrows=True)
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    st.pyplot(plt)
