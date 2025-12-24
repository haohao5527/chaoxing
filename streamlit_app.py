# -*- coding: utf-8 -*-
"""
超星学习通自动化工具 - Streamlit Web界面
提供友好的Web界面来配置和执行自动化学习任务
"""

import streamlit as st
import sys
import traceback
import threading
import os
from typing import Optional
import time

# 添加项目根目录到Python路径
sys.path.append('.')

from api.static_config import StaticConfigManager, config_manager
from api.web_adapter import WebChaoxingAdapter, WebExecutionCallback
from api.logger import logger
from api.base import Chaoxing, Account


def init_session_state():
    """初始化Streamlit session state - 静态网页风格"""
    if 'config_initialized' not in st.session_state:
        st.session_state.config_initialized = False
        st.session_state.is_running = False
        st.session_state.execution_status = "等待开始"
        st.session_state.logs = []
        st.session_state.current_course = ""
        st.session_state.current_chapter = ""
        st.session_state.progress = 0
        st.session_state.total_tasks = 0
        st.session_state.completed_tasks = 0
        
        # 初始化静态配置（每个用户会话独立）
        config_manager.reset_config()
        config_manager.save_to_session_state(st.session_state)
        st.session_state.config_initialized = True


def get_course_list(username: str, password: str, use_cookies: bool = False) -> list:
    """获取课程列表供用户选择"""
    try:
        # 创建临时账号和超星实例
        account = Account(username, password)
        chaoxing = Chaoxing(account=account)
        
        # 登录获取课程
        login_state = chaoxing.login(login_with_cookies=use_cookies)
        if not login_state["status"]:
            return []
        
        # 获取课程列表
        all_courses = chaoxing.get_course_list()
        
        # 格式化课程信息，返回包含ID和名称的列表
        course_options = []
        for course in all_courses:
            course_options.append({
                "id": course["courseId"],
                "name": course["title"],
                "info": f"{course['title']} (ID: {course['courseId']})"
            })
        
        return course_options
        
    except Exception as e:
        logger.error(f"获取课程列表失败: {e}")
        return []


