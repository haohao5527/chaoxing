# -*- coding: utf-8 -*-
"""
静态网页配置管理模块
用于Streamlit静态Web界面的配置管理
每个用户会话都有独立的配置，刷新页面会重置
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class SessionConfig:
    """会话配置类 - 每个用户访问时的独立配置"""
    # 登录配置
    username: Optional[str] = None
    password: Optional[str] = None
    use_cookies: bool = False
    
    # 课程配置
    course_list: Optional[List[str]] = None
    course_list_str: str = ""  # 用于界面显示的字符串格式
    
    # 学习配置
    speed: float = 1.0
    jobs: int = 4
    notopen_action: str = "retry"
    verbose: bool = False
    
    # 题库配置
    tiku_enabled: bool = True
    tiku_provider: str = "TikuYanxi"
    tiku_delay: float = 1.0
    tiku_cover_rate: float = 0.8
    tiku_submit: bool = True
    
    # 通知配置
    notification_enabled: bool = False
    notification_provider: str = "NotificationService"
    notification_url: str = ""


class StaticConfigManager:
    """静态网页配置管理器 - 基于会话，无持久化存储"""
    
    def __init__(self):
        self.config = SessionConfig()
    
    def load_from_session_state(self, session_state):
        """从Streamlit session_state加载配置"""
        for key, value in self.config.__dict__.items():
            if key in session_state:
                setattr(self.config, key, session_state[key])
        
        # 特殊处理课程列表
        if hasattr(self.config, 'course_list_str') and self.config.course_list_str:
            self.config.course_list = [item.strip() for item in self.config.course_list_str.split(",") if item.strip()]
    
    def save_to_session_state(self, session_state):
        """保存配置到Streamlit session_state"""
        for key, value in self.config.__dict__.items():
            session_state[key] = value
    
    def validate_config(self) -> List[str]:
        """验证配置，只验证必要条件，返回错误信息列表"""
        errors = []
        
        # 验证必要的登录配置（二选一）
        if self.config.use_cookies:
            # Cookie登录时，无需验证用户名密码
            pass
        else:
            # 账号密码登录时，必须提供用户名和密码
            if not self.config.username:
                errors.append("使用账号密码登录时，用户名不能为空")
            if not self.config.password:
                errors.append("使用账号密码登录时，密码不能为空")
        
        # 验证必要的课程配置
        # 如果没有指定课程列表，会学习所有课程，所以这不是必要条件
        
        # 验证基本数值合理性（防止明显错误）
        if self.config.speed < 0.5 or self.config.speed > 3.0:
            errors.append("播放速度设置不合理，建议在0.5-3.0之间")
        
        if self.config.jobs < 1 or self.config.jobs > 20:
            errors.append("并发数设置不合理，建议在1-20之间")
        
        # 题库配置仅在启用时验证
        if self.config.tiku_enabled:
            if self.config.tiku_delay < 0:
                errors.append("查询延迟不能为负数")
            
            if not 0 <= self.config.tiku_cover_rate <= 1:
                errors.append("覆盖率必须在0-1之间")
        
        # 通知配置仅在启用时验证
        if self.config.notification_enabled:
            if not self.config.notification_url:
                errors.append("启用通知时，通知URL不能为空")
        
        # 验证基本选择项
        if self.config.notopen_action not in ["retry", "ask", "continue"]:
            errors.append("未开放任务处理方式必须是retry、ask或continue")
        
        return errors
    
    def get_common_dict(self) -> Dict[str, Any]:
        """获取通用配置字典（用于API调用）"""
        return {
            "username": self.config.username,
            "password": self.config.password,
            "use_cookies": self.config.use_cookies,
            "course_list": self.config.course_list or [],
            "speed": self.config.speed,
            "jobs": self.config.jobs,
            "notopen_action": self.config.notopen_action
        }
    
    def get_tiku_dict(self) -> Dict[str, Any]:
        """获取题库配置字典"""
        if not self.config.tiku_enabled:
            return {}
        
        return {
            "provider": self.config.tiku_provider,
            "delay": self.config.tiku_delay,
            "cover_rate": self.config.tiku_cover_rate,
            "submit": self.config.tiku_submit
        }
    
    def get_notification_dict(self) -> Dict[str, Any]:
        """获取通知配置字典"""
        if not self.config.notification_enabled:
            return {}
        
        return {
            "provider": self.config.notification_provider,
            "url": self.config.notification_url
        }
    
    def reset_config(self):
        """重置配置为默认值"""
        self.config = SessionConfig()


# 全局配置管理器实例（每个会话独立）
config_manager = StaticConfigManager()