import streamlit as st
import pandas as pd
import joblib
import random
from gtts import gTTS
import io
import speech_recognition as sr
from fuzzywuzzy import fuzz # Thêm thư viện so sánh chuỗi

# --- 1. Cấu hình giao diện ---
st.set_page_config(page_title="ESL AI Tutor", page_icon="🎓", layout="centered")

# CSS để hiển thị màu sắc cho từ đúng/sai
st.markdown("""
<style>
    .correct { color: #155724; background-color: #d4edda; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
    .incorrect { color: #721c24; background-color: #f8d7da; padding: 2px 5px; border-radius: 3px; font-weight: bold; }
    .score-box { border: 1px solid #dee2e6; padding: 15px; border-radius: 10px; background-color: #f8f9fa; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 2. Hàm đánh giá phát âm ---
def evaluate_pronunciation(user_text, predicted_intent, df):
    # Lấy một câu mẫu chuẩn trong dataset thuộc cùng Intent để làm mốc so sánh
    sample_targets = df[df['Intent'] == predicted_intent]['User_Input'].tolist()
    if not sample_targets:
        return None
    
    target_text = random.choice(sample_targets).lower().strip()
    user_text_clean = user_text.lower().strip()
    
    # Tính điểm tương đồng (%)
    score = fuzz.ratio(target_text, user_text_clean)
    
    # So sánh từng từ để highlight
    target_words = target_text.split()
    user_words = user_text_clean.split()
    
    evaluated_html = ""
    for word in user_words:
        if word in target_words:
            evaluated_html += f'<span class="correct">{word}</span> '
        else:
            evaluated_html += f'<span class="incorrect">{word}</span> '
            
    return {"score": score, "html": evaluated_html, "target": target_text}

# --- 3. Tải Dữ liệu & Mô hình ---
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

def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_data = io.BytesIO()
    tts.write_to_fp(audio_data)
    audio_data.seek(0)
    return audio_data

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your AI English tutor. How can I help you practice today?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# --- 4. Nhập liệu ---
user_message = None
is_audio = False

col1, col2 = st.columns([1, 1])
with col1:
    user_text = st.chat_input("Gõ tin nhắn của bạn...")
with col2:
    user_audio = st.audio_input("🎙️ Nhấn để thu âm")

if user_text:
    user_message = user_text
elif user_audio:
    with st.spinner("Đang nghe giọng của bạn..."):
        r = sr.Recognizer()
        with sr.AudioFile(user_audio) as source:
            audio_data = r.record(source)
            try:
                user_message = r.recognize_google(audio_data, language="en-US")
                is_audio = True # Đánh dấu là dùng giọng nói để đánh giá
            except:
                st.warning("Xin lỗi, tôi nghe không rõ.")

# --- 5. AI Phản hồi & Đánh giá ---
if user_message:
    # Dự đoán Intent trước để lấy dữ liệu so sánh
    predicted_intent = model.predict([user_message])[0]
    
    # Nếu dùng giọng nói, hiển thị bảng đánh giá trước
    if is_audio:
        eval_result = evaluate_pronunciation(user_message, predicted_intent, df)
        if eval_result:
            with st.expander("📊 Bảng đánh giá phát âm chi tiết", expanded=True):
                st.markdown(f"""
                <div class="score-box">
                    <h4>Độ chính xác: <b>{eval_result['score']}%</b></h4>
                    <p><b>Phân tích:</b> {eval_result['html']}</p>
                    <p><small><i>(Từ màu đỏ có thể bạn đã phát âm sai hoặc thiếu chữ)</i></small></p>
                </div>
                """, unsafe_allow_html=True)

    with st.chat_message("user"):
        st.markdown(f"*{user_message}*")
    st.session_state.messages.append({"role": "user", "content": f"*{user_message}*"})

    with st.chat_message("assistant"):
        possible_responses = df[df['Intent'] == predicted_intent]['Bot_Response'].tolist()
        bot_reply = random.choice(possible_responses)
        st.markdown(bot_reply)
        st.audio(text_to_speech(bot_reply), format='audio/mp3', autoplay=True)
    
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