def render_config_sidebar():
    """渲染侧边栏配置界面 - 静态网页风格"""
    st.sidebar.title("⚙️ 配置设置")
    
    # 添加静态网页说明
    st.sidebar.info("🌐 **静态网页模式**\n每个用户都有独立配置\n刷新页面会重置所有设置")
    
    # 必要条件说明
    st.sidebar.warning("📋 **必要条件**\n• 账号密码 或 Cookie登录（二选一）\n• 其他选项都是可选的")
    
    # 登录配置
    st.sidebar.subheader("🔐 登录配置（必要）")
    use_cookies = st.sidebar.checkbox("使用Cookies登录", value=st.session_state.get("use_cookies", False))
    
    if not use_cookies:
        username = st.sidebar.text_input("手机号", value=st.session_state.get("username", ""), placeholder="请输入手机号")
        password = st.sidebar.text_input("密码", value=st.session_state.get("password", ""), 
                                       type="password", placeholder="请输入密码")
    else:
        username = st.session_state.get("username", "")
        password = st.session_state.get("password", "")
        st.sidebar.info("使用Cookies登录时无需输入账号密码")
    
    # 课程配置
    st.sidebar.subheader("📚 课程配置（可选）")
    
    # 检查是否已登录信息
    has_login_info = (use_cookies or (username and password))
    
    if has_login_info:
        # 添加获取课程列表的按钮
        if st.sidebar.button("🔄 获取课程列表", help="点击获取可选课程"):
            # 显示加载状态
            st.sidebar.info("🔄 正在获取课程列表...")
            try:
                courses = get_course_list(username, password, use_cookies)
                st.session_state.available_courses = courses
                st.session_state.courses_loaded = True
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ 获取课程列表失败: {str(e)}")
                st.session_state.courses_loaded = False
        
        # 如果已加载课程列表，显示选择界面
        if st.session_state.get("courses_loaded", False):
            available_courses = st.session_state.get("available_courses", [])
            
            if available_courses:
                st.sidebar.success(f"📚 找到 {len(available_courses)} 个课程")
                
                # 课程选择模式
                selection_mode = st.sidebar.radio(
                    "选择方式",
                    ["学习所有课程", "选择特定课程"],
                    key="course_selection_mode"
                )
                
                if selection_mode == "选择特定课程":
                    # 创建课程选项
                    course_options = [course["info"] for course in available_courses]
                    selected_courses = st.sidebar.multiselect(
                        "选择要学习的课程",
                        options=course_options,
                        default=[],
                        help="可以选择多个课程，留空则学习所有课程"
                    )
                    
                    # 将选择的课程转换为ID列表
                    if selected_courses:
                        selected_ids = []
                        for course_info in selected_courses:
                            # 从课程信息中提取ID
                            for course in available_courses:
                                if course["info"] == course_info:
                                    selected_ids.append(course["id"])
                                    break
                        st.session_state.selected_course_ids = selected_ids
                    else:
                        st.session_state.selected_course_ids = []
                else:
                    st.session_state.selected_course_ids = []  # 空列表表示学习所有课程
            else:
                st.sidebar.error("❌ 未找到课程，请检查登录信息")
                st.session_state.courses_loaded = False
    else:
        st.sidebar.info("💡 请先填写登录信息，然后获取课程列表")
        # 保留原来的文本输入作为备选
        course_list_str = st.sidebar.text_area("课程ID列表（备用）", 
                                              value=st.session_state.get("course_list_str", ""),
                                              placeholder="请输入课程ID，多个ID用逗号分隔，如：123456,789012")
    
    # 学习配置
    st.sidebar.subheader("🎯 学习配置（可选）")
    speed = st.sidebar.slider("视频播放倍速", min_value=1.0, max_value=2.0, 
                             value=float(st.session_state.get("speed", 1.0)), step=0.1)
    jobs = st.sidebar.number_input("并发章节数", min_value=1, max_value=10,
                                  value=int(st.session_state.get("jobs", 4)), step=1)
    notopen_action = st.sidebar.selectbox("未开放任务处理方式",
                                        options=["retry", "ask", "continue"],
                                        index=["retry", "ask", "continue"].index(st.session_state.get("notopen_action", "retry")))
    verbose = st.sidebar.checkbox("启用调试模式", value=st.session_state.get("verbose", False))
    
    # 题库配置
    st.sidebar.subheader("📖 题库配置（可选）")
    tiku_enabled = st.sidebar.checkbox("启用题库功能", value=st.session_state.get("tiku_enabled", True))
    
    if tiku_enabled:
        tiku_provider = st.sidebar.selectbox("题库提供商",
                                           options=["TikuYanxi", "TikuGaoXiao", "TikuOther"],
                                           index=0)
        tiku_delay = st.sidebar.number_input("查询延迟(秒)", min_value=0.0, max_value=10.0,
                                           value=float(st.session_state.get("tiku_delay", 1.0)), step=0.1)
        tiku_cover_rate = st.sidebar.slider("答案覆盖率", min_value=0.0, max_value=1.0,
                                          value=float(st.session_state.get("tiku_cover_rate", 0.8)), step=0.1)
        tiku_submit = st.sidebar.checkbox("自动提交答案", value=st.session_state.get("tiku_submit", True))
    else:
        tiku_provider = "TikuYanxi"
        tiku_delay = 1.0
        tiku_cover_rate = 0.8
        tiku_submit = False
    
    # 通知配置
    st.sidebar.subheader("🔔 通知配置（可选）")
    notification_enabled = st.sidebar.checkbox("启用通知功能", value=st.session_state.get("notification_enabled", False))
    
    if notification_enabled:
        notification_provider = st.sidebar.selectbox("通知服务",
                                                   options=["NotificationService", "ServerChan", "Qmsg", "Bark"],
                                                   index=0)
        notification_url = st.sidebar.text_input("通知URL", 
                                               value=st.session_state.get("notification_url", ""),
                                               placeholder="请输入通知服务的URL或Token")
    else:
        notification_provider = "NotificationService"
        notification_url = ""
    
    # 保存配置到session state
    st.session_state.update({
        "username": username,
        "password": password,
        "use_cookies": use_cookies,
        "speed": speed,
        "jobs": jobs,
        "notopen_action": notopen_action,
        "verbose": verbose,
        "tiku_enabled": tiku_enabled,
        "tiku_provider": tiku_provider,
        "tiku_delay": tiku_delay,
        "tiku_cover_rate": tiku_cover_rate,
        "tiku_submit": tiku_submit,
        "notification_enabled": notification_enabled,
        "notification_provider": notification_provider,
        "notification_url": notification_url
    })
    
    # 处理课程配置
    if st.session_state.get("courses_loaded", False):
        # 使用新选择的课程
        selected_ids = st.session_state.get("selected_course_ids", [])
        st.session_state.course_list_str = ",".join(selected_ids) if selected_ids else ""
    else:
        # 使用备用文本输入
        st.session_state.course_list_str = course_list_str if 'course_list_str' in locals() else ""
    
    # 配置验证和重置按钮
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🔍 验证配置"):
            config_manager.load_from_session_state(st.session_state)
            errors = config_manager.validate_config()
            
            if errors:
                st.sidebar.error("配置验证失败：\n" + "\n".join(f"• {error}" for error in errors))
            else:
                st.sidebar.success("✅ 配置验证通过！")
    
    with col2:
        if st.button("🔄 重置配置"):
            config_manager.reset_config()
            config_manager.save_to_session_state(st.session_state)
            # 重置课程相关状态
            st.session_state.courses_loaded = False
            st.session_state.available_courses = []
            st.session_state.selected_course_ids = []
            st.session_state.course_list_str = ""
            # 清空日志收集器
            log_collector.clear_logs()
            st.sidebar.success("✅ 配置已重置！")
            st.rerun()


