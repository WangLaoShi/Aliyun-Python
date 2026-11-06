"""本机教学服务：DashScope 流式讲解，以及明确授权的本机 Python 练习执行。"""
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import sys
import tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parent
TOKEN = secrets.token_urlsafe(32)
SYSTEM = """你是一位耐心的 Python 中文教师。学生在阅读《Python 一篇概全》。
围绕提供的章节和当前代码回答，区分代码实际行为与建议。先直接回答问题，
再以具体输入解释关键步骤，必要时指出边界和错误。不要默认重写完整程序。
学生要求练习时先给提示，不直接给答案。不声称自己运行过代码。"""


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format, *args):
        # 不记录查询、请求正文和凭据。
        pass

    def do_GET(self):
        if self.path == "/api/config":
            self.reply(200, {"token": TOKEN, "environment_key": bool(os.getenv("DASHSCOPE_API_KEY"))})
        else:
            super().do_GET()

    def reply(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.headers.get("X-Tutorial-Token") != TOKEN:
            self.reply(403, {"error": "本地连接凭证已过期，可能是服务刚刚重启。请点击“重新连接”后重试；这不是百炼 API Key 错误。"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 160000:
                raise ValueError("请求为空或过大")
            data = json.loads(self.rfile.read(size))
            if not isinstance(data, dict):
                raise ValueError("请求格式不正确")
            if self.path == "/api/chat":
                self.chat(data)
            elif self.path == "/api/run":
                self.run_code(data)
            else:
                self.reply(404, {"error": "接口不存在"})
        except (ValueError, TypeError) as error:
            self.reply(400, {"error": str(error)})

    def run_code(self, data):
        code = data.get("code", "")
        stdin = data.get("stdin", "")
        if not isinstance(code, str) or not isinstance(stdin, str) or len(code) > 40000:
            raise ValueError("代码或输入格式不正确，代码上限 40000 字符")
        # 这是本机执行，不是安全沙箱。仅用于本人信任的教学练习。
        with tempfile.TemporaryDirectory(prefix="python-tutorial-") as folder:
            script = Path(folder) / "exercise.py"
            script.write_text(code, encoding="utf-8")
            env = {k: v for k, v in os.environ.items() if k in ("PATH", "LANG", "SYSTEMROOT", "TMPDIR")}
            env["PYTHONIOENCODING"] = "utf-8"
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                process = subprocess.Popen(
                    [sys.executable, "-I", "-u", "-c",
                     "import resource,runpy; "
                     "resource.setrlimit(resource.RLIMIT_FSIZE,(2097152,2097152)); "
                     "runpy.run_path('exercise.py',run_name='__main__')"]
                    if os.name == "posix" else [sys.executable, "-I", "-u", str(script)],
                    cwd=folder, start_new_session=True,
                    stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, env=env,
                )
                timed_out = False
                try:
                    process.communicate(stdin.encode(), timeout=8)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    if os.name == "posix":
                        os.killpg(process.pid, signal.SIGKILL)
                    else:
                        process.kill()
                    process.communicate()
                stdout.seek(0)
                stderr.seek(0)
                out = stdout.read(24001)
                err = stderr.read(24001)
                self.reply(200, {
                    "stdout": out[:24000].decode("utf-8", errors="replace"),
                    "stderr": err[:24000].decode("utf-8", errors="replace"),
                    "exit_code": process.returncode,
                    "timed_out": timed_out,
                    "truncated": len(out) > 24000 or len(err) > 24000,
                })

    def chat(self, data):
        try:
            import dashscope
        except ImportError:
            self.reply(503, {"error": "缺少 dashscope，请运行 python -m pip install -r requirements.txt"})
            return
        key = data.get("key") or os.getenv("DASHSCOPE_API_KEY", "")
        if not isinstance(key, str) or not key.strip():
            self.reply(400, {"error": "请填写 API Key，或为服务配置 DASHSCOPE_API_KEY。"})
            return
        question = data.get("question", "")
        code = data.get("code", "")
        chapter = data.get("chapter", "")
        history = data.get("history", [])
        if not all(isinstance(item, str) for item in (question, code, chapter)) or not question.strip():
            raise ValueError("请填写问题")
        if not isinstance(history, list) or len(history) > 12:
            raise ValueError("对话历史过长，请新建对话")
        messages = [{"role": "system", "content": SYSTEM}]
        for message in history:
            if not isinstance(message, dict) or message.get("role") not in ("user", "assistant") or not isinstance(message.get("content"), str):
                raise ValueError("对话历史格式不正确")
            messages.append({"role": message["role"], "content": message["content"]})
        messages.append({"role": "user", "content": f"当前章节：{chapter}\n当前代码：\n```python\n{code}\n```\n学生问题：{question}"})
        self.send_response(200)
        self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        def emit(value):
            self.wfile.write((json.dumps(value, ensure_ascii=False) + "\n").encode())
            self.wfile.flush()

        try:
            responses = dashscope.Generation.call(
                api_key=key.strip(), model="qwen-plus", messages=messages,
                result_format="message", stream=True, incremental_output=True,
                timeout=45,
            )
            usage = None
            for chunk in responses:
                if chunk.status_code != 200:
                    # 平台错误消息可能带请求信息，不转发凭据。
                    emit({"error": f"百炼请求失败：HTTP {chunk.status_code}，错误码 {chunk.code}。请检查 KEY、地域、额度和模型权限。"})
                    return
                if chunk.output and chunk.output.choices:
                    content = chunk.output.choices[0].message.content
                    if content:
                        emit({"text": content})
                if chunk.usage:
                    usage = dict(chunk.usage)
            emit({"done": True, "usage": usage})
        except (BrokenPipeError, ConnectionResetError):
            return
        except Exception:
            emit({"error": "调用未完成，请检查网络、SDK 版本及百炼配置后重试。"})


if __name__ == "__main__":
    port = int(os.getenv("TUTORIAL_PORT", "8765"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"教学页面：http://127.0.0.1:{port}（仅监听本机）", flush=True)
    server.serve_forever()
