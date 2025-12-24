# 🎓 超星学习通自动化工具 - Streamlit Cloud部署版本

## 🚀 一键部署到Streamlit Cloud

### 📋 部署前准备

1. **Fork此仓库到您的GitHub账户**
2. **访问 [Streamlit Cloud](https://share.streamlit.io/)**
3. **使用GitHub账户登录**

### 🎯 部署步骤

1. **点击"New app"**
2. **选择仓库**：选择您fork的仓库
3. **设置配置**：
   - **Repository**: `your-username/chaoxing`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
4. **点击"Deploy"** 🎉

### ⚙️ 自动配置

项目已包含所有必要的配置文件：

- `requirements.txt` - Python依赖
- `.streamlit/config.toml` - Streamlit配置
- `packages.txt` - 系统依赖（如需要）

## 🔧 功能特性

- 🌐 **纯Streamlit架构** - 无Flask/Celery依赖
- ⚡ **一键部署** - 直接部署到Streamlit Cloud
- 🎨 **现代Web界面** - 响应式设计
- 📊 **实时监控** - 进度跟踪和日志显示
- ⚙️ **可视化配置** - 表单化参数设置
- 🔐 **安全登录** - 支持账号密码和Cookie登录

## 📱 使用说明

1. **访问部署后的应用**
2. **在左侧边栏配置参数**：
   - 登录信息
   - 课程选择
   - 学习设置
   - 题库配置
3. **点击验证配置**确保参数正确
4. **开始执行自动化学习**
5. **实时监控进度和日志**

## 🛠️ 技术架构

### 纯Streamlit技术栈
```
Frontend: Streamlit Web UI
Backend: Python Core APIs
Config: Web-based Forms
Deployment: Streamlit Cloud
```

### 核心模块
- `streamlit_app.py` - 主应用入口
- `api/web_config.py` - Web配置管理
- `api/web_adapter.py` - Web适配器
- `api/base.py` - 核心API功能

## 📦 依赖说明

### Python依赖 (requirements.txt)
- `streamlit>=1.28.0` - Web框架
- `requests>=2.32.5` - HTTP请求
- `beautifulsoup4>=4.14.2` - HTML解析
- `loguru>=0.7.3` - 日志管理
- `pyaes>=1.6.1` - AES加密
- 其他核心依赖...

### 无需系统依赖
项目完全基于Python，无需额外的系统级依赖。

## 🔒 安全说明

- ✅ **无敏感信息硬编码**
- ✅ **配置通过界面输入**
- ✅ **支持Cookie登录**
- ✅ **本地数据处理**

## 📋 项目结构

```
chaoxing/
├── streamlit_app.py        # 🎯 主应用入口
├── requirements.txt        # 📦 Python依赖
├── .streamlit/
│   └── config.toml        # ⚙️ Streamlit配置
├── packages.txt           # 🖥️ 系统依赖（空）
├── api/                   # 🔧 核心API模块
│   ├── web_config.py      # Web配置管理
│   ├── web_adapter.py     # Web适配器
│   └── ...（其他API文件）
├── resource/              # 📁 资源文件
└── README_STREAMLIT.md    # 📖 本文档
```

## 🆚 与本地运行的区别

| 特性 | 本地运行 | Streamlit Cloud |
|------|----------|-----------------|
| 部署方式 | `streamlit run` | 一键部署 |
| 访问方式 | localhost:8501 | 公开URL |
| 配置持久化 | Session State | Session State |
| 数据存储 | 本地文件 | 内存会话 |
| 外部访问 | 需要端口转发 | 公开可访问 |

## 🚨 注意事项

1. **数据隐私**：Streamlit Cloud是公开的，请注意数据隐私
2. **会话限制**：每次刷新页面会重置配置
3. **资源限制**：免费版有CPU和内存限制
4. **使用条款**：请遵守超星平台使用条款

## 🤝 支持

- 📖 [完整文档](./WEB_README.md)
- 🐛 [报告问题](https://github.com/Samueli924/chaoxing/issues)
- 💬 [讨论交流](https://github.com/Samueli924/chaoxing/discussions)

---

🎉 **享受一键部署的便利！**