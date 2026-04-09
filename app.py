import streamlit as st
import pandas as pd
import joblib
import random
from gtts import gTTS
import io
import speech_recognition as sr

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(
    page_title="ESL AI Tutor", 
    page_icon="🎓", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- THÊM CSS TÙY CHỈNH CHO GIAO DIỆN HIỆN ĐẠI ---
st.markdown("""
    <style>
        /* Tiêu đề chính với hiệu ứng Gradient */
        .main-title {
            text-align: center;
            background: -webkit-linear-gradient(45deg, #00C9FF 0%, #92FE9D 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-family: 'Nunito', 'Segoe UI', sans-serif;
            font-weight: 900;
            font-size: 3.2rem;
            margin-bottom: -10px;
        }
        /* Phụ đề */
        .sub-title {
            text-align: center;
            color: #6c757d;
            font-size: 1.1rem;
            font-weight: 500;
            margin-bottom: 30px;
            letter-spacing: 0.5px;
        }
        /* Làm đẹp phần thu âm */
        .record-section {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #e9ecef;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. THANH SIDEBAR (Menu bên trái) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=150, use_container_width=True)
    st.markdown("<h2 style='text-align: center; color: #2E86C1;'>ESL AI Tutor</h2>", unsafe_allow_html=True)
    
    st.markdown("### 🌟 Về Ứng Dụng")
    st.info("Trợ lý ảo giúp bạn tự tin giao tiếp Tiếng Anh. Hãy bật micro lên và bắt đầu trò chuyện ngay!")
    
    st.markdown("### 💡 Mẹo Luyện Nói")
    st.success("""
    - **Nghe kỹ:** Lắng nghe phát âm của AI.
    - **Nói to, rõ:** Giúp hệ thống nhận diện tốt hơn.
    - **Đừng sợ sai:** AI luôn ở đây để giúp bạn!
    """)
    
    st.divider()
    
    # Nút làm mới giao diện 
    if st.button("🔄 Bắt đầu cuộc hội thoại mới", use_container_width=True, type="primary"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello there! I'm your AI English tutor. I'm ready to listen, what would you like to talk about?"}]
        st.toast('Đã làm mới cuộc trò chuyện!', icon='✨')
        st.rerun()

# --- 3. GIAO DIỆN CHÍNH (Header) ---
st.markdown("<h1 class='main-title'>ESL AI TUTOR</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Trợ lý Luyện Nghe & Nói Tiếng Anh Thông Minh 🎙️</div>", unsafe_allow_html=True)

# --- 4. TẢI DỮ LIỆU & MODEL ---
@st.cache_resource
def load_data_and_model():
    # Đã sửa lại tên file mới
    df = pd.read_csv('cleaned_esl_dataset.csv')
    model = joblib.load('esl_model.pkl')
    return df, model

try:
    df, model = load_data_and_model()
except Exception as e:
    st.error("⚠️ Lỗi tải dữ liệu. Vui lòng kiểm tra lại file .pkl và .csv!")
    st.stop()

# Hàm tạo giọng nói AI
def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

# --- 5. HIỂN THỊ LỊCH SỬ KHUNG CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello there! I'm your AI English tutor. I'm ready to listen, what would you like to talk about?"}]

# Vùng chứa khung chat
chat_container = st.container(height=380, border=True)
with chat_container:
    for message in st.session_state.messages:
        avatar_icon = "👤" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])

# --- 6. KHU VỰC THU ÂM (TRỰC TIẾP Ở MÀN HÌNH CHÍNH) ---
st.markdown("<div class='record-section'>", unsafe_allow_html=True)
st.markdown("### 🎙️ Đến lượt bạn nói...")
st.caption("✨ Nhấn vào biểu tượng micro bên dưới, đọc một câu Tiếng Anh, hệ thống sẽ tự động chuyển thành văn bản và phản hồi.")

user_message = None
user_audio = st.audio_input("Nhấn để thu âm", label_visibility="collapsed")

if user_audio:
    with st.spinner("🎧 Đang phân tích giọng nói..."):
        r = sr.Recognizer()
        with sr.AudioFile(user_audio) as source:
            audio_data = r.record(source)
            try:
                # Nhận diện giọng nói Tiếng Anh
                recognized_text = r.recognize_google(audio_data, language="en-US")
                user_message = recognized_text
                st.success(f"🗣️ **Bạn vừa nói:** *'{recognized_text}'*")
            except sr.UnknownValueError:
                st.error("⚠️ Xin lỗi, hệ thống nghe không rõ. Bạn hãy thử nói to và rõ chữ hơn nhé!")
            except sr.RequestError:
                st.error("⚠️ Lỗi kết nối máy chủ giọng nói.")
st.markdown("</div>", unsafe_allow_html=True)

# --- 7. XỬ LÝ LOGIC AI TRẢ LỜI ---
if user_message:
    # 7.1 Lưu tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Hiển thị tạm thời tin nhắn người dùng
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_message)

    # 7.2 AI Xử lý và Phản hồi
    with chat_container:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤖 Đang suy nghĩ..."):
                try:
                    # Phân tích ý định và tìm câu trả lời
                    predicted_intent = model.predict([user_message])[0]
                    possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
                    bot_reply = random.choice(possible_responses)
                except Exception as e:
                    bot_reply = "I'm sorry, I couldn't understand that perfectly. Could you try saying it again?"
            
            # In câu trả lời ra màn hình
            st.markdown(bot_reply)
            
            # Đọc câu trả lời bằng giọng nói
            audio_bytes = text_to_speech(bot_reply)
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
            
    # Lưu câu trả lời vào bộ nhớ
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
