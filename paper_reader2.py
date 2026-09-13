import os
import streamlit as st
from pypdf import PdfReader
from dotenv import load_dotenv
from google import genai

# 載入環境變數
load_dotenv()

# 頁面基本設定
st.set_page_config(
    page_title="Gemini 論文 AI 快速解讀器",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Gemini 論文 AI 快速解讀器")
st.caption("輕鬆拖曳上傳 PDF 論文，透過 Gemini 進行結構化重點摘要與深度提問")

# 側邊欄：API Key 與模型設定
with st.sidebar:
    st.header("⚙️ 系統設定")
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=env_key,
        type="password",
        help="金鑰優先從 .env 讀取，亦可在此手動輸入。"
    )
    
    model_choice = st.selectbox(
        "選擇 Gemini 模型",
        ["gemini-3.5-flash", "gemini-2.5-pro"],
        index=0
    )
    st.divider()
    st.markdown("""
    **💡 使用小提示：**
    1. 上傳 PDF 檔案（支援多頁論文）
    2. 點擊「生成論文結構化摘要」
    3. 也可在自訂問答區輸入特定問題
    """)

# 論文 PDF 上傳元件
uploaded_file = st.file_uploader("請拖曳或選擇上傳 PDF 檔案", type=["pdf"])

def extract_text_from_pdf(file_obj):
    """自 PDF 檔案逐頁萃取純文字內容"""
    reader = PdfReader(file_obj)
    full_text = []
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            full_text.append(f"--- 第 {page_num + 1} 頁 ---\n{page_text}")
    return "\n\n".join(full_text)

if uploaded_file is not None:
    st.success(f"已成功載入檔案：**{uploaded_file.name}**")
    
    # 抽取 PDF 文字
    with st.spinner("正在解析 PDF 內容..."):
        paper_text = extract_text_from_pdf(uploaded_file)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📄 論文預覽")
        st.info(f"總字數約：{len(paper_text)} 字元")
        st.text_area("擷取文字預覽（前 1,500 字）", paper_text[:1500] + ("..." if len(paper_text) > 1500 else ""), height=350)
    
    with col2:
        st.subheader("🤖 AI 解讀與問答")
        
        # 快捷結構化摘要按鈕
        if st.button("🚀 生成論文結構化摘要", use_container_width=True, type="primary"):
            if not api_key_input:
                st.error("請在左側輸入或在 .env 中設定 GEMINI_API_KEY！")
            else:
                with st.spinner("Gemini 正在閱讀全文並彙整摘要，請稍候..."):
                    try:
                        client = genai.Client(api_key=api_key_input)
                        summary_prompt = f"""你是一位資深的學術研究專家。請根據以下提供的論文內容，以繁體中文撰寫一份高水準、結構清晰的研究總結：

### 必須涵蓋的維度：
1. **研究背景與核心假說**：此研究解決什麼核心問題？主要假說是什麼？
2. **研究方法與對象**：研究對象（受試者條件、數量等）、實驗設計或使用的分析演算法/工具。
3. **主要研究發現**：關鍵數據、顯著性結果或新發現。
4. **研究貢獻與局限性**：對領域的貢獻與研究限制。

---
以下為論文完整內容：
{paper_text}
"""
                        response = client.models.generate_content(
                            model=model_choice,
                            contents=summary_prompt
                        )
                        st.session_state["summary_result"] = response.text
                    except Exception as e:
                        st.error(f"API 呼叫失敗：{e}")
        
        # 自訂問題輸入
        user_question = st.text_input("或輸入針對此論文的自訂問題：", placeholder="例如：論文中提到的 EEG 頻段有哪些特徵差異？")
        if st.button("發送問題", use_container_width=True):
            if not api_key_input:
                st.error("請在左側輸入或在 .env 中設定 GEMINI_API_KEY！")
            elif not user_question.strip():
                st.warning("請先輸入問題！")
            else:
                with st.spinner("AI 正在比對論文回答問題..."):
                    try:
                        client = genai.Client(api_key=api_key_input)
                        qa_prompt = f"""請僅根據以下論文內容，用繁體中文回答使用者的問題。如果論文中沒有提及相關資訊，請誠實說明。

論文內容：
{paper_text}
