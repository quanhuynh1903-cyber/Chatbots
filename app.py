import streamlit as st
import pandas as pd
import joblib
import random
from gtts import gTTS
import io

# --- 1. Cấu hình giao diện trang web ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🎓", layout="centered")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("Về Ứng Dụng")
    st.markdown("""
    **ESL AI Tutor** đã được nâng cấp tính năng Phát âm thanh (Text-to-Speech).
    
    **💡 Mẹo luyện Speaking:**
    Thay vì gõ phím, hãy sử dụng tính năng nhập bằng giọng nói (Voice Typing) của bàn phím để luyện phát âm!
    """)
    st.divider()
    if st.button("Xóa lịch sử trò chuyện"):
        st.session_state.messages = []
        st.rerun()

st.title("🎓 Trợ Lý Luyện Nói Tiếng Anh AI")
st.caption("Sử dụng Voice Typing trên bàn phím để nói chuyện với Bot nhé!")

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

# --- 3. Hàm tạo giọng nói cho Bot ---
def text_to_speech(text):
    # Tạo âm thanh từ văn bản, ngôn ngữ tiếng Anh ('en')
    tts = gTTS(text=text, lang='en', slow=False)
    # Lưu vào bộ nhớ tạm thay vì lưu thành file cứng trong máy
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# --- 4. Xử lý Logic Trò chuyện ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI English tutor. How can I help you practice today?"}]

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nhận tin nhắn mới từ người dùng
if user_input := st.chat_input("Type or Speak your message here..."):
    # Hiện tin nhắn User
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI Phản hồi
    with st.chat_message("assistant"):
        # Dự đoán ý định
        predicted_intent = model.predict([user_input])[0]
        possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
        bot_reply = random.choice(possible_responses)
        
        # In chữ ra màn hình
        st.markdown(bot_reply)
        
        # 🟢 TẠO VÀ PHÁT ÂM THANH NGAY BÊN DƯỚI CÂU TRẢ LỜI 🟢
        audio_bytes = text_to_speech(bot_reply)
        st.audio(audio_bytes, format='audio/mp3', autoplay=True)
    
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
