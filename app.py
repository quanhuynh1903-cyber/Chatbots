import streamlit as st
import pandas as pd
import numpy as np
import time

# --- 1. CẤU HÌNH TRANG WEB ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🤖", layout="wide")

# --- 2. CSS TÙY CHỈNH NÂNG CAO (Mô phỏng bản thiết kế) ---
st.markdown("""
<style>
    /* Reset nền và font */
    .stApp {
        background-color: #f0f4f8;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Ẩn menu mặc định của Streamlit cho giống App thật */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* --- SIDEBAR STYLING --- */
    [data-testid="stSidebar"] {
        background-color: #e5eaf0;
        padding-top: 1rem;
    }
    .robot-avatar-container {
        text-align: center;
        margin-bottom: 20px;
    }
    .robot-avatar {
        width: 150px;
        border-radius: 20px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        background: linear-gradient(145deg, #ffffff, #e6e6e6);
        padding: 10px;
    }
    
    /* Các thẻ (Cards) ở Sidebar */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.5);
    }
    .card-title {
        font-size: 14px;
        font-weight: bold;
        color: #334155;
        margin-bottom: 10px;
    }

    /* --- MAIN AREA STYLING --- */
    /* Thẻ Chat của AI */
    .ai-chat-bubble {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        margin-top: 20px;
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    /* Thẻ Feedback Tức thì (Giống y hệt ảnh) */
    .feedback-card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.08);
        width: 80%;
        margin: 0 auto;
        position: relative;
    }
    .feedback-title {
        font-size: 16px;
        font-weight: bold;
        color: #1e293b;
        margin-bottom: 15px;
    }
    
    /* Highlight màu từ vựng */
    .word-bad {
        background-color: #fed7aa; /* Màu cam nhạt */
        color: #c2410c;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
    }
    .word-good {
        background-color: #bbf7d0; /* Màu xanh nhạt */
        color: #15803d;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
    }
    
    /* Lưới điểm số (Scores Grid) */
    .score-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-top: 20px;
        font-size: 14px;
        color: #475569;
    }

    /* --- BOTTOM NEON MIC STYLING --- */
    .neon-mic-container {
        background: linear-gradient(90deg, #dbeafe, #e0e7ff, #f3e8ff);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin-top: 40px;
        box-shadow: inset 0 0 20px rgba(255,255,255,0.5);
        border: 1px solid #e2e8f0;
    }
    .mic-button-mockup {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: -40px auto 10px auto; /* Kéo nút mic lên trên một chút */
        box-shadow: 0 0 20px rgba(139, 92, 246, 0.6), 0 0 40px rgba(59, 130, 246, 0.4);
        font-size: 24px;
        border: 4px solid white;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. THANH SIDEBAR (Tương đương cột trái trong ảnh) ---
with st.sidebar:
    # Hình ảnh Robot 3D (Sử dụng link ảnh public có sẵn)
    st.markdown("""
        <div class="robot-avatar-container">
            <img class="robot-avatar" src="https://cdn-icons-png.flaticon.com/512/8649/8649603.png" alt="3D Robot">
        </div>
    """, unsafe_allow_html=True)
    
    # Ứng dụng Info
    st.markdown("""
        <div class="glass-card">
            <div class="card-title">✨ Về Ứng Dụng</div>
            <p style="font-size: 13px; color: #475569; margin: 0;">
                <strong style="color: #2563eb;">ESL AI Tutor</strong> nay đã được nâng cấp với 'bộ tai' siêu nhạy Whisper từ OpenAI, giúp nghe hiểu cả những phát âm chưa chuẩn xác nhất!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Biểu đồ Progress
    st.markdown('<div class="glass-card"><div class="card-title">📉 Your Speaking Progress</div><p style="font-size: 12px; color: gray; margin-bottom: 5px;">Weekly practice time (in min)</p>', unsafe_allow_html=True)
    chart_data = pd.DataFrame(np.array([2, 5, 4, 10, 15, 8, 12]), columns=['Minutes'])
    st.line_chart(chart_data, height=120)
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-top: 10px;">
            <div style="background-color: #0284c7; color: white; padding: 5px 10px; border-radius: 8px; font-weight: bold;">A2</div>
            <div>
                <div style="font-weight: bold; font-size: 14px; color: #1e293b;">Intermediate A2</div>
                <div style="color: #f59e0b; font-size: 12px;">⭐⭐⭐⭐⭐</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Gamification List
    st.markdown("""
        <div style="padding-left: 10px;">
            <p style="font-size: 14px; color: #334155; margin-bottom: 8px;">🔥 <strong>5-Day Streak</strong></p>
            <p style="font-size: 14px; color: #334155; margin-bottom: 8px;">🏅 <strong>Pronunciation Ace</strong></p>
            <p style="font-size: 14px; color: #334155;">⭐ <strong>Grammar Master</strong></p>
        </div>
    """, unsafe_allow_html=True)

    st.write("")
    if st.button("🔄 Xóa lịch sử & Bắt đầu lại", use_container_width=True):
        st.session_state.step = 0
        st.rerun()

# --- 4. KHU VỰC CHÍNH (MAIN AREA) ---

# Khởi tạo trạng thái mô phỏng
if "step" not in st.session_state:
    st.session_state.step = 0

# Thẻ Chat của AI ở trên cùng
st.markdown("""
    <div class="ai-chat-bubble">
        <span style="font-size: 24px;">🌐</span>
        <span style="color: #334155; font-size: 16px;">Hello! I am your AI English tutor. How can I help you practice today?</span>
    </div>
""", unsafe_allow_html=True)

# Hiển thị Thẻ Feedback sau khi thu âm
if st.session_state.step == 1:
    st.markdown("""
<div class="feedback-card">
    <div class="feedback-title">Instant Practice Feedback</div>
    <p style="color: #334155; font-size: 15px;">Your Sentence: 
        Can you <span class="word-bad">recommend</span> a <span class="word-good">good restaurant</span>?
    </p>
    <div class="score-grid">
        <div>
            <div>Pronunciation Score: <strong style="color: #10b981;">88%</strong></div>
            <div style="margin-top: 10px;">Herterode: <span style="color: #f59e0b;">⭐⭐⭐⭐☆</span></div>
            <div style="margin-top: 10px;">Grammar check: <strong style="color: #10b981;">Correct</strong></div>
        </div>
        <div>
            <div>Fluency: <span style="color: #f59e0b;">⭐⭐⭐⭐⭐</span></div>
            <div style="margin-top: 10px;">Grammar check: <strong style="color: #10b981;">Correct</strong></div>
        </div>
    </div>
</div>
    """, unsafe_allow_html=True)

# --- 5. KHU VỰC THU ÂM (Mô phỏng Neon Wave) ---
tab1, tab2 = st.tabs(["📝 Luyện Viết (Văn bản)", "🎙️ Luyện Nói (Giọng nói)"])

with tab2:
    # Vùng chứa mô phỏng sóng âm neon
    st.markdown("""
        <div class="neon-mic-container">
            <div class="mic-button-mockup">🎙️</div>
            <p style="color: #475569; font-size: 14px; margin-top: 10px; font-weight: 500;">
                💡 Nhấn vào micro (của Streamlit ở dưới), đọc một câu Tiếng Anh. AI Whisper siêu nhạy sẽ dịch giọng nói của bạn!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Nút thu âm thật của Streamlit (bắt buộc phải dùng cái này để lấy mic)
    user_audio = st.audio_input("Thu âm", label_visibility="collapsed")
    
    if user_audio:
        with st.spinner("Đang phân tích..."):
            time.sleep(2)
            st.session_state.step = 1
            st.rerun()
