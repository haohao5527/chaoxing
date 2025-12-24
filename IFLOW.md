# 超星学习通自动化完成任务点项目

## 项目概述

这是一个用于超星学习通/超星尔雅/泛雅超星平台的自动化完成任务点工具。项目使用 Python 开发，支持多种部署方式：

- 🖥️ **命令行版本** (`main.py`) - 传统的CLI工具
- 🌐 **静态网页版本** (`streamlit_app.py`) - 无需注册的Web应用
- 📱 **响应式界面** - 适配各种设备屏幕

支持视频播放、文档阅读、章节检测、直播任务等多种类型的自动化学习功能。

### 主要技术栈
- **编程语言**: Python 3.13+
- **核心框架**: 
  - `requests` - HTTP 请求处理
  - `beautifulsoup4` - HTML 解析
  - `loguru` - 日志管理
  - `streamlit` - Web 界面框架
  - `openai` - AI 接口支持

### 项目结构
```
chaoxing/
├── main.py                 # 命令行版本入口
├── streamlit_app.py        # Streamlit Web 版本入口
├── run_web.py             # Web 应用启动脚本
├── api/                    # 核心功能模块
│   ├── base.py            # 超星 API 核心类和主要功能
│   ├── answer.py          # 题库接口和答题功能
│   ├── captcha.py         # 验证码识别
│   ├── cipher.py          # AES 加密解密
│   ├── config.py          # 全局配置常量
│   ├── cookies.py         # Cookie 管理
│   ├── decode.py          # 页面数据解析
│   ├── font_decoder.py    # 字体解码器
│   ├── live.py            # 直播任务处理
│   ├── live_process.py    # 直播处理逻辑
│   ├── logger.py          # 日志功能
│   ├── notification.py    # 外部通知
│   ├── process.py         # 进度显示工具
│   ├── web_config.py      # Web 配置管理
│   └── web_adapter.py     # Web 适配器
├── resource/              # 资源文件
│   └── font_map_table.json # 字体映射表
└── requirements.txt       # 依赖包列表
```

## 构建和运行

### 环境要求
- Python 3.13 或更高版本
- 操作系统: Windows/Linux/macOS

### 安装依赖

#### 方法一：使用 requirements.txt
```bash
pip install -r requirements.txt
```

#### 方法二：使用 pyproject.toml
```bash
pip install .
```

### 运行方式

#### 1. 静态网页版本（推荐）
```bash
# 安装依赖
pip install -r requirements.txt

# 启动Web应用
streamlit run streamlit_app.py

# 或使用启动脚本
python run_web.py
```

**特点**：
- 🌐 无需注册，每位访客独立配置
- 🔒 会话隔离，用户间配置互不影响  
- 🔄 刷新页面自动重置配置
- 📱 响应式界面，适配各种设备

#### 2. 命令行版本
```bash
# 直接运行（交互式输入账号密码）
python main.py

# 使用配置文件运行
python main.py -c config.ini

# 命令行参数运行
python main.py -u 手机号 -p 密码 -l 课程ID1,课程ID2 -a retry
```

#### 3. 打包文件运行
从 [Releases](https://github.com/Samueli924/chaoxing/releases) 下载 exe 文件：
```bash
# 直接运行
./chaoxing.exe

# 使用配置文件
./chaoxing.exe -c config.ini

# 命令行参数
./chaoxing.exe -u "手机号" -p "密码" -l 课程ID1,课程ID2 -a ask
```

#### 4. Docker 运行
```bash
# 构建镜像
docker build -t chaoxing .

# 运行容器
docker run -it chaoxing

# 使用自定义配置文件
docker run -it -v /本地路径/config.ini:/config/config.ini chaoxing
```

### 命令行参数说明
- `-c, --config`: 使用配置文件运行
- `-u, --username`: 手机号账号
- `-p, --password`: 登录密码
- `-l, --list`: 要学习的课程ID列表，以逗号分隔
- `-s, --speed`: 视频播放倍速（默认1.0，最大2.0）
- `-j, --jobs`: 同时进行的章节数（默认4）
- `-v, --verbose`: 启用调试模式
- `-a, --notopen-action`: 遇到关闭任务点的处理方式（retry/ask/continue）
- `--use-cookies`: 使用 cookies 登录

### 配置文件说明
配置文件采用 INI 格式，包含以下主要部分：

#### [common] 节
```ini
username = 手机号
password = 密码
course_list = 课程ID1,课程ID2,课程ID3
speed = 1.5
jobs = 4
notopen_action = retry
use_cookies = false
```

#### [tiku] 节（题库配置）
```ini
provider = TikuYanxi
delay = 1.0
cover_rate = 0.8
submit = true
```

#### [notification] 节（通知配置）
```ini
provider = NotificationService
url = 通知服务URL
```

## 开发约定

### 代码风格
- 使用 UTF-8 编码
- 遵循 PEP 8 代码规范
- 使用类型注解提高代码可读性
- 函数和类需要包含详细的文档字符串

### 日志规范
- 使用 `loguru` 库进行日志管理
- 日志级别：DEBUG、INFO、WARNING、ERROR
- 重要操作需要记录详细日志信息

### 错误处理
- 使用自定义异常类（见 `api/exceptions.py`）
- 关键操作需要异常捕获和处理
- 提供友好的错误提示信息

### 测试策略
- 项目目前没有自动化测试框架
- 建议在实际使用前进行小范围测试
- 重点关注登录、课程获取、任务处理等核心功能

## 核心功能模块

### 1. 登录认证 (`api/base.py`)
- 支持账号密码登录
- 支持 Cookie 登录
- 自动处理验证码识别

### 2. 课程管理 (`api/base.py`)
- 获取课程列表
- 过滤指定课程
- 获取课程章节信息

### 3. 任务处理 (`api/base.py`)
- 视频任务：自动播放视频，支持倍速
- 文档任务：自动阅读文档
- 测验任务：支持题库答题
- 阅读任务：自动完成阅读任务
- 直播任务：处理直播任务点

### 4. 题库系统 (`api/answer.py`)
- 支持多种题库接口
- 自动搜索答案
- 支持答案提交和保存

### 5. 通知系统 (`api/notification.py`)
- 支持外部通知服务
- 任务完成通知
- 错误异常通知

## 注意事项

### 安全提醒
- 妥善保管账号密码信息
- 建议使用 Cookie 登录方式
- 避免在公共环境下运行

### 使用限制
- 仅用于学习讨论目的
- 禁止用于商业盈利
- 遵守 GPL-3.0 开源协议

### 性能优化
- 支持多线程并发处理
- 内置请求频率限制
- 智能重试机制

## 扩展开发

### 添加新的题库
1. 在 `api/answer.py` 中继承 `Tiku` 基类
2. 实现 `search_answer` 方法
3. 在配置文件中添加相应的题库配置

### 添加新的任务类型
1. 在 `api/base.py` 的 `process_job` 函数中添加新的任务类型判断
2. 实现相应的处理方法
3. 更新任务类型枚举

### 添加新的通知服务
1. 在 `api/notification.py` 中继承 `Notification` 基类
2. 实现 `send` 方法
3. 在配置文件中添加相应的通知服务配置

## 故障排除

### 常见问题
1. **登录失败**：检查账号密码是否正确，或尝试使用 Cookie 登录
2. **任务无法完成**：检查课程是否已关闭，或配置题库重试
3. **视频播放异常**：检查网络连接，降低播放倍速

### 调试模式
使用 `-v` 参数启用调试模式，查看详细的日志输出：
```bash
python main.py -v
```

### 日志查看
程序运行日志会输出到控制台，包含详细的执行过程和错误信息。