import streamlit as st
import pandas as pd
import joblib
from gtts import gTTS
import io
import time
import base64
from fuzzywuzzy import fuzz

# --- 1. CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="ESL Master AI", page_icon="🎓", layout="centered")

# Giao diện Modern Minimalist
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #ffffff; }
    
    /* Dashboard Feedback */
    .feedback-container {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        background-color: #f8fafc;
        margin: 20px 0;
    }
    .metric-box {
        text-align: center;
        padding: 10px;
        background: white;
        border-radius: 8px;
        border: 1px solid #edf2f7;
    }
    .ai-bubble {
        background-color: #6366f1;
        color: white;
        padding: 15px 20px;
        border-radius: 15px 15px 15px 0;
        margin-bottom: 20px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. XỬ LÝ DỮ LIỆU ---
@st.cache_resource
def init_resources():
    try:
        data = pd.read_csv('10000_esl_dataset.csv')
        model = joblib.load('esl_model.pkl')
        return data, model
    except: return None, None

df, nlp_model = init_resources()

def play_audio(text):
    tts = gTTS(text=text, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    audio_b64 = base64.b64encode(fp.getvalue()).decode()
    html_str = f'<audio autoplay><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>'
    st.markdown(html_str, unsafe_allow_html=True)

# --- 3. QUẢN LÝ TRẠNG THÁI ---
if "history" not in st.session_state: st.session_state.history = []
if "current_response" not in st.session_state: st.session_state.current_response = None

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🎓 ESL AI Tutor")
st.caption("Luyện tập tiếng Anh thông minh với phản hồi thời gian thực")

# Hiển thị câu hỏi/lời chào từ AI
st.markdown('<div class="ai-bubble">Hello! I\'m your language partner. Let\'s practice. Can you introduce yourself or say something in English?</div>', unsafe_allow_html=True)

# --- KHỐI PHÂN TÍCH (PRACTICE FEEDBACK) - THIẾT KẾ MỚI ---
if st.session_state.current_response:
    res = st.session_state.current_response
    
    st.markdown('<div class="feedback-container">', unsafe_allow_html=True)
    st.subheader("📊 Practice Analysis")
    
    # Chia cột hiển thị chỉ số
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-box"><small>ACCURACY</small><br><b style="color:#6366f1; font-size:1.5em;">{res["score"]}%</b></div>', unsafe_allow_html=True)
    with col2:
        level = "High" if res["score"] > 80 else "Medium" if res["score"] > 50 else "Low"
        st.markdown(f'<div class="metric-box"><small>FLUENCY</small><br><b style="color:#10b981; font-size:1.5em;">{level}</b></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><small>STATUS</small><br><b style="font-size:1.1em;">{"✅ Passed" if res["score"] > 60 else "⚠️ Review"}</b></div>', unsafe_allow_html=True)

    # Chi tiết phản hồi
    st.markdown(f"""
    <div style="margin-top:20px; font-size: 0.95em;">
        <p><b>Your Input:</b> <span style="color:#475569;">"{res['user_text']}"</span></p>
        <p><b>Feedback:</b> {res['feedback']}</p>
        <p style="color:#6366f1;"><b>Recommendation:</b> {res['advice']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. KHU VỰC TƯƠNG TÁC ---
st.write("")
input_mode = st.radio("Choose mode:", ["Keyboard", "Microphone"], horizontal=True, label_visibility="collapsed")

if input_mode == "Keyboard":
    user_input = st.chat_input("Type your English sentence here...")
    if user_input:
        # Xử lý logic
        score = fuzz.ratio(user_input.lower(), "i want to learn english") # Ví dụ so sánh
        
        # Tạo dữ liệu feedback mới
        st.session_state.current_response = {
            "user_text": user_input,
            "score": score,
            "feedback": "Great attempt! Your meaning is clear." if score > 50 else "Keep trying, focus on the sentence structure.",
            "advice": "Try to practice this sentence 3 more times to gain muscle memory."
        }
        play_audio("I heard you. That is a good sentence. Let's try more!")
        st.rerun()

else:
    audio_input = st.audio_input("Record your voice")
    if audio_input:
        with st.spinner("Analyzing voice..."):
            # Giả lập xử lý Speech-to-text
            time.sleep(1)
            # Code xử lý thực tế của bạn sẽ nằm ở đây
            st.success("Voice captured! (Vui lòng tích hợp speech_recognition để chuyển thành text)")

# Sidebar lịch sử
with st.sidebar:
    st.title("Progress")
    if st.session_state.current_response:
        st.write(f"Last score: {st.session_state.current_response['score']}%")
        st.progress(st.session_state.current_response['score'] / 100)
