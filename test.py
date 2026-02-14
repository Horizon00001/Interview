# 导入Streamlit库，用于构建Web界面
import streamlit as st
# 导入OpenAI库，用于调用AI API
from openai import OpenAI
# 导入datetime模块，用于处理时间
from datetime import datetime
# 导入json模块，用于处理JSON数据
import json
# 导入os模块，用于处理文件路径
import os
# 导入uuid模块，用于生成唯一标识符
import uuid

# 定义配置文件路径
CONFIG_FILE = "config.json"
# 定义历史记录目录
HISTORY_DIR = "history"

# 如果历史记录目录不存在，则创建
if not os.path.exists(HISTORY_DIR):
    os.makedirs(HISTORY_DIR)

# 定义加载配置的函数
def load_config():
    # 如果配置文件存在，则读取并返回
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 如果不存在，返回默认配置
    return {"api_key": "", "base_url": "https://api.deepseek.com", "model": "deepseek-chat"}

# 定义保存配置的函数
def save_config(config):
    # 将配置写入JSON文件
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# 定义获取历史记录文件列表的函数
def get_history_files():
    # 如果历史记录目录不存在，返回空列表
    if not os.path.exists(HISTORY_DIR):
        return []
    # 获取目录下所有JSON文件
    files = [f for f in os.listdir(HISTORY_DIR) if f.endswith(".json")]
    # 按修改时间倒序排列
    files.sort(key=lambda x: os.path.getmtime(os.path.join(HISTORY_DIR, x)), reverse=True)
    return files

# 定义加载历史记录的函数
def load_history(file_name):
    file_path = os.path.join(HISTORY_DIR, file_name)
    # 如果文件存在，读取并返回
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# 定义保存历史记录的函数
def save_history(history_data, file_name=None):
    # 如果未指定文件名，生成基于时间的文件名
    if file_name is None:
        file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.json"
    file_path = os.path.join(HISTORY_DIR, file_name)
    # 写入JSON数据
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
    return file_name

# 定义删除历史记录的函数
def delete_history(file_name):
    file_path = os.path.join(HISTORY_DIR, file_name)
    # 如果文件存在，删除
    if os.path.exists(file_path):
        os.remove(file_path)

# 面试系统的系统提示词，定义AI面试官的角色和行为
INTERVIEW_SYSTEM_PROMPT = """
Role: Java面试助手
Profile
language: 中文
description: 专业的Java技术面试官，专注于通过互动问答评估用户的Java知识深度和广度，并提供建设性反馈。
background: 拥有超过10年的Java开发和企业级架构经验，曾主导多个大型分布式系统的设计与评审，并长期担任技术面试官。
personality: 严谨、客观、鼓励式教学。提问清晰，反馈具体，旨在帮助用户发现知识盲区并提升。
expertise: Java核心语法、JVM原理、并发编程、集合框架、Spring生态、设计模式、数据库与ORM、分布式系统基础。
target_audience: 准备Java技术面试的求职者（初级至高级）、希望系统性巩固Java知识的开发者。

Skills
面试评估技能

知识点拆解: 能将复杂的Java知识点拆解为清晰、可评估的具体问题。
回答精准评分: 根据回答的准确性、完整性、深度和实践理解进行量化评分（0-100分）。
差距分析: 精准识别用户回答中的错误、遗漏、概念模糊或理解片面之处。
引导式追问: 在用户回答不完整时，能提出引导性问题，帮助用户展现真实水平。

教学与反馈技能

结构化反馈: 提供"得分 + 优点 + 不足 + 改进建议"的完整反馈结构。
知识补充: 针对不足，能提供关键概念的精炼解释或标准答案要点。
关联知识提示: 指出当前知识点与相关知识的联系，帮助用户构建知识网络。
鼓励与激励: 在指出不足的同时，肯定用户的正确部分，保持积极的学习氛围。

Rules
基本原则：

客观公正: 评分和反馈严格基于技术事实，不掺杂主观偏好。
循序渐进: 从核心基础概念开始提问，根据用户水平动态调整问题的深度和广度。
一次一问: 每次交互只提出一个明确的、边界清晰的知识点问题。
用户为先: 等待用户完整回答后再进行评估和反馈，不中途打断。

行为准则：

清晰提问: 问题表述需精确，避免歧义。
评分透明: 明确告知评分标准。
反馈具体: 不足的指出必须对应到回答的具体部分，并提供改进方向。
保持专业: 使用规范的科技术语，反馈语气专业且友好。

限制条件：

不提供完整答案: 首次反馈侧重于指出不足和给出提示，仅在用户明确请求或多次尝试后，才提供完整标准答案。
不涉及超纲: 问题范围严格限定在公认的Java技术体系内。
不进行人身评价: 反馈仅针对回答内容。
不替代系统学习: 明确告知本助手用于查漏补缺和模拟面试。

Workflows
目标: 通过模拟面试，精准评估用户的Java知识掌握程度，并针对性地提升其薄弱环节。

步骤 1: 发起提问。选择一个合适的Java知识点，向用户提出一个结构清晰、有明确考察点的问题。
步骤 2: 接收与评估。等待用户回答。分析回答内容，从准确性、完整性、深度等维度进行评分（0-100分）。
步骤 3: 结构化反馈。首先给出分数，然后总结回答中的亮点（如有），接着详细、具体地指出所有不足之处，最后可提供简明的知识要点提示或改进建议。

预期结果: 用户能清晰了解自己对该知识点的掌握水平，明确知道具体哪里存在不足，并获得下一步学习的明确指引。
"""

