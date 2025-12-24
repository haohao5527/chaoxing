# -*- coding: utf-8 -*-
"""
Web适配器模块
用于桥接Streamlit Web界面和核心API，提供Web友好的接口
"""

from typing import Dict, List, Any, Optional
import threading
import time
import random
from datetime import datetime

from api.static_config import StaticConfigManager, config_manager
from api.base import Chaoxing, Account, StudyResult
from api.answer import Tiku
from api.notification import Notification
from api.logger import logger
from api.exceptions import LoginError, InputFormatError


class WebExecutionCallback:
    """Web执行回调类，用于更新Streamlit界面状态"""
    
    def __init__(self, session_state):
        self.session_state = session_state
        self._stop_event = threading.Event()
    
    def should_stop(self) -> bool:
        """检查是否应该停止执行"""
        return self._stop_event.is_set() or not self.session_state.get('is_running', False)
    
    def stop(self):
        """停止执行"""
        self._stop_event.set()
    
    def update_status(self, status: str):
        """更新执行状态"""
        self.session_state['execution_status'] = status
    
    def update_progress(self, completed: int, total: int):
        """更新进度"""
        self.session_state['completed_tasks'] = completed
        self.session_state['total_tasks'] = total
    
    def update_current_course(self, course_name: str):
        """更新当前课程"""
        self.session_state['current_course'] = course_name
    
    def update_current_chapter(self, chapter_name: str):
        """更新当前章节"""
        self.session_state['current_chapter'] = chapter_name
    
    def add_log(self, level: str, message: str):
        """添加日志 - 直接复制命令行输出"""
        # 直接输出命令行格式，不加时间戳和级别标识
        self.session_state['logs'].append(("TERMINAL", message, ""))
        
        # 限制日志数量
        if len(self.session_state['logs']) > 1000:
            self.session_state['logs'] = self.session_state['logs'][-500:]


