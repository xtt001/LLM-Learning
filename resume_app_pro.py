import streamlit as st
from openai import OpenAI
import json
import pdfplumber  # 引入新库：处理PDF

# --- 1. 获取 API Key (安全版) ---
# 优先从 Streamlit Secrets 读取，如果没配，允许用户手动输入（作为备选）
try:
    api_key = st.secrets["OPENAI_API_KEY"]
    is_hardcoded = True # 标记：是内置Key
except:
    api_key = None
    is_hardcoded = False

# --- 2. 核心逻辑函数 ---
def get_ai_response(api_key, system_prompt, user_input):
    client = OpenAI(
        api_key=api_key,
        base_url="https://llmapi.paratera.com" # ⚠️ 确认你的 Host
    )
    response = client.chat.completions.create(
        model="Qwen3-235B-A22B-Instruct-2507", # ⚠️ 确认你的模型
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- 3. 辅助函数：提取 PDF 文本 ---
def extract_text_from_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# --- 4. 页面布局 ---
st.set_page_config(page_title="AI 简历助手", layout="wide")
st.title("🚀 AI 简历优化助手 Pro")

# 侧边栏
with st.sidebar:
    st.header("⚙️ 设置")
    # 如果没有配置 secrets，才显示输入框
    if not api_key:
        api_key = st.text_input("请输入 API Key", type="password")
    else:
        st.success("✅ 已内置 API Key (朋友专享版)")

# 主区域
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 上传简历")
    
    # === 修改点：增加文件上传组件 ===
    uploaded_file = st.file_uploader("上传 PDF 简历", type=["pdf"])
    
    # 定义一个变量存文本，初始化为空
    resume_text = ""

    # 如果用户传了文件，就解析文件
    if uploaded_file is not None:
        try:
            with st.spinner("正在读取 PDF..."):
                resume_text = extract_text_from_pdf(uploaded_file)
            st.success(f"PDF 读取成功！共 {len(resume_text)} 字")
            # 可以选择把读取到的文字展示出来让用户确认
            with st.expander("点击查看读取到的文本内容"):
                st.text(resume_text)
        except Exception as e:
            st.error(f"PDF 解析失败: {e}")
    
    # 如果没传文件，也允许直接粘贴 (双保险)
    else:
        resume_text = st.text_area("或者直接粘贴文本", height=300, placeholder="如果没有PDF，可以在这里直接粘贴...")

    start_btn = st.button("开始魔法优化 ✨", type="primary", use_container_width=True)

with col2:
    st.subheader("🧠 AI 分析结果")
    result_container = st.container()

# --- 5. 业务逻辑 ---
if start_btn:
    if not api_key:
        st.toast("❌ 缺 Key！")
    elif not resume_text or len(resume_text) < 10:
        st.toast("❌ 简历内容太少了，请上传文件或粘贴文本")
    else:
        with st.spinner("AI 正在大脑风暴中..."):
            try:
                # 这里复用之前的逻辑...
                json_prompt = "提取简历关键信息，严格输出 JSON 格式。包含字段：name, education, skills, years。"
                json_res = get_ai_response(api_key, json_prompt, resume_text)
                
                review_prompt = "你是个尖酸刻薄且毒舌的 HR。指出 3 个缺点并给出建议。使用 Markdown 格式。"
                review_res = get_ai_response(api_key, review_prompt, resume_text)
                
                with result_container:
                    try:
                        info = json.loads(json_res)
                        m1, m2, m3 = st.columns(3)
                        m1.metric("姓名", info.get("name", "未知"))
                        m2.metric("年限", info.get("years", "未知"))
                        m3.metric("学历", info.get("education", "未知"))
                        st.json(info.get("skills", []))
                    except:
                        st.warning("JSON 解析失败")
                    
                    st.markdown("---")
                    st.markdown(review_res)
                    
            except Exception as e:
                st.error(f"发生错误：{str(e)}")
