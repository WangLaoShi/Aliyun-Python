# Python 一篇概全 · 交互教程

## 启动

在终端进入本目录，使用你准备授课的 Python 环境：

```bash
cd /Users/luosen/Documents/GitHub/Aliyun-Python/v2610
python3 -m pip install -r requirements.txt
python3 build_preview.py
python3 server.py
```

然后访问 http://127.0.0.1:8765 。直接双击 HTML 可以阅读，但不能请求本地接口。

端口已占用时：`TUTORIAL_PORT=8766 python3 server.py`，并访问对应端口。

## 使用

- 左侧目录定位章节，中间可修改 Python 示例，右侧围绕选定代码与 AI 对话。
- 点击“让 AI 解释”选择代码并填入问题，再点击“发送问题”；连续追问保留最近五轮，切换代码会新建对话。
- 页面填写百炼 API Key，只保留在页面内存，刷新即清空，不写浏览器存储或文件。也可在启动前自行设置 `DASHSCOPE_API_KEY` 环境变量。
- 当前按提供的示例调用 `dashscope.Generation.call(model="qwen-plus")`，开启 `stream` 和 `incremental_output`。这是直接模型调用，尚不是百炼已发布应用 Agent；接入应用需要应用标识和对应协议。
- 地域沿用 SDK 默认值。KEY 必须与服务地域匹配；其他地域可按百炼文档在启动前设置 `DASHSCOPE_HTTP_BASE_URL`。页面不接受任意服务地址，避免把 KEY 发往错误地址。
- 点击“本机运行”会执行当前编辑器代码。`input()` 的输入提前填写在“标准输入”，每行一个。各代码块互相隔离，承接前文的片段需要补齐变量。
- 运行使用本机 Python，**不是沙箱**，具有当前用户权限。独立临时目录仅用于隔离练习产生的相对路径文件，不限制绝对路径或网络访问。仅限个人本机教学，不部署到公网或多人共享服务器。
- 8 秒超时与输出截断不构成安全隔离。图形窗口和长期交互任务请在编辑器运行。
- 百炼回答默认以 Markdown 预览展示，支持切换原文。使用 Marked 解析、DOMPurify 清理 HTML，代码块使用 highlight.js 高亮。三个依赖都保存在 vendor 中，页面运行时不访问 CDN。失败时显示状态与可操作提示。

## 文件

- `01-Python一篇概全.md`：讲义源文件。
- `build_preview.py`：从讲义生成 HTML。
- `index.html`、`tutorial.css`、`tutorial.js`：页面及交互。
- `server.py`：仅监听 127.0.0.1 的本地 API 与静态文件服务。
- `examples/grade_report.py`：综合示例。

## 验证边界

没有真实 API Key 时不能验证真实模型响应、额度和账号地域权限。可验证请求参数、模拟流式输出及本地执行功能，不代表已经完成账号联调。

官方接口参考：https://www.alibabacloud.com/help/en/model-studio/stream