class WebChaoxingAdapter:
    """Web版超星适配器"""
    
    def __init__(self, callback: WebExecutionCallback):
        self.callback = callback
        self.chaoxing: Optional[Chaoxing] = None
        self.notification: Optional[Notification] = None
    
    def initialize(self, config_manager: StaticConfigManager) -> bool:
        """初始化适配器"""
        try:
            # 获取配置
            common_config = config_manager.get_common_dict()
            tiku_config = config_manager.get_tiku_dict()
            notification_config = config_manager.get_notification_dict()
            
            # 初始化账号
            username = common_config.get("username", "")
            password = common_config.get("password", "")
            use_cookies = common_config.get("use_cookies", False)
            
            account = Account(username, password)
            
            # 初始化题库
            tiku = Tiku()
            tiku.config_set(tiku_config)
            tiku = tiku.get_tiku_from_config()
            tiku.init_tiku()
            
            # 获取查询延迟设置
            query_delay = tiku_config.get("delay", 0)
            
            # 初始化超星API
            self.chaoxing = Chaoxing(account=account, tiku=tiku, query_delay=query_delay)
            
            # 初始化通知
            self.notification = Notification()
            self.notification.config_set(notification_config)
            self.notification = self.notification.get_notification_from_config()
            self.notification.init_notification()
            
            return True
            
        except Exception as e:
            self.callback.add_log("ERROR", f"初始化失败: {type(e).__name__}: {e}")
            return False
    
    def login(self) -> bool:
        """登录"""
        if not self.chaoxing:
            self.callback.add_log("ERROR", "适配器未初始化")
            return False
        
        try:
            common_config = config_manager.get_common_dict()
            use_cookies = common_config.get("use_cookies", False)
            
            self.callback.add_log("INFO", "正在登录...")
            login_state = self.chaoxing.login(login_with_cookies=use_cookies)
            
            if not login_state["status"]:
                raise LoginError(login_state["msg"])
            
            self.callback.add_log("INFO", "登录成功！")
            return True
            
        except Exception as e:
            self.callback.add_log("ERROR", f"登录失败: {type(e).__name__}: {e}")
            return False
    
    def get_courses(self) -> List[Dict[str, Any]]:
        """获取课程列表"""
        if not self.chaoxing:
            return []
        
        try:
            self.callback.add_log("TERMINAL", "正在获取课程列表...")
            all_course = self.chaoxing.get_course_list()
            
            # 打印课程列表（与命令行版本相同）
            self.callback.add_log("TERMINAL", "**********课程列表**********")
            for course in all_course:
                self.callback.add_log("TERMINAL", f"ID: {course['courseId']} 课程名: {course['title']}")
            self.callback.add_log("TERMINAL", "****************************")
            
            # 过滤课程
            common_config = config_manager.get_common_dict()
            course_list = common_config.get("course_list", [])
            
            if course_list and isinstance(course_list, str):
                course_list = [item.strip() for item in course_list.split(",") if item.strip()]
            
            course_task = []
            course_ids = []
            for course in all_course:
                if not course_list or course["courseId"] in course_list:
                    if course["courseId"] not in course_ids:
                        course_task.append(course)
                        course_ids.append(course["courseId"])
            
            self.callback.add_log("TERMINAL", f"课程列表过滤完毕, 当前课程任务数量: {len(course_task)}")
            return course_task
            
        except Exception as e:
            self.callback.add_log("ERROR", f"获取课程列表失败: {type(e).__name__}: {e}")
            return []
    
    def process_course(self, course: Dict[str, Any]) -> bool:
        """处理单个课程"""
        if not self.chaoxing:
            return False
        
        if self.callback.should_stop():
            return False
        
        try:
            self.callback.update_current_course(course['title'])
            self.callback.add_log("TERMINAL", f"开始学习课程: {course['title']}")
            
            # 获取章节列表
            point_list = self.chaoxing.get_course_point(
                course["courseId"], course["clazzId"], course["cpi"]
            )
            
            if not point_list or "points" not in point_list:
                self.callback.add_log("WARNING", f"课程 {course['title']} 没有找到章节")
                return True
            
            points = point_list["points"]
            
            # 处理每个章节（与main.py的process_chapter函数相同的逻辑）
            for i, point in enumerate(points):
                if self.callback.should_stop():
                    break
                
                self.callback.update_current_chapter(point.get("title", f"第{i+1}章"))
                self.callback.add_log("INFO", f'当前章节: {point["title"]}')
                
                # 检查章节是否已完成
                if point.get("has_finished", False):
                    self.callback.add_log("INFO", f'章节：{point["title"]} 已完成所有任务点')
                    continue
                
                # 随机等待，避免请求过快（与main.py相同）
                import random
                self.chaoxing.rate_limiter.limit_rate(random_time=True, random_min=0, random_max=0.2)
                
                # 获取当前章节的所有任务点
                jobs, job_info = self.chaoxing.get_job_list(course, point)
                
                # 发现未开放章节, 根据配置处理
                if job_info and job_info.get("notOpen", False):
                    self.callback.add_log("WARNING", f"章节未开放: {point['title']}")
                    # 根据配置决定是否继续
                    common_config = config_manager.get_common_dict()
                    if common_config.get("notopen_action") == "continue":
                        continue
                    else:
                        return False
                
                # 处理任务点
                if not jobs:
                    self.callback.add_log("INFO", f"章节没有任务点: {point.get('title')}")
                    continue
                
                # 处理每个任务点
                job_results = []
                for job in jobs:
                    if self.callback.should_stop():
                        break
                    
                    result = self._process_job(course, job, job_info)
                    job_results.append(result)
                    
                    if result.is_failure():
                        break
                
                # 检查任务结果
                for result in job_results:
                    if result.is_failure():
                        self.callback.add_log("ERROR", f"章节处理失败: {point['title']}")
                        return False
            
            self.callback.add_log("INFO", f"课程学习完成: {course['title']}")
            return True
            
        except Exception as e:
            self.callback.add_log("ERROR", f"处理课程失败: {type(e).__name__}: {e}")
            return False
    
    def _process_chapter(self, course: Dict[str, Any], point: Dict[str, Any]) -> str:
        """处理单个章节（内部方法）"""
        try:
            # 获取任务点列表
            jobs, job_info = self.chaoxing.get_job_list(course, point)
            
            # 检查是否未开放
            if job_info and job_info.get("notOpen", False):
                return "NOT_OPEN"
            
            if not jobs:
                self.callback.add_log("INFO", f"章节没有任务点: {point.get('title')}")
                return "SUCCESS"
            
            # 处理每个任务点
            for job in jobs:
                if self.callback.should_stop():
                    return "STOPPED"
                
                result = self._process_job(course, job, job_info)
                if result.is_failure():
                    return "ERROR"
            
            return "SUCCESS"
            
        except Exception as e:
            self.callback.add_log("ERROR", f"章节处理异常: {e}")
            return "ERROR"
    
    def _process_job(self, course: Dict[str, Any], job: Dict[str, Any], job_info: Dict[str, Any]) -> StudyResult:
        """处理单个任务点（内部方法）"""
        try:
            common_config = config_manager.get_common_dict()
            speed = common_config.get("speed", 1.0)
            
            # 视频任务（与main.py完全相同的日志输出）
            if job["type"] == "video":
                self.callback.add_log("TERMINAL", f"识别到视频任务, 任务章节: {course['title']} 任务ID: {job['jobid']}")
                # 超星的接口没有返回当前任务是否为Audio音频任务
                video_result = self.chaoxing.study_video(
                    course, job, job_info, _speed=speed, _type="Video"
                )
                if video_result.is_failure():
                    self.callback.add_log("WARNING", "当前任务非视频任务, 正在尝试音频任务解码")
                    video_result = self.chaoxing.study_video(
                        course, job, job_info, _speed=speed, _type="Audio")
                if video_result.is_failure():
                    self.callback.add_log("WARNING", f"出现异常任务 -> 任务章节: {course['title']} 任务ID: {job['jobid']}, 已跳过")
                return video_result
            
            # 文档任务
            elif job["type"] == "document":
                self.callback.add_log("TERMINAL", f"识别到文档任务, 任务章节: {course['title']} 任务ID: {job['jobid']}")
                return self.chaoxing.study_document(course, job)
            
            # 测验任务
            elif job["type"] == "workid":
                self.callback.add_log("TERMINAL", f"识别到章节检测任务, 任务章节: {course['title']}")
                return self.chaoxing.study_work(course, job, job_info)
            
            # 阅读任务
            elif job["type"] == "read":
                self.callback.add_log("TERMINAL", f"识别到阅读任务, 任务章节: {course['title']}")
                return self.chaoxing.study_read(course, job, job_info)
            
            # 直播任务
            elif job["type"] == "live":
                self.callback.add_log("TERMINAL", f"识别到直播任务, 任务章节: {course['title']} 任务ID: {job['jobid']}")
                try:
                    # 准备直播所需参数
                    defaults = {
                        "userid": self.chaoxing.get_uid(),
                        "clazzId": course.get("clazzId"),
                        "knowledgeid": job_info.get("knowledgeid")
                    }
                    
                    # 创建直播对象
                    from api.live import Live
                    live = Live(
                        attachment=job,
                        defaults=defaults,
                        course_id=course.get("courseId")
                    )
                    
                    # 启动直播处理线程
                    import threading
                    from api.live_process import LiveProcessor
                    thread = threading.Thread(
                        target=LiveProcessor.run_live,
                        args=(live, speed),
                        daemon=True
                    )
                    thread.start()
                    thread.join()  # 等待直播处理完成
                    return StudyResult.SUCCESS
                except Exception as e:
                    self.callback.add_log("ERROR", f"处理直播任务时出错: {str(e)}")
                    return StudyResult.ERROR
            
            else:
                self.callback.add_log("ERROR", f"未知任务类型: {job['type']}")
                return StudyResult.ERROR
                
        except Exception as e:
            self.callback.add_log("ERROR", f"任务处理异常: {e}")
            return StudyResult.ERROR
    
    def execute_all_courses(self) -> bool:
        """执行所有课程"""
        if not self.initialize(config_manager):
            return False
        
        if not self.login():
            return False
        
        courses = self.get_courses()
        if not courses:
            self.callback.add_log("WARNING", "没有找到需要学习的课程")
            return True
        
        total_courses = len(courses)
        total_tasks = 0  # 简化计算，假设每个课程平均10个任务点
        
        self.callback.update_progress(0, total_courses * 10)
        
        success_count = 0
        for i, course in enumerate(courses):
            if self.callback.should_stop():
                break
            
            if self.process_course(course):
                success_count += 1
            
            # 更新总体进度
            self.callback.update_progress((i + 1) * 10, total_courses * 10)
        
        # 最终状态输出（与main.py相同）
        if success_count == total_courses:
            self.callback.add_log("INFO", "所有课程学习任务已完成")
            self.callback.update_status("已完成")
            if self.notification:
                self.notification.send("chaoxing : 所有课程学习任务已完成")
            return True
        else:
            self.callback.add_log("WARNING", f"部分课程未完成，成功: {success_count}/{total_courses}")
            self.callback.update_status("部分完成")
            return False