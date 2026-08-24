#!/usr/bin/env python3
"""Build gdr_gds.html from gdr_gds.md with a self-contained modern design."""

import re
import os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gdr_gds.md")
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gdr_gds.html")
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")


def anchor_id(heading_text):
    """Generate HTML anchor ID from Chinese/English heading text."""
    result = []
    for ch in heading_text:
        if '\u4e00' <= ch <= '\u9fff' or '\u3000' <= ch <= '\u303f':
            result.append(ch)
        elif ch.isalnum() or ch in '-_':
            result.append(ch.lower() if ch.isascii() and ch.isalpha() else ch)
        elif ch in ' \t':
            result.append('-')
    s = ''.join(result)
    s = re.sub(r'-+', '-', s)
    s = s.strip('-')
    return s


def inline_parse(text):
    """Parse inline markdown: **bold**, `code`, ![img](url), [link](url), <autolink>.
    Uses placeholders for code spans so bold markers wrap correctly around them."""
    # 1. Extract code spans into placeholders
    code_spans = []
    def stash_code(m):
        code_spans.append(m.group(1))
        return f'\x00CODE{len(code_spans)-1}\x00'
    text = re.sub(r'(?<!`)`(?!`)(.+?)(?<!`)`(?!`)', stash_code, text)

    # 2. Apply formatting to text without backticks
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" class="figure-img">', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'<(https?://[^>]+)>', r'<a href="\1">\1</a>', text)

    # 3. Restore code spans with HTML escaping
    for i, code in enumerate(code_spans):
        escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = text.replace(f'\x00CODE{i}\x00', f'<code>{escaped}</code>')

    return text


def parse_table_row(line):
    cells = [c.strip() for c in line.strip().strip('|').split('|')]
    return cells


def is_separator_row(cells):
    return all(re.match(r'^[-:]+$', c) for c in cells)


def render_table(rows):
    html = ['<div class="table-wrapper"><table>']
    header_cells = parse_table_row(rows[0])
    sep_cells = parse_table_row(rows[1]) if len(rows) > 1 else []
    if len(rows) > 1 and is_separator_row(sep_cells):
        html.append('<thead><tr>')
        for c in header_cells:
            html.append(f'<th>{inline_parse(c)}</th>')
        html.append('</tr></thead>')
        data_start = 2
    else:
        data_start = 0
    html.append('<tbody>')
    for row in rows[data_start:]:
        cells = parse_table_row(row)
        html.append('<tr>')
        for c in cells:
            html.append(f'<td>{inline_parse(c)}</td>')
        html.append('</tr>')
    html.append('</tbody></table></div>')
    return '\n'.join(html)


def parse_markdown(text):
    lines = text.split('\n')
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped == '---':
            blocks.append(('hr',))
            i += 1
            continue

        if stripped.startswith('```'):
            lang = stripped[3:].strip()
            code_lines = []
            i += 1
            while i < n:
                if lines[i].strip().startswith('```'):
                    i += 1
                    break
                code_lines.append(lines[i])
                i += 1
            blocks.append(('code', lang, code_lines))
            continue

        if stripped.startswith('#### '):
            blocks.append(('h4', stripped[5:].strip()))
            i += 1
            continue
        if stripped.startswith('### '):
            blocks.append(('h3', stripped[4:].strip()))
            i += 1
            continue
        if stripped.startswith('## '):
            blocks.append(('h2', stripped[3:].strip()))
            i += 1
            continue
        if stripped.startswith('# '):
            blocks.append(('h1', stripped[2:].strip()))
            i += 1
            continue

        if '|' in stripped and stripped.startswith('|'):
            table_rows = []
            while i < n and lines[i].strip().startswith('|'):
                table_rows.append(lines[i])
                i += 1
            blocks.append(('table', table_rows))
            continue

        if re.match(r'^- ', stripped):
            items = []
            while i < n and re.match(r'^- ', lines[i].strip()):
                items.append(re.sub(r'^- ', '', lines[i].strip(), 1))
                i += 1
            blocks.append(('ul', items))
            continue

        if re.match(r'^\d+\. ', stripped):
            items = []
            while i < n and re.match(r'^\d+\. ', lines[i].strip()):
                items.append(re.sub(r'^\d+\. ', '', lines[i].strip(), 1))
                i += 1
            blocks.append(('ol', items))
            continue

        if stripped.startswith('> '):
            quote_lines = []
            while i < n and (lines[i].startswith('> ') or lines[i].strip() == '>'):
                content = lines[i][2:] if lines[i].startswith('> ') else ''
                quote_lines.append(content)
                i += 1
            blocks.append(('blockquote', quote_lines))
            continue

        para_lines = []
        while i < n and lines[i].strip() and not (
            lines[i].strip().startswith('#') or
            lines[i].strip().startswith('```') or
            lines[i].strip().startswith('|') or
            lines[i].strip().startswith('- ') or
            lines[i].strip().startswith('> ') or
            lines[i].strip() == '---' or
            re.match(r'^\d+\. ', lines[i].strip())
        ):
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            blocks.append(('para', para_lines))

    return blocks


