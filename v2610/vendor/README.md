# 本地浏览器依赖

固定版本保存在项目中，页面运行时不请求 CDN：

- highlight.js 11.11.1（BSD-3-Clause）：https://github.com/highlightjs/highlight.js
  - 下载：https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js
- Marked 15.0.12（MIT）：https://github.com/markedjs/marked
  - 下载：https://cdn.jsdelivr.net/npm/marked@15.0.12/lib/marked.umd.js
- DOMPurify 3.4.16（Apache-2.0 OR MPL-2.0）：https://github.com/cure53/DOMPurify
  - 下载：https://cdn.jsdelivr.net/npm/dompurify@3.4.16/dist/purify.min.js

保留各脚本内的原始许可证声明。Markdown 先解析，再清理不安全 HTML，最后对代码块高亮。
