import streamlit as st
from openai import OpenAI
import json

# --- 1. 核心逻辑函数 ---

def get_ai_response(api_key, system_prompt, user_input):
    """
    通用函数：调用 API 获取结果
    """
    # 初始化客户端 (注意：这里我们用动态传入的 Key)
    client = OpenAI(
        api_key=api_key,
        base_url="https://llmapi.paratera.com" # ⚠️ 记得确认这个地址！
    )

    response = client.chat.completions.create(
        model="Qwen3-235B-A22B-Instruct-2507", # ⚠️ 记得确认模型名字！
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- 2. 页面布局 ---

st.set_page_config(page_title="AI 简历助手", layout="wide")

st.title("🚀 AI 简历优化助手")
st.markdown("---") # 画一条分割线

# 侧边栏：配置区
with st.sidebar:
    st.header("⚙️ 设置")
    user_api_key = st.text_input("请输入 API Key", type="password", help="这里填你的 sk-xxxx")
    st.info("提示：你的 Key 仅在本次运行有效，不会被保存。")

# 主区域：左右分栏
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 原始简历")
    raw_resume = st.text_area("请粘贴简历内容", height=400, placeholder=" 我叫张三，电话是13800000000。我之前在字节跳动干了3年后端开发，主要用Python和Go。后来去了腾讯做了一年产品经理。我现在想找一份AI开发的工作。")

    start_btn = st.button("开始魔法优化 ✨", type="primary", use_container_width=True)

with col2:
    st.subheader("🧠 AI 分析结果")

    # 定义一个空容器，用来占位显示结果
    result_container = st.container()

# --- 3. 业务交互逻辑 ---

if start_btn:
    if not user_api_key:
        st.toast("❌ 请先填写 API Key") # 弹出一个小提示
    elif not raw_resume:
        st.toast("❌ 请填写简历内容")
    else:
        # 显示加载转圈圈
        with st.spinner("AI 正在大脑风暴中..."):
            try:
                # 任务 A: 提取信息 (JSON)
                json_prompt = """
                提取简历关键信息，严格输出 JSON 格式。包含字段：name, education, skills, years。
                """
                json_res = get_ai_response(user_api_key, json_prompt, raw_resume)

                # 任务 B: 毒舌点评
                review_prompt = """
                你是个毒舌 HR。指出 3 个缺点并给出建议。使用 Markdown 格式。
                """
                review_res = get_ai_response(user_api_key, review_prompt, raw_resume)

                # --- 展示结果 ---
                with result_container:
                    # 展示 1: JSON 变成漂亮的指标卡
                    try:
                        info = json.loads(json_res) # 解析 JSON
                        st.success("✅ 解析成功！")

                        # 漂亮的指标显示
                        m1, m2, m3 = st.columns(3)
                        m1.metric("姓名", info.get("name", "未知"))
                        m2.metric("工作年限", info.get("years", "未知"))
                        m3.metric("学历", info.get("education", "未知"))

                        st.write("**技能栈：**")
                        st.json(info.get("skills", [])) # 直接展示 JSON 数据

                    except:
                        st.warning("⚠️ JSON 解析失败，模型可能没听话，直接显示原文：")
                        st.code(json_res)

                    st.markdown("---")

                    # 展示 2: 点评内容
                    st.write("### 🌶️ 毒舌点评")
                    st.markdown(review_res)

            except Exception as e:
                st.error(f"发生错误：{str(e)}")
