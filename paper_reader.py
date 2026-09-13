import streamlit as st
import os
import tempfile
from google import genai

st.set_page_config(page_title="PDF 論文閱讀助手", layout="wide")

st.title("📄 AI 論文閱讀與分析系統")
st.caption("基於 Gemini 與 Streamlit 的學術論文智慧摘要工具")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ 找不到 GEMINI_API_KEY 環境變數，請確認是否已在終端機中 export。")
    st.stop()

client = genai.Client(api_key=api_key)

uploaded_file = st.file_uploader("請上傳 PDF 論文檔案", type=["pdf"])

if uploaded_file is not None:
    st.info(f"已選擇檔案：{uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
    
    if st.button("🚀 開始分析論文", type="primary"):
        with st.spinner("正在上傳並使用 Gemini 分析論文，請稍候..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            try:
                # 使用 Gemini File API 上傳 PDF
                uploaded_doc = client.files.upload(file=tmp_path)

                prompt = """
                請詳細閱讀並深入分析這篇論文，以繁體中文整理出結構清晰的重點報告：
                
                ### 1. 論文摘要 (Executive Summary)
                - 核心研究問題與動機
                - 總體摘要概述
                
                ### 2. 研究方法 (Methodology)
                - 實驗設計、資料集或使用工具
                - 核心技術/演算法架構
                
                ### 3. 主要發現 (Key Findings)
                - 關鍵實驗數據與成果
                - 與現有方法的比較
                
                ### 4. 限制與未來方向 (Limitations & Future Work)
                - 本研究之限制
                - 潛在未來改進或延伸應用
                """

                # 呼叫 Gemini 分析檔案
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[uploaded_doc, prompt],
                )

                st.success("✅ 分析完成！")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"分析失敗：{e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
