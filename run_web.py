# -*- coding: utf-8 -*-
"""
超星学习通自动化工具 - Web版本启动脚本
"""

import os
import sys
import subprocess

def main():
    """启动Streamlit应用"""
    print("🎓 超星学习通自动化工具 - Web版本")
    print("=" * 50)
    
    # 检查依赖
    try:
        import streamlit
        print(f"✅ Streamlit 已安装: {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit>=1.28.0"])
        print("✅ Streamlit 安装完成")
    
    # 启动应用
    print("🚀 正在启动Web应用...")
    print("📝 应用将在浏览器中打开: http://localhost:8501")
    print("⚠️  请勿关闭此窗口，关闭窗口将停止服务")
    print("=" * 50)
    
    # 启动Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port", "8501",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()