def blocks_to_html(blocks):
    buf = []
    for block in blocks:
        kind = block[0]
        if kind == 'h1':
            buf.append(f'<header class="page-header"><h1>{inline_parse(block[1])}</h1></header>')
        elif kind == 'h2':
            aid = anchor_id(block[1])
            buf.append(f'<h2 id="{aid}">{inline_parse(block[1])}</h2>')
        elif kind == 'h3':
            aid = anchor_id(block[1])
            buf.append(f'<h3 id="{aid}">{inline_parse(block[1])}</h3>')
        elif kind == 'h4':
            buf.append(f'<h4>{inline_parse(block[1])}</h4>')
        elif kind == 'hr':
            buf.append('<hr>')
        elif kind == 'code':
            lang = block[1]
            code_lines = block[2]
            cls = f' class="language-{lang}"' if lang else ''
            escaped = '\n'.join(code_lines).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            buf.append(f'<pre><code{cls}>{escaped}</code></pre>')
        elif kind == 'table':
            buf.append(render_table(block[1]))
        elif kind == 'ul':
            buf.append('<ul>')
            for item in block[1]:
                buf.append(f'<li>{inline_parse(item)}</li>')
            buf.append('</ul>')
        elif kind == 'ol':
            buf.append('<ol>')
            for item in block[1]:
                buf.append(f'<li>{inline_parse(item)}</li>')
            buf.append('</ol>')
        elif kind == 'blockquote':
            inner = '<br>'.join(inline_parse(l) for l in block[1])
            buf.append(f'<blockquote>{inner}</blockquote>')
        elif kind == 'para':
            text = '<br>'.join(inline_parse(l) for l in block[1])
            buf.append(f'<p>{text}</p>')
    return '\n'.join(buf)


def extract_toc(blocks):
    entries = []
    for block in blocks:
        if block[0] == 'h2':
            text = block[1]
            aid = anchor_id(text)
            entries.append((aid, text))
    return entries


