import os
import streamlit as st
from pypdf import PdfReader
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.set_page_config(page_title="AI 論文快速解讀工具", layout="wide")
st.title("📚 AI 論文快速解讀工具 (Gemini 3.5 Flash)")

# 側邊欄設定
st.sidebar.header("設定")
env_key = os.getenv("GEMINI_API_KEY", "")

api_key = st.sidebar.text_input(
    "Gemini API Key",
    value=env_key,
    type="password",
    help="金鑰優先從 .env 讀取，亦可在此手動輸入。"
)

uploaded_file = st.file_uploader("請拖曳或上傳論文 PDF", type=["pdf"])

if uploaded_file is not None:
    reader = PdfReader(uploaded_file)
    paper_text = "".join([page.extract_text() or "" for page in reader.pages])

    st.success(f"已成功讀取檔案：{uploaded_file.name}（共 {len(reader.pages)} 頁）")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("🚀 生成論文結構化摘要"):
            if not api_key:
                st.error("請先在側邊欄輸入有效的 Gemini API Key！")
            else:
                with st.spinner("Gemini 3.5 Flash 正在分析論文重點..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        summary_prompt = f"""請根據以下論文內容，使用繁體中文條列式回答：
1. 研究目的與核心假說
2. 研究方法、收案對象與分析工具
3. 主要研究結果與結論

論文內容：
{paper_text}"""
                        response = client.models.generate_content(
                            model="gemini-3.5-flash",
                            contents=summary_prompt
                        )
                        st.markdown("### 📋 論文分析摘要")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"分析失敗：{e}")

    with col2:
        st.subheader("💬 針對本篇論文提問")
        user_question = st.text_input("輸入你想詢問這篇論文的問題：")
        if st.button("送出提問"):
            if not api_key:
                st.error("請先在側邊欄輸入有效的 Gemini API Key！")
            elif not user_question:
                st.warning("請先輸入問題！")
            else:
                with st.spinner("Gemini 3.5 Flash 正在查詢論文內容..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        qa_prompt = f"""請僅根據以下論文內容，用繁體中文回答使用者的問題。如果論文中沒有提及相關資訊，請誠實說明。

論文內容：
{paper_text}

問題：{user_question}"""
                        response = client.models.generate_content(
                            model="gemini-3.5-flash",
                            contents=qa_prompt
                        )
                        st.markdown("### 💡 回答")
                        st.write(response.text)
                    except Exception as e:
                        st.error(f"查詢失敗：{e}")
