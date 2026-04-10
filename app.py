import streamlit as st
import random
from gtts import gTTS
import io
import speech_recognition as sr
import google.generativeai as genai

# --- 1. CẤU HÌNH TRANG WEB & API ---
st.set_page_config(page_title="ESL Tutor Pro", page_icon="🎙️", layout="centered")

# Đã dán mã API Key của bạn
API_KEY = "AIzaSyCHTfFiNkF1tCWIY3qpNB3K1mudcFh8qlw" 

# Khởi tạo trực tiếp Gemini (đã bỏ lệnh if gây lỗi)
try:
    genai.configure(api_key=API_KEY)
    system_instruction = """
    You are 'ESL Elite', a friendly, native English tutor. Your goal is to help the user practice speaking.
    1. Respond naturally and enthusiastically.
    2. Keep your answers short (1-3 sentences) for easy listening.
    3. If the user makes a grammar mistake, gently point it out and correct it, then continue the chat.
    4. ONLY speak English.
    """
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction=system_instruction
    )
except Exception as e:
    model = None
    st.error(f"Lỗi khởi tạo API: {e}")

# --- 2. CSS TÙY CHỈNH (Giữ nguyên giao diện hiện đại) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif !important; }
        .stApp { background-color: #f8fafc; }
        .main-title { text-align: center; color: #1e293b; font-weight: 800; font-size: 3rem; margin-bottom: 5px; }
        .main-subtitle { text-align: center; color: #64748b; font-size: 1rem; font-weight: 500; margin-bottom: 30px; text-transform: uppercase; letter-spacing: 1px; }
        .stChatMessage { background-color: #ffffff !important; border-radius: 16px !important; border: 1px solid #e2e8f0 !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important; margin-bottom: 15px !important; }
        .record-card { background: #ffffff; border-radius: 20px; padding: 25px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0; text-align: center; margin-top: 20px; }
        [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0 !important; }
        .sidebar-logo-text { color: #2563eb; font-weight: 800; font-size: 1.5rem; text-align: center; margin-bottom: 20px; }
        .sidebar-section-title { color: #1e293b; font-weight: 600; font-size: 1rem; margin-top: 20px; margin-bottom: 8px; }
        .sidebar-info-text { color: #475569; font-size: 0.9rem; line-height: 1.5; }
        [data-testid="stSidebar"] button { background-color: #2563eb !important; color: white !important; border-radius: 10px !important; border: none !important; }
        div[data-testid="stAudioInput"] { border-radius: 12px; border: 2px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# --- 3. THANH SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='sidebar-logo-text'>ESL TUTOR PRO</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-section-title'>🧠 AI Engine</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-info-text'>Powered by Large Language Model (Generative AI)</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Làm mới cuộc hội thoại", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your AI English tutor. How is your day going?"}]
        if "chat_session" in st.session_state:
            del st.session_state.chat_session
        st.rerun()

# --- 4. GIAO DIỆN CHÍNH ---
st.markdown("<h1 class='main-title'>ESL AI TUTOR</h1>", unsafe_allow_html=True)
st.markdown("<div class='main-subtitle'>Smart Generative AI Partner</div>", unsafe_allow_html=True)

if model is None:
    st.stop()

# Hàm tạo giọng nói
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# --- 5. KHUNG CHAT & LỊCH SỬ LLM ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your AI English tutor. How is your day going?"}]

if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

chat_container = st.container(height=350, border=False)
with chat_container:
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# --- 6. KHU VỰC THU ÂM ---
st.markdown("<div class='record-card'>", unsafe_allow_html=True)
st.markdown("<h3 style='color: #1e293b; margin-bottom: 15px;'>🎙️ Chạm để giao tiếp</h3>", unsafe_allow_html=True)

user_message = None
user_audio = st.audio_input("", label_visibility="collapsed")

if user_audio:
    with st.spinner("Đang lắng nghe..."):
        r = sr.Recognizer()
        with sr.AudioFile(user_audio) as source:
            audio_data = r.record(source)
            try:
                recognized_text = r.recognize_google(audio_data, language="en-US")
                user_message = recognized_text
                st.success(f"**Bạn:** {recognized_text}")
            except:
                st.warning("Xin lỗi, tôi chưa nghe rõ. Bạn có thể nói lại không?")
st.markdown("</div>", unsafe_allow_html=True)

# --- 7. LOGIC PHẢN HỒI BẰNG LLM ---
if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})
    with chat_container:
        with st.chat_message("user", avatar="👤"): st.markdown(user_message)

    with chat_container:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("AI đang suy nghĩ..."):
                try:
                    response = st.session_state.chat_session.send_message(user_message)
                    bot_reply = response.text
                except Exception as e:
                    bot_reply = "I'm having a little trouble connecting to my brain right now. Could you repeat that?"
            
            st.markdown(bot_reply)
            st.audio(text_to_speech(bot_reply), format='audio/mp3', autoplay=True)
            
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
