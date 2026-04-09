import streamlit as st
import pandas as pd
import joblib
import random
from gtts import gTTS
import io
import whisper # 🟢 Nhập thư viện Whisper mới
import os

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🇬🇧", layout="centered")

st.markdown("""
    <style>
    .main-title { text-align: center; color: #2E86C1; font-family: 'Arial Black', sans-serif; }
    .sub-title { text-align: center; color: #808B96; font-size: 16px; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. THANH SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=120)
    st.markdown("### 🌟 Về Ứng Dụng")
    st.info("**ESL AI Tutor** nay đã được nâng cấp với "bộ tai" siêu nhạy Whisper từ OpenAI, giúp nghe hiểu cả những phát âm chưa chuẩn xác nhất!")
    st.divider()
    if st.button("🔄 Xóa lịch sử & Bắt đầu lại", use_container_width=True, type="primary"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI English tutor. How can I help you practice today?"}]
        st.rerun()

st.markdown("<h1 class='main-title'>🎓 ESL AI TUTOR</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Trợ lý Luyện nghe - nói Tiếng Anh Thông minh (Powered by Whisper)</div>", unsafe_allow_html=True)

# --- 3. TẢI DỮ LIỆU & MODEL CHAT ---
@st.cache_resource
def load_data_and_model():
    df = pd.read_csv('10000_esl_dataset.csv')
    model = joblib.load('esl_model.pkl')
    return df, model

try:
    df, model = load_data_and_model()
except Exception as e:
    st.error("Lỗi tải dữ liệu. Vui lòng kiểm tra lại file trên GitHub!")
    st.stop()

# --- 4. 🟢 TẢI MODEL WHISPER (Tải 1 lần để web không bị chậm) ---
@st.cache_resource
def load_whisper_model():
    # Sử dụng model "base" (nhỏ gọn, đủ thông minh và phù hợp với RAM của Streamlit)
    return whisper.load_model("base")

whisper_model = load_whisper_model()

# Hàm tạo giọng nói AI (Text-to-Speech)
def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# --- 5. HIỂN THỊ LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI English tutor. How can I help you practice today?"}]

chat_container = st.container(height=450, border=True)
with chat_container:
    for message in st.session_state.messages:
        avatar_icon = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])

st.write("") 

# --- 6. KHU VỰC NHẬP LIỆU (TABS) ---
tab1, tab2 = st.tabs(["⌨️ Luyện Viết (Văn bản)", "🎙️ Luyện Nói (Giọng nói)"])
user_message = None

# TAB 1: GIAO DIỆN GÕ VĂN BẢN
with tab1:
    with st.form("text_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_text = st.text_input("Gõ tin nhắn Tiếng Anh...", label_visibility="collapsed")
        with col_btn:
            submit_text = st.form_submit_button("Gửi 🚀", use_container_width=True)
        if submit_text and user_text.strip() != "":
            user_message = user_text

# TAB 2: 🟢 GIAO DIỆN THU ÂM (SỬ DỤNG WHISPER)
with tab2:
    st.info("💡 Nhấn vào micro, đọc một câu Tiếng Anh. AI Whisper siêu nhạy sẽ dịch giọng nói của bạn!")
    user_audio = st.audio_input("Nhấn để thu âm", label_visibility="collapsed")
    
    if user_audio:
        with st.spinner("🎧 Whisper đang phân tích giọng nói của bạn..."):
            # Lưu file âm thanh do trình duyệt thu được thành 1 file tạm thời trên máy chủ
            temp_audio_path = "temp_user_audio.wav"
            with open(temp_audio_path, "wb") as f:
                f.write(user_audio.read())
            
            try:
                # Nhờ Whisper nghe và chuyển thành chữ (chỉ định nghe tiếng Anh)
                result = whisper_model.transcribe(temp_audio_path, language="en")
                user_message = result["text"]
            except Exception as e:
                st.error(f"⚠️ Có lỗi xảy ra khi phân tích giọng nói: {e}")
            finally:
                # Dọn dẹp: Xóa file tạm sau khi nghe xong để nhẹ máy chủ
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)

# --- 7. XỬ LÝ LOGIC AI TRẢ LỜI ---
if user_message:
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    with chat_container:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_message)

    with chat_container:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤖 AI đang suy nghĩ..."):
                predicted_intent = model.predict([user_message])[0]
                possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
                bot_reply = random.choice(possible_responses)
            
            st.markdown(bot_reply)
            
            audio_bytes = text_to_speech(bot_reply)
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
            
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
