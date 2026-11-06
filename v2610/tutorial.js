const $ = id => document.getElementById(id);
let token = '', selected = null, busy = false, history = [], contextId = '';
const editors = [];
function highlight(code, language = 'python') {
  if (window.hljs && hljs.getLanguage(language)) return hljs.highlight(code, {language}).value;
  return code.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}
function renderMarkdown(target, text) {
  if (!window.marked || !window.DOMPurify) { target.textContent = text; return; }
  target.innerHTML = DOMPurify.sanitize(marked.parse(text, {gfm:true, breaks:true}), {
    USE_PROFILES: {html:true}, FORBID_TAGS:['img','style','form','input','button','video','audio'],
    FORBID_ATTR:['style'],
  });
  target.querySelectorAll('pre code').forEach(code => {
    const language = [...code.classList].find(name => name.startsWith('language-'))?.slice(9) || 'python';
    code.innerHTML = highlight(code.textContent, language);
  });
  target.querySelectorAll('a').forEach(link => {
    if (!/^https?:/i.test(link.getAttribute('href') || '')) link.removeAttribute('href');
    link.target = '_blank'; link.rel = 'noopener noreferrer';
  });
}
function message(text, role = '') {
  const node = document.createElement('div');
  node.className = 'message ' + role;
  if (role) node.textContent = text;
  else {
    node.classList.add('assistant-answer');
    const toolbar = document.createElement('div'); toolbar.className = 'answer-tools';
    const preview = document.createElement('button'); preview.type='button'; preview.textContent='预览';
    const source = document.createElement('button'); source.type='button'; source.textContent='Markdown 原文';
    const content = document.createElement('div'); content.className = 'markdown-preview';
    let raw = text, rawMode = false, scheduled = null;
    function paint() {
      scheduled = null;
      preview.setAttribute('aria-pressed', String(!rawMode)); source.setAttribute('aria-pressed', String(rawMode));
      content.className = rawMode ? 'markdown-source' : 'markdown-preview';
      if (rawMode) content.textContent = raw; else renderMarkdown(content, raw);
    }
    node.update = value => {raw=value; if(!scheduled) scheduled=setTimeout(paint, 60);};
    node.flush = () => {clearTimeout(scheduled);paint();};
    preview.onclick = () => {rawMode=false;node.flush();};
    source.onclick = () => {rawMode=true;node.flush();};
    toolbar.append(preview, source); node.append(toolbar, content); paint();
  }
  $('messages').append(node);
  node.scrollIntoView({block:'nearest'});
  return node;
}
function select(item) {
  if (selected) selected.editor.classList.remove('selected-code');
  if (contextId !== item.id) { history = []; $('messages').replaceChildren(); }
  selected = item; contextId = item.id;
  item.editor.classList.add('selected-code');
  $('context').textContent = item.chapter + ' · 代码 ' + item.number + '（发送时包含编辑后的完整代码）';
}
async function connect() {
  if (location.protocol === 'file:') throw new Error('这是直接打开的 HTML 文件。请先运行 server.py，再访问 http://127.0.0.1:8765/。');
  try {
    const response = await fetch('/api/config', {cache:'no-store', signal:AbortSignal.timeout(5000)});
    if (!response.ok) throw new Error();
    const config = await response.json();
    if (!config.token) throw new Error();
    token = config.token;
    $('connection').textContent = config.environment_key ? '本地服务已连接 · 可使用环境变量 KEY' : '本地服务已连接 · 请填写百炼 API Key';
  } catch (_) {
    token = '';
    throw new Error('无法连接本地服务。请确认终端中的 server.py 仍在运行，且当前端口正确，再点击“重新连接”。无需清空 API Key。');
  }
}
async function request(path, body) {
  // 每次操作先取得当前服务凭证，服务重启后无需刷新或重新填写 KEY。
  await connect();
  const send = () => fetch(path, {method:'POST', headers:{'Content-Type':'application/json','X-Tutorial-Token':token}, body:JSON.stringify(body)});
  try {
    let response = await send();
    if (response.status === 403) {
      // 本地服务在取得凭证后恰好重启；403 在执行前返回，允许重连一次。
      await connect();
      response = await send();
    }
    return response;
  } catch (_) {
    throw new Error('与本地服务的连接中断。请确认 server.py 正在运行，再点击“重新连接”。');
  }
}
async function run(item) {
  if (!busy) select(item); item.run.disabled = true; item.result.hidden = false; item.result.textContent = '正在本机执行…';
  try {
    const response = await request('/api/run', {code:item.editor.value, stdin:item.stdin.value});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error);
    item.result.textContent = (result.stdout || '') + (result.stderr ? '\n' + result.stderr : '') +
      (result.timed_out ? '\n运行超过 8 秒，已停止。' : '\n退出码：' + result.exit_code) +
      (result.truncated ? '\n输出过长，已截断。' : '');
  } catch (error) { item.result.textContent = error.message; }
  finally {item.run.disabled = false;}
}
document.querySelectorAll('pre > code.language-python').forEach((code, i) => {
  const pre = code.parentElement;
  let previous = pre.previousElementSibling;
  while (previous && previous.tagName !== 'H2') previous = previous.previousElementSibling;
  const item = {id:'code-'+i, chapter:previous ? previous.textContent : 'Python 一篇概全', number:i+1, original:code.textContent};
  const tools = document.createElement('div'); tools.className = 'code-tools';
  const choose = document.createElement('button'); choose.textContent = '让 AI 解释';
  const runButton = document.createElement('button'); runButton.textContent = '本机运行';
  const reset = document.createElement('button'); reset.textContent = '还原';
  tools.append(choose, runButton, reset);
  const editor = document.createElement('textarea'); editor.className='editor'; editor.value=item.original;
  editor.rows=Math.min(22, Math.max(5,item.original.split('\n').length)); editor.spellcheck=false;
  editor.setAttribute('aria-label',item.chapter+' 示例代码 '+item.number);
  const inputDetails = document.createElement('details');
  const summary = document.createElement('summary'); summary.textContent='标准输入（input() 所需内容，每行一个）';
  const stdin = document.createElement('textarea'); stdin.className='stdin'; stdin.setAttribute('aria-label','运行标准输入');
  inputDetails.append(summary,stdin);
  const result = document.createElement('pre'); result.className='run-result'; result.hidden=true;
  const frame = document.createElement('div'); frame.className='code-editor';
  const layer = document.createElement('pre'); layer.className='code-highlight'; layer.setAttribute('aria-hidden','true');
  const colored = document.createElement('code'); layer.append(colored);
  editor.wrap='off'; editor.autocapitalize='off'; editor.autocomplete='off';
  frame.append(layer, editor); pre.replaceWith(frame); frame.before(tools); frame.after(inputDetails,result);
  function repaint() {
    colored.innerHTML=highlight(editor.value + '\n');
    layer.scrollTop=editor.scrollTop;layer.scrollLeft=editor.scrollLeft;
  }
  editor.addEventListener('input',repaint);
  editor.addEventListener('scroll',()=>{layer.scrollTop=editor.scrollTop;layer.scrollLeft=editor.scrollLeft;});
  new ResizeObserver(()=>{layer.style.height=editor.offsetHeight+'px';}).observe(editor);
  repaint();
  Object.assign(item,{editor,stdin,result,run:runButton}); editors.push(item);
  choose.onclick=()=>{if(busy)return;select(item);$('question').value='请解释这段代码的数据流和关键语法，并给出一个检查理解的小问题。';$('question').focus();};
  runButton.onclick=()=>run(item);
  reset.onclick=()=>{editor.value=item.original;repaint();result.hidden=true;};
  editor.addEventListener('focus',()=>{if(!busy)select(item);});
  editor.addEventListener('keydown',event=>{if(event.key==='Tab'){event.preventDefault();editor.setRangeText('    ',editor.selectionStart,editor.selectionEnd,'end');repaint();}});
});
if(editors.length)select(editors[0]);
$('clear').onclick=()=>{if(busy)return;history=[];$('messages').replaceChildren();$('usage').textContent='';};
$('forget').onclick=()=>{$('key').value='';$('connection').textContent='已清空页面 KEY；若服务配置环境变量，仍可使用。';};
document.querySelectorAll('[data-prompt]').forEach(button=>button.onclick=()=>{$('question').value=button.dataset.prompt;$('question').focus();});
$('chat-form').onsubmit=async event=>{
  event.preventDefault(); if(busy || !selected)return;
  const question=$('question').value.trim(); if(!question)return;
  const current=selected; const code=current.editor.value;
  busy=true;$('send').disabled=true;$('clear').disabled=true;$('usage').textContent='正在请求 qwen-plus…';
  message(question,'user');const answer=message('');let text='',done=false;
  try {
    const response=await request('/api/chat',{key:$('key').value,question,code,chapter:current.chapter,history:history.slice(-10)});
    if(!response.ok){const body=await response.json();throw new Error(body.error);}
    const reader=response.body.getReader();const decoder=new TextDecoder();let buffer='';
    function consume(line){
      if(!line.trim())return;const item=JSON.parse(line);
      if(item.error)throw new Error(item.error);
      if(item.text){text+=item.text;answer.update(text);$('messages').scrollTop=$('messages').scrollHeight;}
      if(item.done){done=true;$('usage').textContent=item.usage ? '本次用量：'+JSON.stringify(item.usage) : '回答完成';}
    }
    while(true){const {value,done:ended}=await reader.read();buffer+=decoder.decode(value||new Uint8Array(),{stream:!ended});let pos;
      while((pos=buffer.indexOf('\n'))>=0){const line=buffer.slice(0,pos);buffer=buffer.slice(pos+1);consume(line);}if(ended)break;}
    if(buffer.trim())consume(buffer);
    answer.flush();
    if(!done)throw new Error('响应中断，请重试。');
    history.push({role:'user',content:`章节：${current.chapter}\n代码：\n${code}\n问题：${question}`},{role:'assistant',content:text});
    history=history.slice(-10);$('question').value='';
  }catch(error){answer.flush();message(error.message,'error');$('usage').textContent='本次请求未完成';if(!text)answer.remove();}
  finally{busy=false;$('send').disabled=false;$('clear').disabled=false;}
};
$('reconnect').onclick = async () => {
  $('reconnect').disabled = true;
  try { await connect(); }
  catch (error) { $('connection').textContent = error.message; }
  finally { $('reconnect').disabled = false; }
};
connect().catch(error => { $('connection').textContent = error.message; });
