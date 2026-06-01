"""
Premium Streamlit Frontend for Multi-Agent Conversational Sales Copilot.
Implements beautiful dark-mode glassmorphism styling, real-time memory tracking, and feedback widgets.
"""
import streamlit as st
import requests
import uuid
import pandas as pd
from typing import Dict, Any, List

# Define API Backend host
BACKEND_URL = "http://localhost:8081/api"

# Configure premium dark theme styles using Streamlit markdown injections
st.set_page_config(
    page_title="Sales Copilot - Hybrid GraphRAG",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark CSS Styles
st.markdown(
    """
    <style>
    /* Dark Obsidian theme colors */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Glassmorphism sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Premium Title Header */
    .header-title {
        background: linear-gradient(90deg, #1f6feb 0%, #58a6ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        color: #8b949e;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Glassmorphism Card for Requirements */
    .req-card {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
    }
    .req-title {
        color: #58a6ff;
        font-weight: bold;
        margin-bottom: 10px;
        font-size: 1.1rem;
        border-bottom: 1px solid #21262d;
        padding-bottom: 5px;
    }
    
    /* Custom Chat Bubbles */
    .user-bubble {
        background-color: #1f6feb;
        color: #ffffff;
        border-radius: 15px 15px 0px 15px;
        padding: 12px 16px;
        margin: 8px 0px 8px auto;
        max-width: 75%;
        width: fit-content;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .assistant-bubble {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 15px 15px 15px 0px;
        padding: 15px 18px;
        margin: 8px auto 8px 0px;
        max-width: 85%;
        width: fit-content;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        line-height: 1.5;
    }
    
    /* Custom buttons */
    .stButton>button {
        background-color: #21262d;
        color: #c9d1d9;
        border: 1px solid #30363d;
        border-radius: 8px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #1f6feb;
        color: white;
        border-color: #58a6ff;
        box-shadow: 0 0 10px rgba(88, 166, 255, 0.4);
    }
    
    /* Status label */
    .status-active {
        color: #3fb950;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------- SESSION STATE INITS -----------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "requirements" not in st.session_state:
    st.session_state.requirements = {}
if "sessions_list" not in st.session_state:
    st.session_state.sessions_list = []

# ----------------- API HELPER FUNCTIONS -----------------
def fetch_sessions():
    try:
        response = requests.get(f"{BACKEND_URL}/sessions/")
        if response.status_code == 200:
            st.session_state.sessions_list = response.json()
    except Exception as e:
        st.sidebar.error(f"Cannot load sessions list: {e}")

def load_session_details(sess_id: str):
    try:
        response = requests.get(f"{BACKEND_URL}/sessions/{sess_id}")
        if response.status_code == 200:
            data = response.json()
            st.session_state.chat_history = data.get("messages", [])
            st.session_state.requirements = data.get("requirements") or {}
            st.session_state.session_id = sess_id
    except Exception as e:
        st.error(f"Error loading session details: {e}")

def trigger_ingestion():
    with st.spinner("Đang nạp sản phẩm vào Qdrant & Neo4j..."):
        try:
            response = requests.post(f"{BACKEND_URL}/ingest/products")
            if response.status_code in [200, 201]:
                data = response.json()
                st.sidebar.success(f"Nạp thành công! Vector: {data['qdrant_count']}, Graph: {data['neo4j_count']}")
            else:
                st.sidebar.warning(f"Lỗi nạp một phần: {response.text}")
        except Exception as e:
            st.sidebar.error(f"Lỗi nạp dữ liệu: {e}")

def send_message(text: str):
    with st.spinner("Copilot đang suy luận..."):
        try:
            payload = {
                "session_id": st.session_state.session_id,
                "message": text
            }
            response = requests.post(f"{BACKEND_URL}/chat/", json=payload)
            if response.status_code == 200:
                data = response.json()
                # Reload history and requirements state from DB
                load_session_details(st.session_state.session_id)
                fetch_sessions()
            else:
                st.error(f"Gửi tin nhắn thất bại: {response.text}")
        except Exception as e:
            st.error(f"Lỗi kết nối Backend: {e}")

def send_feedback(product_id: str, feedback_type: str, comment: str = None):
    try:
        payload = {
            "session_id": st.session_state.session_id,
            "product_id": product_id,
            "feedback_type": feedback_type,
            "comment": comment
        }
        response = requests.post(f"{BACKEND_URL}/feedback/", json=payload)
        if response.status_code == 200:
            st.toast("Cảm ơn Anh/Chị đã gửi phản hồi! 👍" if feedback_type == "like" else "Đã ghi nhận góp ý của Anh/Chị! 📝")
        else:
            st.error("Gửi feedback lỗi.")
    except Exception as e:
        st.error(f"Lỗi gửi feedback: {e}")

# ----------------- SIDEBAR INTERFACE -----------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2318/2318274.png", width=60)
st.sidebar.markdown("<div style='font-size:1.5rem; font-weight:bold; color:#58a6ff;'>Truck Copilot Dashboard</div>", unsafe_allow_html=True)

# Ingest products button
st.sidebar.subheader("🗃️ Dữ liệu Sản Phẩm")
if st.sidebar.button("Nạp lại CSV (Qdrant & Neo4j)", use_container_width=True):
    trigger_ingestion()

# Sessions Selector
st.sidebar.subheader("💬 Quản lý Hội thoại")
fetch_sessions()

session_options = {s["session_id"]: f"Phiên {s['session_id'][:8]}... ({s['created_at'][:16].replace('T', ' ')})" for s in st.session_state.sessions_list}
session_options[st.session_state.session_id] = f"Phiên hiện tại ({st.session_state.session_id[:8]})"

options_list = list(session_options.keys())
try:
    default_index = options_list.index(st.session_state.session_id)
except ValueError:
    default_index = 0

selected_sess = st.sidebar.selectbox(
    "Chọn phiên chat:",
    options=options_list,
    index=default_index,
    format_func=lambda x: session_options[x]
)

if selected_sess != st.session_state.session_id:
    load_session_details(selected_sess)
    st.rerun()

if st.sidebar.button("➕ Tạo Phiên Mới", use_container_width=True):
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.chat_history = []
    st.session_state.requirements = {}
    st.toast("Đã khởi tạo phiên trò chuyện mới!")
    st.rerun()

# REAL-TIME MEMORY TRACKING WIDGET
st.sidebar.subheader("🧠 Trí Nhớ Đa Tác Nhân")
st.sidebar.markdown(
    """
    <div class='req-card'>
        <div class='req-title'>📋 Yêu cầu trích xuất (PostgreSQL)</div>
        <table style='width:100%; font-size:0.9rem; color:#c9d1d9;'>
            <tr><td><b>Ngân sách:</b></td><td class='status-active'>{}</td></tr>
            <tr><td><b>Tải trọng:</b></td><td class='status-active'>{}</td></tr>
            <tr><td><b>Nhiên liệu:</b></td><td class='status-active'>{}</td></tr>
            <tr><td><b>Loại xe:</b></td><td class='status-active'>{}</td></tr>
            <tr><td><b>Mục đích:</b></td><td class='status-active'>{}</td></tr>
            <tr><td><b>Đại bàn:</b></td><td class='status-active'>{}</td></tr>
            <tr><td><b>Loại hàng:</b></td><td class='status-active'>{}</td></tr>
        </table>
    </div>
    """.format(
        f"{st.session_state.requirements.get('budget')} triệu" if st.session_state.requirements.get('budget') else "Chưa có",
        f"{st.session_state.requirements.get('payload')} kg" if st.session_state.requirements.get('payload') else "Chưa có",
        st.session_state.requirements.get('fuel_type') or "Chưa có",
        st.session_state.requirements.get('vehicle_type') or "Chưa có",
        st.session_state.requirements.get('use_case') or "Chưa có",
        st.session_state.requirements.get('location') or "Chưa có",
        st.session_state.requirements.get('cargo_type') or "Chưa có"
    ),
    unsafe_allow_html=True
)

# ----------------- MAIN INTERFACE -----------------
st.markdown("<div class='header-title'>🚚 Multi-Agent Conversational Sales Copilot</div>", unsafe_allow_html=True)
st.markdown("<div class='header-subtitle'>Tư vấn xe thương mại thông minh sử dụng Hybrid GraphRAG (Qdrant + Neo4j) & LangGraph</div>", unsafe_allow_html=True)

# Display chat history in container
chat_container = st.container()

with chat_container:
    if not st.session_state.chat_history:
        st.markdown(
            """
            <div class='assistant-bubble'>
                Xin chào Anh/Chị! Em là **Truck Sales Copilot** - Chuyên viên tư vấn xe thương mại thông minh.<br>
                Em có thể hỗ trợ Anh/Chị chọn dòng xe van hoặc xe tải phù hợp nhất với nhu cầu sử dụng của doanh nghiệp.<br><br>
                <i>Gợi ý câu hỏi: "Tôi cần tìm xe chở hàng" hoặc "Tôi cần xe tải van dưới 500 triệu chạy xăng chở đồ trong nội thành"</i>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        for idx, msg in enumerate(st.session_state.chat_history):
            if msg["sender"] == "user":
                st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='assistant-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
                
                # Check if the assistant message is a recommendation and has products
                # Since we load recommendations state, we can add a feedback action widget
                # only underneath the very last assistant message for a clean UI
                if idx == len(st.session_state.chat_history) - 1:
                    # Render small like/dislike buttons
                    st.markdown("<p style='font-size:0.8rem; color:#8b949e; margin-bottom:5px;'>Anh/Chị có thích đề xuất tư vấn này của trợ lý không?</p>", unsafe_allow_html=True)
                    col1, col2, col3 = st.columns([1, 1, 10])
                    
                    with col1:
                        if st.button("👍 Thích", key=f"like_{idx}"):
                            # Assume first recommended product or general
                            send_feedback(product_id="GENERAL_RECOMMENDATION", feedback_type="like", comment="User liked the recommendations.")
                    with col2:
                        if st.button("👎 Không thích", key=f"dislike_{idx}"):
                            # Prompt user with text input for comment
                            st.session_state.show_dislike_form = True
                            
                    if st.session_state.get("show_dislike_form", False):
                        with st.form("dislike_comment_form"):
                            comment = st.text_input("Góp ý của bạn giúp cải thiện tư vấn:", placeholder="Mẫu xe chưa đúng ngân sách, Tải trọng quá nhỏ...")
                            submitted = st.form_submit_button("Gửi góp ý")
                            if submitted:
                                send_feedback(product_id="GENERAL_RECOMMENDATION", feedback_type="dislike", comment=comment)
                                st.session_state.show_dislike_form = False
                                st.rerun()

# Chat Input Box
user_input = st.chat_input("Nhập câu hỏi của bạn tại đây (ví dụ: chạy xăng thì sao, chở 2 tấn)...")

if user_input:
    # Render user bubble instantly for fluid UX
    st.markdown(f"<div class='user-bubble'>{user_input}</div>", unsafe_allow_html=True)
    # Call backend
    send_message(user_input)
    st.rerun()
