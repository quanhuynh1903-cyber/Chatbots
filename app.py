import streamlit as st
import pandas as pd
import joblib
import random

# --- 1. Cấu hình giao diện trang web ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🎓", layout="centered")

# --- 2. Thiết kế Sidebar (Trình đơn bên trái) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100) # Icon minh họa
    st.title("Về Ứng Dụng")
    st.markdown("""
    **ESL AI Tutor** là chatbot hỗ trợ luyện nói tiếng Anh.
    
    **Các chủ đề hỗ trợ:**
    - 👋 Giao tiếp cơ bản
    - 🗣️ Sửa lỗi phát âm
    - 📝 Chữa lỗi ngữ pháp
    - 🎭 Đóng vai (Nhà hàng, Sân bay, Phỏng vấn...)
    
    *Dự án được xây dựng bằng Python, Scikit-Learn và Streamlit.*
    """)
    st.divider()
    if st.button("Xóa lịch sử trò chuyện"):
        st.session_state.messages = []
        st.rerun()

# --- 3. Thiết kế Phần chính (Main Area) ---
st.title("🎓 Trợ Lý Luyện Nói Tiếng Anh AI")
st.caption("Hãy gõ tiếng Anh để bắt đầu trò chuyện. Bạn có thể yêu cầu đóng vai, hỏi ngữ pháp hoặc cách phát âm!")

# --- 4. Tải Dữ liệu & Mô hình ---
@st.cache_resource
def load_data_and_model():
    # Tải file model và dataset
    df = pd.read_csv('10000_esl_dataset.csv')
    model = joblib.load('esl_model.pkl')
    return df, model

try:
    df, model = load_data_and_model()
except Exception as e:
    st.error(f"Lỗi tải dữ liệu: {e}. Vui lòng kiểm tra lại file .pkl và .csv")
    st.stop()

# --- 5. Xử lý Logic Trò chuyện ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI English tutor. How can I help you practice today?"}]

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nhận tin nhắn mới từ người dùng
if user_input := st.chat_input("Type your message here..."):
    # Hiện tin nhắn User
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # AI Phản hồi
    with st.chat_message("assistant"):
        predicted_intent = model.predict([user_input])[0]
        possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
        bot_reply = random.choice(possible_responses)
        
        st.markdown(bot_reply)
    
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
