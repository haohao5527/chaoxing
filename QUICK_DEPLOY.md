# 🌐 静态网页版 - 快速部署指南

## ⚡ 一键部署到Streamlit Cloud

### 📋 部署前准备
1. **删除不需要的文件**：
   ```bash
   rm -rf .github/
   rm app.py
   rm config_template.ini
   rm Dockerfile
   ```

2. **提交到GitHub**：
   ```bash
   git add .
   git commit -m "改造为静态网页版本，支持多用户独立配置"
   git push origin main
   ```

### 🚀 部署步骤
1. 访问 [share.streamlit.io](https://share.streamlit.io/)
2. GitHub登录
3. 点击 "New app"
4. 配置：
   - Repository: `your-username/chaoxing`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
5. 点击 "Deploy" 🎉

## 💻 本地运行

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动应用
```bash
streamlit run streamlit_app.py
```

### 访问应用
打开浏览器访问：http://localhost:8501

## ✨ 静态网页特性

- 🌐 **无需注册** - 每位访客独立配置
- 🔒 **会话隔离** - 用户间配置互不影响
- 🔄 **自动重置** - 刷新页面恢复默认
- 📱 **响应式设计** - 适配各种设备
- ⚡ **即时可用** - 打开即用，无需等待

## 📱 使用说明

1. **配置参数** - 左侧边栏设置
2. **验证配置** - 点击验证按钮
3. **开始执行** - 点击开始按钮
4. **监控进度** - 查看实时状态
5. **查看日志** - 分类显示日志

## 🛠️ 故障排除

### 常见问题
- **配置不保存**：正常现象，刷新会重置
- **无法访问**：检查网络和端口
- **功能异常**：刷新页面重试

### 技术支持
- 📖 [完整文档](./README_STATIC.md)
- 🐛 [报告问题](https://github.com/Samueli924/chaoxing/issues)

---

🎉 **享受静态网页的便利！**