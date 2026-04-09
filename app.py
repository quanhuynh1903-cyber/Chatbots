import streamlit as st
import pandas as pd
import joblib
import time
import io
import base64
from gtts import gTTS
from fuzzywuzzy import fuzz
import speech_recognition as sr

# --- 1. CẤU HÌNH GIAO DIỆN ĐỐI THOẠI ---
st.set_page_config(page_title="AI Speaking Partner", page_icon="💬", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; }
    /* Bong bóng chat người dùng */
    .user-msg {
        background-color: #0084ff;
        color: white;
        padding: 15px;
        border-radius: 18px 18px 2px 18px;
        margin: 10px 0;
        float: right;
        clear: both;
        max-width: 70%;
    }
    /* Bong bóng chat AI */
    .ai-msg {
        background-color: white;
        color: #1c1e21;
        padding: 15px;
        border-radius: 18px 18px 18px 2px;
        margin: 10px 0;
        float: left;
        clear: both;
        max-width: 70%;
        border: 1px solid #ddd;
    }
    /* Card phân tích feedback */
    .feedback-panel {
        background: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #4f46e5;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. HÀM HỖ TRỢ ---
def speak(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    return f'<audio autoplay><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'

# --- 3. QUẢN LÝ LỊCH SỬ ĐỐI THOẠI (SESSION STATE) ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "ai", "content": "Hi there! I'm your English partner. What's on your mind today?"}]
if "last_feedback" not in st.session_state:
    st.session_state.last_feedback = None

# --- 4. GIAO DIỆN CHÍNH ---
st.title("💬 Real-time Speaking Conversation")

col_chat, col_feedback = st.columns([2, 1])

with col_chat:
    st.subheader("Conversation")
    # Hiển thị lịch sử chat
    chat_container = st.container(height=450)
    with chat_container:
        for msg in st.session_state.messages:
            div_class = "ai-msg" if msg["role"] == "ai" else "user-msg"
            st.markdown(f'<div class="{div_class}">{msg["content"]}</div>', unsafe_allow_html=True)

    # Nhập liệu bằng giọng nói (Voice Input)
    st.write("---")
    voice_input = st.audio_input("Bấm micro để nói chuyện với AI")

    if voice_input:
        with st.spinner("AI đang nghe..."):
            r = sr.Recognizer()
            try:
                with sr.AudioFile(voice_input) as source:
                    audio_data = r.record(source)
                    user_text = r.recognize_google(audio_data, language="en-US")
                    
                    # 1. Lưu câu nói của người dùng
                    st.session_state.messages.append({"role": "user", "content": user_text})
                    
                    # 2. AI Phản hồi (Ở đây bạn có thể dùng nlp_model để dự đoán câu trả lời)
                    # Demo: AI phản hồi đơn giản dựa trên từ khóa
                    ai_reply = "That sounds interesting! Tell me more about it."
                    if "hello" in user_text.lower(): ai_reply = "Hello! How has your day been so far?"
                    elif "weather" in user_text.lower(): ai_reply = "The weather is quite nice for a conversation, don't you think?"
                    
                    st.session_state.messages.append({"role": "ai", "content": ai_reply})
                    
                    # 3. Phân tích Feedback (Chạy ngầm cho câu vừa nói)
                    # So sánh với một câu "lý tưởng" hoặc đánh giá độ dài/từ vựng
                    score = min(100, len(user_text) * 5 + 30) # Demo logic điểm số
                    st.session_state.last_feedback = {
                        "text": user_text,
                        "score": score,
                        "suggestion": "Good flow! Try to use more descriptive adjectives to make your speech vivid."
                    }
                    
                    st.rerun()
            except:
                st.error("I couldn't catch that. Could you say it again?")

# --- 5. BẢNG PHÂN TÍCH FEEDBACK (Bên phải) ---
with col_feedback:
    st.subheader("Practice Feedback")
    if st.session_state.last_processed_id := st.session_state.last_feedback:
        fb = st.session_state.last_feedback
        st.markdown(f"""
        <div class="feedback-panel">
            <p style="color: #666; font-size: 0.8em; margin-bottom: 5px;">LATEST ANALYSIS</p>
            <h2 style="margin: 0; color: #4f46e5;">{fb['score']}%</h2>
            <p style="font-weight: bold; margin-top: 10px;">Your sentence:</p>
            <p style="font-style: italic; color: #444;">"{fb['text']}"</p>
            <hr>
            <p><b>Coach's Advice:</b><br>{fb['suggestion']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Phát âm thanh câu trả lời mới nhất của AI
        last_ai_msg = st.session_state.messages[-1]["content"]
        st.markdown(speak(last_ai_msg), unsafe_allow_html=True)
    else:
        st.info("Hãy bắt đầu nói để AI phân tích kỹ năng giao tiếp của bạn.")

with st.sidebar:
    st.header("Conversation Tools")
    if st.button("Clear Conversation"):
        st.session_state.messages = [{"role": "ai", "content": "Conversation reset. How can I help?"}]
        st.session_state.last_feedback = None
        st.rerun()
