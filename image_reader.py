import streamlit as st
import os
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="AI 圖片多輪對話助手", layout="wide")

st.title("🖼️ AI 圖片分析與多輪問答系統")
st.caption("支援圖片上傳、醫學影像描述與連續對話提問")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ 找不到 GEMINI_API_KEY 環境變數，請確認是否已 export。")
    st.stop()

# 初始化 session 狀態
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_image" not in st.session_state:
    st.session_state.current_image = None

# 左側上傳圖片
with st.sidebar:
    st.header("上傳圖片")
    uploaded_file = st.file_uploader("請選擇圖片 (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="已上傳圖片", use_container_width=True)
        
        # 更換新圖片時清空歷史紀錄
        if st.session_state.current_image != uploaded_file.name:
            st.session_state.current_image = uploaded_file.name
            st.session_state.messages = []
            st.success("圖片已就緒，請開始提問！")

# 顯示聊天歷史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 接收提問
if prompt := st.chat_input("對這張圖片提問（例如：請分析這張腦波/頻譜圖）..."):
    if uploaded_file is None:
        st.warning("⚠️ 請先在左側邊欄上傳圖片！")
    else:
        # 顯示使用者問題
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("AI 正在分析影像與問題..."):
                try:
                    # 每次請求建立 client 避免連線被釋放
                    client = genai.Client(api_key=api_key)
                    
                    # 組合對話歷史與圖片
                    contents = [image]
                    for msg in st.session_state.messages:
                        contents.append(f"{msg['role']}: {msg['content']}")

                    response = client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=contents
                    )
                    
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"發生錯誤：{e}")
