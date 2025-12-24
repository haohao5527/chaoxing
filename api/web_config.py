# -*- coding: utf-8 -*-
"""
Web配置管理模块
用于Streamlit Web界面的配置管理，替代原有的ini文件配置系统
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class CommonConfig:
    """通用配置类"""
    username: Optional[str] = None
    password: Optional[str] = None
    course_list: Optional[List[str]] = None
    speed: float = 1.0
    jobs: int = 4
    notopen_action: str = "retry"  # retry, ask, continue
    use_cookies: bool = False


@dataclass 
class TikuConfig:
    """题库配置类"""
    provider: str = "TikuYanxi"
    delay: float = 1.0
    cover_rate: float = 0.8
    submit: bool = True


@dataclass
class NotificationConfig:
    """通知配置类"""
    provider: str = "NotificationService"
    url: str = ""
    enabled: bool = False


class WebConfigManager:
    """Web配置管理器"""
    
    def __init__(self):
        self.common_config = CommonConfig()
        self.tiku_config = TikuConfig()
        self.notification_config = NotificationConfig()
    
    def update_common_config(self, **kwargs):
        """更新通用配置"""
        for key, value in kwargs.items():
            if hasattr(self.common_config, key):
                setattr(self.common_config, key, value)
    
    def update_tiku_config(self, **kwargs):
        """更新题库配置"""
        for key, value in kwargs.items():
            if hasattr(self.tiku_config, key):
                setattr(self.tiku_config, key, value)
    
    def update_notification_config(self, **kwargs):
        """更新通知配置"""
        for key, value in kwargs.items():
            if hasattr(self.notification_config, key):
                setattr(self.notification_config, key, value)
    
    def get_common_dict(self) -> Dict[str, Any]:
        """获取通用配置字典"""
        result = {}
        for key, value in self.common_config.__dict__.items():
            if key == "course_list" and value:
                result[key] = ",".join(value) if isinstance(value, list) else value
            else:
                result[key] = value
        return result
    
    def get_tiku_dict(self) -> Dict[str, Any]:
        """获取题库配置字典"""
        return self.tiku_config.__dict__.copy()
    
    def get_notification_dict(self) -> Dict[str, Any]:
        """获取通知配置字典"""
        return self.notification_config.__dict__.copy()
    
    def validate_config(self) -> List[str]:
        """验证配置，返回错误信息列表"""
        errors = []
        
        # 验证通用配置
        if not self.common_config.use_cookies:
            if not self.common_config.username:
                errors.append("用户名不能为空")
            if not self.common_config.password:
                errors.append("密码不能为空")
        
        if self.common_config.speed < 1.0 or self.common_config.speed > 2.0:
            errors.append("播放速度必须在1.0-2.0之间")
        
        if self.common_config.jobs < 1:
            errors.append("并发数必须大于0")
        
        if self.common_config.notopen_action not in ["retry", "ask", "continue"]:
            errors.append("未开放任务处理方式必须是retry、ask或continue")
        
        # 验证题库配置
        if self.tiku_config.delay < 0:
            errors.append("查询延迟不能为负数")
        
        if not 0 <= self.tiku_config.cover_rate <= 1:
            errors.append("覆盖率必须在0-1之间")
        
        return errors
    
    def load_from_session_state(self, session_state):
        """从Streamlit session_state加载配置"""
        # 通用配置
        self.common_config.username = session_state.get("username")
        self.common_config.password = session_state.get("password")
        self.common_config.use_cookies = session_state.get("use_cookies", False)
        
        course_list_str = session_state.get("course_list", "")
        if course_list_str:
            self.common_config.course_list = [item.strip() for item in course_list_str.split(",") if item.strip()]
        
        self.common_config.speed = float(session_state.get("speed", 1.0))
        self.common_config.jobs = int(session_state.get("jobs", 4))
        self.common_config.notopen_action = session_state.get("notopen_action", "retry")
        
        # 题库配置
        self.tiku_config.provider = session_state.get("tiku_provider", "TikuYanxi")
        self.tiku_config.delay = float(session_state.get("tiku_delay", 1.0))
        self.tiku_config.cover_rate = float(session_state.get("tiku_cover_rate", 0.8))
        self.tiku_config.submit = session_state.get("tiku_submit", True)
        
        # 通知配置
        self.notification_config.provider = session_state.get("notification_provider", "NotificationService")
        self.notification_config.url = session_state.get("notification_url", "")
        self.notification_config.enabled = session_state.get("notification_enabled", False)
    
    def save_to_session_state(self, session_state):
        """保存配置到Streamlit session_state"""
        # 通用配置
        session_state["username"] = self.common_config.username
        session_state["password"] = self.common_config.password
        session_state["use_cookies"] = self.common_config.use_cookies
        session_state["course_list"] = ",".join(self.common_config.course_list) if self.common_config.course_list else ""
        session_state["speed"] = self.common_config.speed
        session_state["jobs"] = self.common_config.jobs
        session_state["notopen_action"] = self.common_config.notopen_action
        
        # 题库配置
        session_state["tiku_provider"] = self.tiku_config.provider
        session_state["tiku_delay"] = self.tiku_config.delay
        session_state["tiku_cover_rate"] = self.tiku_config.cover_rate
        session_state["tiku_submit"] = self.tiku_config.submit
        
        # 通知配置
        session_state["notification_provider"] = self.notification_config.provider
        session_state["notification_url"] = self.notification_config.url
        session_state["notification_enabled"] = self.notification_config.enabled


# 全局配置管理器实例
config_manager = WebConfigManager()