# 用于生成面试总结的系统提示词
SUMMARY_PROMPT = """
请对以下Java模拟面试对话进行总结分析，包括：
1. 整体表现评估（平均分、优势领域、薄弱环节）
2. 知识点覆盖情况
3. 具体改进建议
4. 后续学习路径建议

请用结构化的方式呈现总结报告。
"""

# 初始化会话状态的函数
def init_session_state():
    # 如果messages不存在，初始化为空列表
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # 如果current_file不存在，初始化为None
    if "current_file" not in st.session_state:
        st.session_state.current_file = None
    # 如果config不存在，加载配置文件
    if "config" not in st.session_state:
        st.session_state.config = load_config()
    # 如果api_key_set不存在，根据是否有api_key设置
    if "api_key_set" not in st.session_state:
        st.session_state.api_key_set = bool(st.session_state.config.get("api_key", ""))
    # 如果summary_content不存在，初始化为None
    if "summary_content" not in st.session_state:
        st.session_state.summary_content = None

# 获取OpenAI客户端的函数
def get_openai_client():
    config = st.session_state.config
    # 返回配置好的OpenAI客户端
    return OpenAI(
        api_key=config.get("api_key", ""),
        base_url=config.get("base_url", "https://api.deepseek.com"),
    )

# 调用AI API的函数
def call_ai(messages, is_summary=False):
    try:
        # 获取OpenAI客户端
        client = get_openai_client()
        # 获取模型名称
        model = st.session_state.config.get("model", "deepseek-chat")
        # 根据是否为总结选择不同的系统提示词
        if is_summary:
            system_content = SUMMARY_PROMPT
        else:
            system_content = INTERVIEW_SYSTEM_PROMPT
        
        # 组合完整消息列表
        full_messages = [{"role": "system", "content": system_content}] + messages
        
        # 返回流式响应对象
        return client.chat.completions.create(
            model=model,
            messages=full_messages,
            stream=True,
        )
    except Exception as e:
        # 发生异常返回None
        return None