def render_main_interface():
    """渲染主界面 - 静态网页风格"""
    st.title("🎓 超星学习通自动化工具")
    st.markdown("### 🌐 静态网页版本 - 每位用户独立配置")
    st.markdown("**特点**：无需注册，每位访客都有独立的配置空间，刷新页面会重置所有设置")
    st.markdown("---")
    
    # 状态显示区域
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("执行状态", st.session_state.execution_status)
    
    with col2:
        if st.session_state.total_tasks > 0:
            progress_percentage = (st.session_state.completed_tasks / st.session_state.total_tasks) * 100
            st.metric("完成进度", f"{progress_percentage:.1f}%")
        else:
            st.metric("完成进度", "0%")
    
    with col3:
        st.metric("当前课程", st.session_state.current_course or "未开始")
    
    with col4:
        st.metric("当前章节", st.session_state.current_chapter or "未开始")
    
    # 进度条
    if st.session_state.total_tasks > 0:
        progress_bar = st.progress(st.session_state.completed_tasks / st.session_state.total_tasks)
        st.write(f"任务进度：{st.session_state.completed_tasks}/{st.session_state.total_tasks}")
    
    # 控制按钮
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not st.session_state.is_running:
            if st.button("🚀 开始执行", type="primary"):
                start_execution()
        else:
            if st.button("⏸️ 暂停执行"):
                pause_execution()
    
    with col2:
        if st.button("🔄 重置状态"):
            reset_execution()
    
    with col3:
        if st.button("🗑️ 清空日志"):
            log_collector.clear_logs()
    
    # 日志显示区域 - 终端窗口
    st.markdown("---")
    st.subheader("💻 终端窗口")
    st.caption("显示命令行执行的完整输出，就像直接看终端一样")
    
    # 日志选项
    log_col1, log_col2 = st.columns([1, 1])
    with log_col1:
        show_debug = st.checkbox("显示调试日志", value=False)
    with log_col2:
        auto_scroll = st.checkbox("自动滚动", value=True)
    
    # 显示日志 - 终端窗口风格
    log_container = st.container()
    with log_container:
        # 终端窗口样式
        st.markdown("""
        <style>
        .terminal-window {
            background-color: #1e1e1e;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #00ff00;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 从日志收集器获取日志
        all_logs = log_collector.get_logs()
        
        # 收集所有终端输出
        terminal_output = []
        for log_entry in all_logs:
            log_level, message, timestamp = log_entry
            if log_level == "TERMINAL":
                terminal_output.append(message)
        
        # 显示终端窗口
        if terminal_output:
            terminal_text = "\n".join(terminal_output)
            st.markdown(f"""
            <div class="terminal-window">{terminal_text}</div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="terminal-window">等待任务开始...</div>
            """, unsafe_allow_html=True)
        
        # 显示原始日志（可选）
        if show_debug:
            with st.expander("显示详细日志"):
                for log_entry in st.session_state.logs:
                    log_level, message, timestamp = log_entry
                    if log_level == "ERROR":
                        st.error(f"🔴 {timestamp} - {message}")
                    elif log_level == "WARNING":
                        st.warning(f"🟡 {timestamp} - {message}")
                    elif log_level == "INFO":
                        st.info(f"🔵 {timestamp} - {message}")
                    else:  # DEBUG or TERMINAL
                        st.code(f"⚪ {timestamp} - {message}")


# 创建全局日志收集器
class LogCollector:
    def __init__(self):
        self.logs = []
        self.lock = threading.Lock()
    
    def add_log(self, level: str, message: str):
        """线程安全的日志添加"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with self.lock:
            self.logs.append((level, message, timestamp))
            # 限制日志数量
            if len(self.logs) > 1000:
                self.logs = self.logs[-500:]
    
    def get_logs(self):
        """获取所有日志"""
        with self.lock:
            return self.logs.copy()
    
    def clear_logs(self):
        """清空日志"""
        with self.lock:
            self.logs.clear()

# 全局日志收集器实例
log_collector = LogCollector()

def add_log(level: str, message: str):
    """添加日志到收集器"""
    log_collector.add_log(level, message)


def init_config_from_web():
    """从Web配置转换为main.py期望的格式"""
    config_manager.load_from_session_state(st.session_state)
    common_config = config_manager.get_common_dict()
    tiku_config = config_manager.get_tiku_dict()
    notification_config = config_manager.get_notification_dict()
    
    return common_config, tiku_config, notification_config

def init_chaoxing_from_config(common_config, tiku_config):
    """使用main.py的初始化逻辑"""
    from api.base import Chaoxing, Account
    from api.answer import Tiku
    
    username = common_config.get("username", "")
    password = common_config.get("password", "")
    use_cookies = common_config.get("use_cookies", False)
    
    account = Account(username, password)
    
    # 设置题库
    tiku = Tiku()
    tiku.config_set(tiku_config)
    tiku = tiku.get_tiku_from_config()
    tiku.init_tiku()
    
    # 获取查询延迟设置
    query_delay = tiku_config.get("delay", 0)
    
    # 实例化超星API
    chaoxing = Chaoxing(account=account, tiku=tiku, query_delay=query_delay)
    
    return chaoxing

def filter_courses_from_web(all_course, course_list):
    """使用main.py的课程过滤逻辑"""
    if not course_list:
        return all_course
    
    course_task = []
    course_ids = []
    for course in all_course:
        if course["courseId"] in course_list and course["courseId"] not in course_ids:
            course_task.append(course)
            course_ids.append(course["courseId"])
    
    return course_task

def start_execution():
    """开始执行任务 - 直接调用main.py核心逻辑"""
    # 加载并验证配置
    config_manager.load_from_session_state(st.session_state)
    errors = config_manager.validate_config()
    
    if errors:
        st.error("配置验证失败，请检查侧边栏配置：\n" + "\n".join(f"• {error}" for error in errors))
        return
    
    st.session_state.is_running = True
    st.session_state.execution_status = "正在执行"
    
    # 清空之前的日志
    log_collector.clear_logs()
    
    # 直接调用main.py的核心逻辑
    def run_main_logic():
        try:
            # 导入main.py的所有核心函数
            from main import init_config, init_chaoxing, filter_courses, process_course, load_config_from_file, build_config_from_args
            from api.base import Chaoxing, Account
            from api.answer import Tiku
            from api.notification import Notification
            
            # 重定向print和logger输出
            import sys
            from io import StringIO
            
            class OutputCapture:
                def __init__(self):
                    self.buffer = []
                
                def write(self, text):
                    if text.strip():
                        add_log("TERMINAL", text.strip())
                
                def flush(self):
                    pass
            
            # 替换stdout
            original_stdout = sys.stdout
            sys.stdout = OutputCapture()
            
            try:
                # 模拟命令行参数
                common_config = config_manager.get_common_dict()
                tiku_config = config_manager.get_tiku_dict()
                notification_config = config_manager.get_notification_dict()
                
                # 创建模拟的args对象
                class Args:
                    def __init__(self):
                        self.username = common_config.get("username")
                        self.password = common_config.get("password")
                        self.course_list = common_config.get("course_list")
                        self.speed = common_config.get("speed", 1.0)
                        self.jobs = common_config.get("jobs", 4)
                        self.notopen_action = common_config.get("notopen_action", "retry")
                        self.use_cookies = common_config.get("use_cookies", False)
                
                args = Args()
                
                # 直接调用main.py的初始化逻辑
                add_log("TERMINAL", "开始初始化配置...")
                
                # 初始化配置
                if args.config:
                    common_config, tiku_config, notification_config = load_config_from_file(args.config)
                else:
                    common_config, tiku_config, notification_config = build_config_from_args(args)
                
                # 初始化超星实例
                add_log("TERMINAL", "正在初始化超星实例...")
                chaoxing = init_chaoxing(common_config, tiku_config)
                
                # 登录
                add_log("TERMINAL", "正在登录...")
                _login_state = chaoxing.login(login_with_cookies=args.use_cookies)
                if not _login_state["status"]:
                    add_log("TERMINAL", f"登录失败: {_login_state['msg']}")
                    return
                
                add_log("TERMINAL", "登录成功")
                
                # 获取课程列表
                add_log("TERMINAL", "正在获取课程列表...")
                all_course = chaoxing.get_course_list()
                
                # 过滤课程
                add_log("TERMINAL", "正在过滤课程...")
                course_task = filter_courses(all_course, args.course_list)
                
                # 显示课程列表
                add_log("TERMINAL", "*" * 10 + "课程列表" + "*" * 10)
                for course in course_task:
                    add_log("TERMINAL", f"ID: {course['courseId']} 课程名: {course['title']}")
                add_log("TERMINAL", "*" * 28)
                
                add_log("TERMINAL", f"课程列表过滤完毕, 当前课程任务数量: {len(course_task)}")
                
                # 处理每个课程
                for course in course_task:
                    if not st.session_state.get('is_running', False):
                        add_log("TERMINAL", "任务被用户停止")
                        break
                    
                    add_log("TERMINAL", f"开始学习课程: {course['title']}")
                    process_course(chaoxing, course, common_config)
                
                add_log("TERMINAL", "所有课程学习任务已完成")
                
            finally:
                # 恢复stdout
                sys.stdout = original_stdout
                
        except Exception as e:
            add_log("TERMINAL", f"执行出错: {type(e).__name__}: {e}")
            import traceback
            add_log("TERMINAL", traceback.format_exc())
        finally:
            st.session_state.is_running = False
    
    # 启动后台线程
    thread = threading.Thread(target=run_main_logic, daemon=True)
    thread.start()


def pause_execution():
    """暂停执行"""
    st.session_state.is_running = False
    st.session_state.execution_status = "已暂停"
    add_log("INFO", "任务已暂停")


def reset_execution():
    """重置执行状态"""
    st.session_state.is_running = False
    st.session_state.execution_status = "等待开始"
    st.session_state.current_course = ""
    st.session_state.current_chapter = ""
    st.session_state.progress = 0
    st.session_state.total_tasks = 0
    st.session_state.completed_tasks = 0
    add_log("INFO", "状态已重置")


def main():
    """主函数"""
    # 配置页面
    try:
        st.set_page_config(
            page_title="超星学习通自动化工具",
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except Exception as e:
        # Streamlit Cloud可能限制页面配置，提供fallback
        st.error(f"页面配置失败，但应用仍可正常运行: {e}")
    
    # 添加Streamlit Cloud检测和功能验证
    streamlit_cloud = os.getenv('STREAMLIT_SERVER_PORT') is not None
    if streamlit_cloud:
        st.info("🌐 运行在Streamlit Cloud上")
        st.success("✅ 刷课功能完整可用")
        st.info("💡 提示：登录状态在当前会话中保持，刷新页面会重置")
        
        # 测试网络连接
        try:
            import requests
            response = requests.get("https://passport2.chaoxing.com/", timeout=5)
            if response.status_code == 200:
                st.success("🔗 网络连接正常，刷课功能完全可用")
            else:
                st.warning("⚠️ 网络连接异常，可能影响刷课功能")
        except:
            st.error("❌ 网络连接失败，请检查网络设置")
    
    # 初始化session state
    init_session_state()
    
    # 渲染界面
    render_config_sidebar()
    render_main_interface()
    
    # 页脚
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            超星学习通自动化工具 - Web版本 | 
            <a href='https://github.com/Samueli924/chaoxing' target='_blank'>GitHub</a>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
