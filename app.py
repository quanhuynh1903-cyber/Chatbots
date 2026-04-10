import streamlit as st
import pandas as pd
import joblib
import random
from gtts import gTTS
import io
import speech_recognition as sr

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="ESL Tutor Pro", 
    page_icon="🎙️", 
    layout="centered"
)

# --- 2. CSS TÙY CHỈNH (PHONG CÁCH SOFT LIGHT) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        /* Nền trắng xanh dịu nhẹ */
        .stApp {
            background-color: #f8fafc;
        }

        /* Tiêu đề chính: Xanh dương đậm & mạnh mẽ */
        .main-title {
            text-align: center;
            color: #1e293b;
            font-weight: 800;
            font-size: 3rem;
            margin-bottom: 5px;
            letter-spacing: -1px;
        }

        .main-subtitle {
            text-align: center;
            color: #64748b;
            font-size: 1rem;
            font-weight: 500;
            margin-bottom: 30px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Khung Chat: Trắng thuần khiết, đổ bóng mềm */
        .stChatMessage {
            background-color: #ffffff !important;
            border-radius: 16px !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            margin-bottom: 15px !important;
        }

        /* Card Thu âm: Nổi bật và sạch sẽ */
        .record-card {
            background: #ffffff;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            border: 1px solid #e2e8f0;
            text-align: center;
            margin-top: 20px;
        }

        /* --- TÙY CHỈNH SIDEBAR MỚI (DỄ NHÌN HƠN) --- */
        [data-testid="stSidebar"] {
            background-color: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
        }
        
        .sidebar-logo-text { color: #2563eb; font-weight: 800; font-size: 1.5rem; text-align: center; margin-bottom: 20px; }
        .sidebar-section-title { color: #1e293b; font-weight: 600; font-size: 1rem; margin-top: 20px; margin-bottom: 8px; }
        .sidebar-info-text { color: #475569; font-size: 0.9rem; line-height: 1.5; }
        .sidebar-icon { color: #2563eb; margin-right: 8px; }
        
        /* Nút bấm Sidebar: Xanh dương chuyên nghiệp */
        [data-testid="stSidebar"] button {
            background-color: #2563eb !important;
            color: white !important;
            border-radius: 10px !important;
            border: none !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: #1d4ed8 !important;
            transform: translateY(-1px);
        }

        /* Tùy chỉnh Audio Input */
        div[data-testid="stAudioInput"] {
            border-radius: 12px;
            border: 2px solid #e2e8f0;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. THANH SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-top: 10px;'>
            <img src='https://cdn-icons-png.flaticon.com/512/3242/3242257.png' width='60' style='margin-bottom: 10px;'>
        </div>
        <div class='sidebar-logo-text'>ESL TUTOR PRO</div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-title'>📘 Giới thiệu</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-info-text'>Ứng dụng hỗ trợ luyện nói Tiếng Anh với phản hồi tức thì từ AI.</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-title'>🚀 Mục tiêu</div>", unsafe_allow_html=True)
    st.markdown("""
        <div class='sidebar-info-text'>
            <p><span class='sidebar-icon'>●</span> Phản xạ tự nhiên</p>
            <p><span class='sidebar-icon'>●</span> Phát âm chuẩn xác</p>
            <p><span class='sidebar-icon'>●</span> Tự tin giao tiếp</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Làm mới cuộc hội thoại", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm ready for our new session. What shall we talk about?"}]
        st.rerun()

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown("<h1 class='main-title'>ESL AI TUTOR</h1>", unsafe_allow_html=True)
st.markdown("<div class='main-subtitle'>Your Smart Language Partner</div>", unsafe_allow_html=True)

# --- 5. TẢI DỮ LIỆU ---
@st.cache_resource
def load_assets():
    df = pd.read_csv('cleaned_esl_dataset.csv')
    model = joblib.load('esl_model.pkl')
    return df, model

try:
    df, model = load_assets()
except:
    st.error("⚠️ Vui lòng kiểm tra file dữ liệu.")
    st.stop()

def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# --- 6. KHUNG CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your English partner. How can I help you today?"}]

chat_container = st.container(height=350, border=False)
with chat_container:
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# --- 7. KHU VỰC THU ÂM ---
st.markdown("<div class='record-card'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1e293b; margin-bottom: 15px;'>🎙️ Chạm để bắt đầu nói</h3>", unsafe_allow_html=True)

user_message = None
user_audio = st.audio_input("", label_visibility="collapsed")

if user_audio:
    with st.spinner("Đang phân tích..."):
        r = sr.Recognizer()
        with sr.AudioFile(user_audio) as source:
            audio_data = r.record(source)
            try:
                recognized_text = r.recognize_google(audio_data, language="en-US")
                user_message = recognized_text
                st.success(f"**Bạn đã nói:** {recognized_text}")
            except:
                st.warning("Tôi chưa nghe rõ, bạn nói lại nhé?")
st.markdown("</div>", unsafe_allow_html=True)

# --- 8. LOGIC PHẢN HỒI ---
if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})
    with chat_container:
        with st.chat_message("user", avatar="👤"): st.markdown(user_message)

    with chat_container:
        with st.chat_message("assistant", avatar="🤖"):
            try:
                predicted_intent = model.predict([user_message])[0]
                possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
                bot_reply = random.choice(possible_responses)
            except:
                bot_reply = "Interesting! Tell me more about that."
            
            st.markdown(bot_reply)
            st.audio(text_to_speech(bot_reply), format='audio/mp3', autoplay=True)
            
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