# 渲染侧边栏的函数
def render_sidebar():
    with st.sidebar:
        # 标题
        st.header("⚙️ 设置")
        
        # API Key输入框
        api_key = st.text_input("API Key", value=st.session_state.config.get("api_key", ""), type="password", key="api_key_input")
        # 如果输入了API Key，更新配置
        if api_key:
            st.session_state.config["api_key"] = api_key
            st.session_state.api_key_set = True
        
        # Base URL输入框
        base_url = st.text_input("API Base URL", value=st.session_state.config.get("base_url", "https://api.deepseek.com"))
        st.session_state.config["base_url"] = base_url
        
        # 模型选择下拉框
        model = st.selectbox("模型", ["deepseek-chat", "gpt-3.5-turbo", "gpt-4"], 
                            index=["deepseek-chat", "gpt-3.5-turbo", "gpt-4"].index(st.session_state.config.get("model", "deepseek-chat")))
        st.session_state.config["model"] = model
        
        # 保存配置按钮
        if st.button("💾 保存配置"):
            save_config(st.session_state.config)
            st.success("配置已保存！")
        
        # 分隔线
        st.divider()
        
        # 分析报告标题
        st.header("分析报告")
        
        # 一键AI总结按钮
        if st.button("📈 一键AI总结"):
            st.session_state.show_summary = True
        
        # 如果触发了总结生成
        if st.session_state.get("show_summary", False):
            with st.spinner("正在生成分析报告..."):
                # 调用AI生成总结
                summary_response = call_ai(st.session_state.messages, is_summary=True)
                if summary_response:
                    full_summary = ""
                    # 遍历流式响应
                    for chunk in summary_response:
                        if chunk.choices[0].delta.content:
                            full_summary += chunk.choices[0].delta.content
                    # 保存到会话状态
                    st.session_state.summary_content = full_summary
                else:
                    st.session_state.summary_content = "调用API时出错，请检查API Key是否正确"
            st.session_state.show_summary = False
            st.rerun()
        
        # 如果有总结内容，显示出来
        if st.session_state.get("summary_content"):
            st.markdown(st.session_state.get("summary_content", ""))
        
        st.divider()
        
        # 历史记录标题
        st.header("历史记录")
        
        # 新建会话按钮
        if st.button("➕ 新建会话"):
            st.session_state.messages = []
            st.session_state.current_file = None
            st.session_state.summary_content = None
            st.rerun()
        
        # 获取历史文件列表
        history_files = get_history_files()
        
        # 遍历显示历史记录
        for file_name in history_files:
            history_data = load_history(file_name)
            if history_data:
                title = history_data.get("title", file_name.replace(".json", ""))
                col1, col2 = st.columns([3, 1])
                with col1:
                    # 加载历史会话按钮
                    if st.button(f"📝 {title[:20]}...", key=f"load_{file_name}"):
                        st.session_state.messages = history_data.get("messages", [])
                        st.session_state.current_file = file_name
                        st.session_state.summary_content = None
                        st.rerun()
                with col2:
                    # 删除历史会话按钮
                    if st.button("🗑️", key=f"del_{file_name}"):
                        delete_history(file_name)
                        if st.session_state.current_file == file_name:
                            st.session_state.messages = []
                            st.session_state.current_file = None
                            st.session_state.summary_content = None
                        st.rerun()

# 渲染主界面的函数
def render_main():
    # 设置页面标题
    st.title("🎯 Java面试助手")
    
    # 如果没有设置API Key，显示警告
    if not st.session_state.api_key_set or not st.session_state.config.get("api_key"):
        st.warning("⚠️ 请在侧边栏设置API Key后开始面试")
        return
    
    # 面试对话标题
    st.markdown("### 💬 面试对话")
    
    # 显示对话历史
    if st.session_state.messages:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # 如果没有消息，自动开始面试
    if not st.session_state.messages:
        welcome_msg = "好的，让我们开始面试。首先，请介绍一下你的Java学习背景和工作经验，以便我更好地评估你的水平并调整问题难度。"
        st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
        with st.chat_message("assistant"):
            st.markdown(welcome_msg)
        st.session_state.current_file = save_history({
            "title": f"面试_{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "messages": st.session_state.messages,
            "created_at": datetime.now().isoformat()
        })
    
    # 聊天输入框
    if prompt := st.chat_input("请输入你的回答..."):
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        # 添加到消息列表
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 显示助手响应（流式输出）
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            # 调用AI获取响应
            response = call_ai(st.session_state.messages)
            if response:
                # 流式显示响应
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)
            else:
                full_response = "调用API时出错，请检查API Key是否正确"
                st.error(full_response)
        # 保存助手响应
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # 如果已有文件，更新保存
        if st.session_state.current_file:
            save_history({
                "title": f"面试_{datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "messages": st.session_state.messages,
                "created_at": datetime.now().isoformat()
            }, st.session_state.current_file)
        else:
            # 新建文件保存
            st.session_state.current_file = save_history({
                "title": f"面试_{datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "messages": st.session_state.messages,
                "created_at": datetime.now().isoformat()
            })

# 主函数
def main():
    # 设置页面配置
    st.set_page_config(page_title="Java面试助手", page_icon="🎯", layout="wide")
    # 初始化会话状态
    init_session_state()
    # 渲染侧边栏
    render_sidebar()
    # 渲染主界面
    render_main()

# 程序入口
if __name__ == "__main__":
    main()
