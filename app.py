import streamlit as st
import pandas as pd
import joblib
import random
from gtts import gTTS
import io
import speech_recognition as sr

# --- 1. CẤU HÌNH TRANG WEB (Tạo màu sắc và tiêu đề) ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🇬🇧", layout="centered")

# Thêm CSS tùy chỉnh để làm đẹp giao diện
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #2E86C1;
        font-family: 'Arial Black', sans-serif;
    }
    .sub-title {
        text-align: center;
        color: #808B96;
        font-size: 16px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. THANH SIDEBAR (Menu bên trái) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=120)
    st.markdown("### 🌟 Về Ứng Dụng")
    st.info("""
    **ESL AI Tutor** là người bạn đồng hành giúp bạn tự tin giao tiếp Tiếng Anh.
    
    Hãy chọn phương thức bạn muốn luyện tập ở màn hình chính!
    """)
    st.divider()
    
    # Nút làm mới giao diện rất đẹp
    if st.button("🔄 Xóa lịch sử & Bắt đầu lại", use_container_width=True, type="primary"):
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI English tutor. How can I help you practice today?"}]
        st.rerun()

# --- 3. GIAO DIỆN CHÍNH (Header) ---
st.markdown("<h1 class='main-title'>🎓 ESL AI TUTOR</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Trợ lý Luyện nghe - nói Tiếng Anh Thông minh</div>", unsafe_allow_html=True)

# --- 4. TẢI DỮ LIỆU & MODEL ---
@st.cache_resource
def load_data_and_model():
    df = pd.read_csv('10000_esl_dataset.csv')
    model = joblib.load('esl_model.pkl')
    return df, model

try:
    df, model = load_data_and_model()
except Exception as e:
    st.error("Lỗi tải dữ liệu. Vui lòng kiểm tra lại file .pkl và .csv trên GitHub!")
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
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI English tutor. How can I help you practice today?"}]

# Vùng chứa khung chat để nó nằm tách biệt với phần nhập liệu
chat_container = st.container(height=450, border=True)
with chat_container:
    for message in st.session_state.messages:
        # Thay đổi icon avatar cho đẹp
        avatar_icon = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar_icon):
            st.markdown(message["content"])

st.write("") # Tạo khoảng trắng

# --- 6. KHU VỰC NHẬP LIỆU (CHIA 2 TABS RÕ RÀNG) ---
# Tạo 2 Tabs: 1 cho Văn bản, 1 cho Giọng nói
tab1, tab2 = st.tabs(["⌨️ Luyện Viết (Văn bản)", "🎙️ Luyện Nói (Giọng nói)"])

user_message = None

# TAB 1: GIAO DIỆN GÕ VĂN BẢN
with tab1:
    with st.form("text_form", clear_on_submit=True):
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            user_text = st.text_input("Gõ tin nhắn Tiếng Anh của bạn vào đây...", label_visibility="collapsed")
        with col_btn:
            submit_text = st.form_submit_button("Gửi 🚀", use_container_width=True)
            
        if submit_text and user_text.strip() != "":
            user_message = user_text

# TAB 2: GIAO DIỆN THU ÂM TRỰC TIẾP
with tab2:
    st.info("💡 Nhấn vào biểu tượng micro bên dưới, đọc một câu Tiếng Anh, sau đó hệ thống sẽ tự động dịch và gửi cho AI.")
    user_audio = st.audio_input("Nhấn để thu âm", label_visibility="collapsed")
    
    if user_audio:
        with st.spinner("🎧 Đang phân tích giọng nói của bạn..."):
            r = sr.Recognizer()
            with sr.AudioFile(user_audio) as source:
                audio_data = r.record(source)
                try:
                    # Nhận diện giọng nói Tiếng Anh
                    recognized_text = r.recognize_google(audio_data, language="en-US")
                    user_message = recognized_text
                except sr.UnknownValueError:
                    st.warning("⚠️ Xin lỗi, hệ thống nghe không rõ. Bạn hãy nói to và rõ chữ hơn nhé!")
                except sr.RequestError:
                    st.error("⚠️ Lỗi kết nối máy chủ giọng nói.")

# --- 7. XỬ LÝ LÝ LOGIC AI TRẢ LỜI ---
if user_message:
    # 7.1 Lưu tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Hiển thị tạm thời tin nhắn người dùng (sẽ chui vào hộp chat ở lần load sau)
    with chat_container:
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_message)

    # 7.2 AI Xử lý và Phản hồi
    with chat_container:
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("🤖 AI đang suy nghĩ..."):
                # Phân tích ý định và tìm câu trả lời
                predicted_intent = model.predict([user_message])[0]
                possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
                bot_reply = random.choice(possible_responses)
            
            # In câu trả lời ra màn hình
            st.markdown(bot_reply)
            
            # Đọc câu trả lời bằng giọng nói
            audio_bytes = text_to_speech(bot_reply)
            st.audio(audio_bytes, format='audio/mp3', autoplay=True)
            
    # Lưu câu trả lời vào bộ nhớ
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
