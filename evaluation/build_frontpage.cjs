/** Render the actual README and release notes as an offline documentation preview. */
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');

const root = path.resolve(__dirname, '..');
const out = path.join(root, 'docs', 'preview');
const pages = [
  { input: 'README.md', output: 'index.html', label: 'README' },
  { input: 'RELEASE_NOTES.md', output: 'release-notes.html', label: '릴리즈 노트' },
];

function slug(text) {
  return text.toLowerCase().replace(/<[^>]*>/g, '').replace(/[^\p{L}\p{N}_\s-]/gu, '').trim().replace(/\s/g, '-');
}

function rewriteUrl(url) {
  if (/^(?:[a-z][a-z\d+.-]*:|\/\/|#)/i.test(url)) return url;
  const [file, fragment] = url.split('#');
  const match = pages.find(page => page.input === file);
  return (match ? match.output : '../../' + file) + (fragment === undefined ? '' : '#' + fragment);
}

const css = `
:root { color-scheme: light; --ink:#1f2328; --muted:#59636e; --line:#d1d9e0; --canvas:#f6f8fa; --paper:#fff; --link:#0969da; }
* { box-sizing:border-box; }
body { margin:0; color:var(--ink); background:var(--canvas); font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif; }
a { color:var(--link); text-decoration:none; }
a:hover { text-decoration:underline; }
a:focus-visible { outline:2px solid var(--link); outline-offset:4px; }
.site-head { max-width:1056px; margin:0 auto; padding:26px 24px 20px; display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; }
.site-name { font-weight:650; font-size:18px; }
.preview-label { color:var(--muted); font-size:13px; }
.frame { max-width:1008px; margin:0 auto 48px; background:var(--paper); border:1px solid var(--line); border-radius:6px; overflow:hidden; }
.tabs { display:flex; align-items:center; gap:24px; min-height:55px; padding:0 32px; border-bottom:1px solid var(--line); font-size:14px; }
.tabs a { padding:15px 0; color:var(--muted); }
.tabs a[aria-current=page] { color:var(--ink); font-weight:600; border-bottom:2px solid #6c6bce; }
.tabs .source { margin-left:auto; font-size:12px; }
.markdown-body { padding:32px; overflow-wrap:anywhere; }
.markdown-body > :first-child { margin-top:0; }
.markdown-body img { max-width:100%; height:auto; }
.markdown-body h1 { font-size:28px; line-height:1.4; padding-bottom:16px; margin:24px 0 16px; border-bottom:1px solid var(--line); }
.markdown-body h2 { font-size:23px; line-height:1.4; margin:36px 0 16px; padding-bottom:8px; border-bottom:1px solid var(--line); }
.markdown-body h3 { font-size:19px; margin:24px 0 12px; }
.markdown-body p { margin:0 0 16px; }
.markdown-body p[align=center] { text-align:center; }
.markdown-body h1[align=center] { text-align:center; }
.markdown-body pre { margin:0 0 20px; padding:16px; background:var(--canvas); border-radius:6px; overflow-x:auto; line-height:1.65; }
.markdown-body code { font:85%/1.6 ui-monospace,SFMono-Regular,Consolas,"Malgun Gothic",monospace; padding:0.16em 0.35em; background:var(--canvas); border-radius:4px; }
.markdown-body pre code { padding:0; background:transparent; white-space:pre-wrap; overflow-wrap:anywhere; }
.markdown-body blockquote { margin:0 0 20px; padding:0 18px; border-left:4px solid var(--line); color:var(--muted); }
.markdown-body blockquote p { margin:0; }
.markdown-body table { border-collapse:collapse; width:100%; margin:0 0 20px; font-size:15px; }
.markdown-body th, .markdown-body td { border:1px solid var(--line); padding:9px 13px; vertical-align:top; text-align:left; }
.markdown-body th { background:var(--canvas); font-weight:600; }
.markdown-body tr:nth-child(even) td { background:var(--canvas); }
.markdown-body ol, .markdown-body ul { margin:0 0 20px; padding-left:28px; }
.markdown-body li + li { margin-top:8px; }
.foot { padding:18px 32px; color:var(--muted); border-top:1px solid var(--line); font-size:12px; }
@media(max-width:640px) {
 .site-head { padding:18px 16px; gap:4px 12px; }
 .site-name { font-size:16px; }
 .frame { margin:0 10px 24px; }
 .tabs { padding:0 18px; gap:18px; }
 .tabs .source { font-size:11px; }
 .markdown-body { padding:16px; }
 .markdown-body h1 { font-size:22px; }
 .markdown-body h2 { font-size:21px; }
 .markdown-body th, .markdown-body td { padding:8px; }
 .markdown-body table { font-size:14px; }
 .foot { padding:16px; }
}
`;

async function main() {
  const { marked } = await import(pathToFileURL(require.resolve('marked')).href);
  const renderer = new marked.Renderer();
  renderer.heading = function(token) {
    return '<h' + token.depth + ' id="' + slug(token.text) + '">' + this.parser.parseInline(token.tokens) + '</h' + token.depth + '>\n';
  };
  fs.mkdirSync(out, { recursive:true });
  for (const page of pages) {
    const source = fs.readFileSync(path.join(root, page.input), 'utf8');
    const body = marked.parse(source, { gfm:true, renderer }).replace(/(href|src)="([^"]+)"/g, (_, attr, url) => attr + '="' + rewriteUrl(url) + '"');
    const nav = pages.map(item => '<a href="' + item.output + '"' + (item === page ? ' aria-current="page"' : '') + '>' + item.label + '</a>').join('');
    const html = `<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${page.label} · AI Slop 탈곡기</title><style>${css}</style></head>
<body><header class="site-head"><a class="site-name" href="index.html">AI Slop Thresher</a><span class="preview-label">GitHub 문서 미리보기</span></header>
<main class="frame"><nav class="tabs" aria-label="문서">${nav}<a class="source" href="../../${page.input}">원본 Markdown</a></nav><article class="markdown-body">${body}</article><footer class="foot">저장된 Markdown을 렌더링한 로컬 미리보기입니다. GitHub의 실제 화면과 세부 서식은 다를 수 있습니다.</footer></main></body></html>\n`;
    fs.writeFileSync(path.join(out, page.output), html, 'utf8');
    console.log('Rendered ' + page.input + ' -> docs/preview/' + page.output);
  }
}

main().catch(error => { console.error(error); process.exitCode=1; });