CSS = r"""
:root {
    --bg: #f8f9fb;
    --text: #2c2c2c;
    --sidebar-bg: #1a1a2e;
    --sidebar-text: #c4c4d4;
    --sidebar-active: #4fc3f7;
    --sidebar-hover: #2a2a3e;
    --accent: #1b5e20;
    --code-bg: #1e1e2e;
    --code-text: #e0e0e0;
    --table-stripe: #f0f2f5;
    --table-hover: #e3e8f0;
    --border: #dde1e6;
    --bq-bg: #f0f4f8;
    --bq-border: #1b5e20;
    --link: #1565c0;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC",
                 "PingFang SC", "Microsoft YaHei", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.75;
    font-size: 15px;
}

a { color: var(--link); text-decoration: none; }
a:hover { text-decoration: underline; }

.layout {
    display: flex;
    justify-content: center;
    min-height: 100vh;
    padding-left: 270px;
}

.sidebar {
    position: fixed;
    top: 0; left: 0;
    width: 270px;
    height: 100vh;
    background: var(--sidebar-bg);
    color: var(--sidebar-text);
    overflow-y: auto;
    padding: 24px 20px;
    z-index: 10;
    scrollbar-width: thin;
    scrollbar-color: #444 transparent;
}
.sidebar::-webkit-scrollbar { width: 6px; }
.sidebar::-webkit-scrollbar-thumb { background: #444; border-radius: 3px; }

.sidebar-header {
    font-size: 15px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    letter-spacing: 0.5px;
}

.sidebar ul { list-style: none; }

.sidebar li { margin-bottom: 2px; }

.sidebar a {
    display: block;
    padding: 6px 12px;
    border-radius: 6px;
    color: var(--sidebar-text);
    font-size: 13px;
    line-height: 1.5;
    transition: all 0.15s;
}
.sidebar a:hover {
    background: var(--sidebar-hover);
    color: #fff;
    text-decoration: none;
}
.sidebar a.active {
    background: rgba(79, 195, 247, 0.15);
    color: var(--sidebar-active);
    font-weight: 600;
}

.mobile-nav-toggle {
    display: none;
    position: fixed;
    top: 12px; left: 12px;
    z-index: 20;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 18px;
    cursor: pointer;
}

.content {
    flex: 0 1 auto;
    width: 100%;
    max-width: 920px;
    padding: 48px 56px 80px;
}

.page-header {
    margin-bottom: 36px;
    padding-bottom: 20px;
    border-bottom: 3px solid var(--accent);
}
.page-header h1 {
    font-size: 30px;
    color: #111;
    line-height: 1.3;
}

h2 {
    font-size: 22px;
    color: #111;
    margin: 48px 0 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}
h3 {
    font-size: 18px;
    color: #222;
    margin: 32px 0 12px;
}
h4 {
    font-size: 16px;
    color: #333;
    margin: 24px 0 8px;
}

p { margin: 12px 0; }

hr {
    border: none;
    border-top: 1px solid var(--border);
    margin: 32px 0;
}

pre {
    background: var(--code-bg);
    color: var(--code-text);
    border-radius: 8px;
    padding: 18px 22px;
    overflow-x: auto;
    margin: 16px 0;
    font-size: 13px;
    line-height: 1.6;
}
pre code {
    font-family: "Cascadia Code", "Fira Code", "JetBrains Mono", "Consolas",
                 "Courier New", monospace;
    background: none;
    padding: 0;
    font-size: inherit;
}

code {
    font-family: "Cascadia Code", "Fira Code", "JetBrains Mono", "Consolas",
                 "Courier New", monospace;
    background: #e8ecef;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.9em;
    color: #c7254e;
}

ul, ol { margin: 10px 0; padding-left: 28px; }
li { margin: 4px 0; }

blockquote {
    background: var(--bq-bg);
    border-left: 4px solid var(--bq-border);
    margin: 16px 0;
    padding: 12px 20px;
    border-radius: 0 8px 8px 0;
    color: #4a5568;
}

.table-wrapper {
    overflow-x: auto;
    margin: 16px 0;
}
table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    font-size: 13.5px;
}
thead th {
    background: var(--accent);
    color: #fff;
    padding: 10px 14px;
    text-align: left;
    font-weight: 600;
    white-space: nowrap;
}
tbody td {
    padding: 8px 14px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}
tbody tr:nth-child(even) { background: var(--table-stripe); }
tbody tr:hover { background: var(--table-hover); }
tbody tr:last-child td { border-bottom: none; }

@media (max-width: 768px) {
    .layout { flex-direction: column; padding-left: 0; }

    .sidebar {
        position: fixed;
        top: 0; left: 0;
        width: 100%;
        height: auto;
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
        padding: 0 20px;
        z-index: 15;
    }
    .sidebar.open {
        max-height: 80vh;
        overflow-y: auto;
        padding: 16px 20px;
    }
    .sidebar-header { margin-top: 40px; }

    .mobile-nav-toggle { display: block; }

    .content {
        padding: 20px 18px 60px;
        margin-top: 10px;
    }
    .page-header h1 { font-size: 22px; }
    h2 { font-size: 19px; }
    h3 { font-size: 16px; }
    pre { padding: 12px 14px; font-size: 12px; }
    table { font-size: 12px; }
}

.figure {
    margin: 28px auto;
    text-align: center;
    overflow-x: auto;
}
.figure svg {
    max-width: 100%;
    height: auto;
}
.fig-caption {
    margin-top: 10px;
    font-size: 13px;
    color: #666;
    font-style: italic;
}
"""

