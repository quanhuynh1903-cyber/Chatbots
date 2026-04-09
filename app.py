import streamlit as st
import pandas as pd
import joblib
import random
from gtts import gTTS
import io
import speech_recognition as sr

# --- 1. Cấu hình giao diện trang web ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🎓", layout="centered")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("Về Ứng Dụng")
    st.markdown("""
    **ESL AI Tutor** là chatbot hỗ trợ luyện nói tiếng Anh toàn diện.
    
    **Tính năng nổi bật:**
    - 🎤 Ghi âm giọng nói trực tiếp
    - 🎧 AI phản hồi bằng âm thanh (Text-to-Speech)
    - 📝 Tự động nhận diện lỗi sai
    """)
    st.divider()
    if st.button("Xóa lịch sử trò chuyện"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI English tutor. How can I help you practice today?"}]
        st.rerun()

st.title("🎓 Trợ Lý Luyện Nói Tiếng Anh AI")
st.caption("Bạn có thể gõ phím HOẶC bấm vào biểu tượng Micro bên dưới để nói chuyện trực tiếp nhé!")

# --- 2. Tải Dữ liệu & Mô hình ---
@st.cache_resource
def load_data_and_model():
    df = pd.read_csv('10000_esl_dataset.csv')
    model = joblib.load('esl_model.pkl')
    return df, model

try:
    df, model = load_data_and_model()
except Exception as e:
    st.error("Lỗi tải dữ liệu. Vui lòng kiểm tra lại file .pkl và .csv")
    st.stop()

# --- 3. Hàm tạo giọng nói cho Bot (Text-to-Speech) ---
def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# --- 4. Logic Hội thoại ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI English tutor. How can I help you practice today?"}]

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. Khu vực Nhập liệu (Gõ phím HOẶC Ghi âm) ---
user_message = None

# Giao diện cho phép chọn 1 trong 2 cách nhập
col1, col2 = st.columns([1, 1])
with col1:
    user_text = st.chat_input("Gõ tin nhắn của bạn...")
with col2:
    # Nút ghi âm trực tiếp của Streamlit
    user_audio = st.audio_input("🎙️ Nhấn để thu âm")

# Xử lý nếu người dùng gõ phím
if user_text:
    user_message = user_text

# Xử lý nếu người dùng gửi file ghi âm
elif user_audio:
    with st.spinner("Đang nghe giọng của bạn..."):
        r = sr.Recognizer()
        # Đọc file âm thanh người dùng vừa ghi
        with sr.AudioFile(user_audio) as source:
            audio_data = r.record(source)
            try:
                # Nhờ Google dịch giọng nói thành chữ (Tiếng Anh)
                recognized_text = r.recognize_google(audio_data, language="en-US")
                user_message = recognized_text
            except sr.UnknownValueError:
                st.warning("Xin lỗi, tôi nghe không rõ. Bạn có thể nói lại hoặc gõ phím được không?")
            except sr.RequestError:
                st.error("Lỗi dịch vụ nhận diện giọng nói. Vui lòng kiểm tra kết nối mạng.")

# --- 6. AI Phản hồi ---
if user_message:
    # 6.1 Hiển thị tin nhắn User
    with st.chat_message("user"):
        st.markdown(f"*{user_message}*") # In nghiêng để nhận biết
    st.session_state.messages.append({"role": "user", "content": f"*{user_message}*"})

    # 6.2 AI Xử lý và Trả lời
    with st.chat_message("assistant"):
        # Phân tích ý định
        predicted_intent = model.predict([user_message])[0]
        possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
        bot_reply = random.choice(possible_responses)
        
        # In chữ ra màn hình
        st.markdown(bot_reply)
        
        # Phát âm thanh phản hồi
        audio_bytes = text_to_speech(bot_reply)
        st.audio(audio_bytes, format='audio/mp3', autoplay=True)
    
    # Lưu vào lịch sử
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