JS = r"""
(function() {
    var sidebar = document.querySelector('.sidebar');
    var toggle = document.querySelector('.mobile-nav-toggle');
    if (toggle && sidebar) {
        toggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
        });
        sidebar.querySelectorAll('a').forEach(function(a) {
            a.addEventListener('click', function() {
                sidebar.classList.remove('open');
            });
        });
    }

    var links = sidebar.querySelectorAll('a');
    var sections = [];
    links.forEach(function(a) {
        var id = a.getAttribute('href').replace('#', '');
        var el = document.getElementById(id);
        if (el) sections.push({ id: id, el: el, link: a });
    });

    function updateActive() {
        var scrollY = window.scrollY + 80;
        var active = null;
        for (var i = sections.length - 1; i >= 0; i--) {
            if (sections[i].el.offsetTop <= scrollY) {
                active = sections[i];
                break;
            }
        }
        links.forEach(function(a) { a.classList.remove('active'); });
        if (active) active.link.classList.add('active');
        else if (sections.length) sections[0].link.classList.add('active');
    }

    window.addEventListener('scroll', updateActive);
    updateActive();
})();
"""


def embed_svgs(html):
    """Replace external SVG img references with inline SVG content,
    stripping fixed width/height so CSS can scale responsively."""
    def replace_img(m):
        src = m.group(1)
        alt = m.group(2)
        fpath = os.path.join(FIGS, os.path.basename(src))
        if os.path.isfile(fpath):
            with open(fpath, 'r', encoding='utf-8') as f:
                svg = f.read()
            # Remove fixed width/height attributes from root <svg> tag,
            # letting the viewBox + CSS handle responsive scaling
            svg = re.sub(r'<(svg[^>]*)\s(width|height)="[^"]*"',
                         r'<\1', svg)
            svg = re.sub(r'<(svg[^>]*)\s(width|height)="[^"]*"',
                         r'<\1', svg)
            return f'<div class="figure">{svg}<p class="fig-caption">{alt}</p></div>'
        return m.group(0)
    return re.sub(r'<img src="([^"]+)" alt="([^"]*)" class="figure-img">', replace_img, html)


def build():
    with open(SRC, 'r', encoding='utf-8') as f:
        text = f.read()

    blocks = parse_markdown(text)
    toc_entries = extract_toc(blocks)
    body_html = blocks_to_html(blocks)
    body_html = embed_svgs(body_html)

    toc_items = '\n'.join(
        f'<li><a href="#{aid}">{inline_parse(t)}</a></li>'
        for aid, t in toc_entries
    )

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GPUDirect RDMA (GDR) 与 GPUDirect Storage (GDS) 技术文档</title>
<style>{CSS}</style>
</head>
<body>

<div class="layout">
<button class="mobile-nav-toggle" aria-label="菜单">&#9776;</button>
<nav class="sidebar" id="sidebar">
  <div class="sidebar-header">目 录</div>
  <ul>
{toc_items}
  </ul>
</nav>

<main class="content">
{body_html}
</main>
</div>

<script>{JS}</script>

</body>
</html>'''

    with open(DST, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Built {DST} ({len(html)} bytes, {len(toc_entries)} sections)")


if __name__ == '__main__':
    build()
