# -*- coding: utf-8 -*-
import base64, os, re
import markdown

BASE = os.path.dirname(os.path.abspath(__file__))
MD_PATH = os.path.join(BASE, "文章.md")
OUT_PATH = os.path.join(BASE, "文章.html")

P   = 'margin:0 0 20px;font-size:16px;line-height:2;color:#333;text-align:justify;'
H2  = 'margin:40px 0 18px;font-size:20px;color:#0F2A5C;border-left:4px solid #2563EB;padding-left:12px;line-height:1.5;'
H3  = 'margin:26px 0 12px;font-size:17px;color:#1a1a1a;'
BQ  = 'margin:0 0 20px;padding:12px 16px;border-left:3px solid #d8d8d8;background:#f7f7f7;color:#888;font-size:15px;line-height:1.9;border-radius:0 6px 6px 0;'
UL  = 'margin:0 0 20px;padding-left:22px;'
LI  = 'font-size:16px;line-height:2;color:#333;margin-bottom:4px;'
HR  = 'border:none;border-top:1px dashed #e0e0e0;margin:34px 0;'
FIG = 'margin:28px 0;text-align:center;'
IMG = 'width:100%;border-radius:8px;display:block;'
CAP = 'margin:10px 0 0;font-size:13px;color:#999;'

with open(MD_PATH, encoding="utf-8") as f:
    md_text = f.read()

title = re.search(r'^#\s+(.+)$', md_text, re.M).group(1).strip()

body = markdown.markdown(md_text)
body = re.sub(r'^<h1>.*?</h1>', '', body, count=1)

fig_no = [0]
def make_figure(img_tag):
    alt = re.search(r'alt="([^"]*)"', img_tag)
    src = re.search(r'src="([^"]*)"', img_tag)
    alt_text = alt.group(1) if alt else ""
    src_path = src.group(1) if src else ""
    fig_no[0] += 1
    abs_path = os.path.join(BASE, src_path.replace("/", os.sep))
    with open(abs_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    cap = f'图{fig_no[0]} · {alt_text}' if alt_text else f'图{fig_no[0]}'
    return ('<figure style="%s"><img style="%s" alt="%s" src="data:image/png;base64,%s"/>'
            '<figcaption style="%s">▲ %s</figcaption></figure>') % (FIG, IMG, alt_text, b64, CAP, cap)

body = re.sub(r'<p>\s*(<img[^>]*/?>)\s*</p>', lambda m: make_figure(m.group(1)), body)

body = body.replace('<h2>', '<h2 style="%s">' % H2)
body = body.replace('<h3>', '<h3 style="%s">' % H3)
body = body.replace('<blockquote>', '<blockquote style="%s">' % BQ)
body = body.replace('<ul>', '<ul style="%s">' % UL)
body = body.replace('<li>', '<li style="%s">' % LI)
body = body.replace('<hr />', '<hr style="%s"/>' % HR)
body = body.replace('<strong>', '<strong style="color:#0F2A5C;">')
body = body.replace('<p><p style=', '<p style=')
body = re.sub(r'<p>(?![^<]*style=)', '<p style="%s">' % P, body)

cjk = len(re.findall(r'[\u4e00-\u9fff]', md_text))
total = len(re.sub(r'\s', '', re.sub(r'!\[.*?\]\(.*?\)', '', md_text)))
minutes = max(1, round(cjk / 300))
total_round = round(total / 100) * 100

header = ('<section style="margin-bottom:30px;">'
          '<h1 style="margin:0;font-size:24px;line-height:1.7;color:#1a1a1a;text-align:center;">%s</h1>'
          '<p style="margin:16px 0 0;text-align:center;color:#999;font-size:14px;">原创 · 全文约%d字 · %d张配图 · 阅读约%d分钟</p>'
          '</section>') % (title, total_round, fig_no[0], minutes)

footer = ('<section style="margin-top:44px;text-align:center;">'
          '<p style="margin:0 0 10px;font-size:15px;color:#999;letter-spacing:4px;">— END —</p>'
          '<p style="margin:0;font-size:13px;color:#b2b2b2;">觉得有收获？点赞、在看、转发，评论区聊聊你的看法</p>'
          '</section>')

html = ('<!DOCTYPE html>\n<html lang="zh-CN">\n<head>\n<meta charset="UTF-8"/>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0"/>\n'
        '<title>%s</title>\n'
        '<style>body{margin:0;padding:26px 0 60px;background:#ededed;'
        'font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Microsoft YaHei",sans-serif;}'
        '.page{max-width:677px;margin:0 auto;background:#fff;padding:38px 30px 42px;'
        'box-shadow:0 1px 4px rgba(0,0,0,.08);}h1{font-weight:bold;}'
        '@media (max-width:720px){.page{padding:24px 16px;}}</style>\n'
        '</head>\n<body>\n<div class="page">\n%s\n%s\n%s\n</div>\n</body>\n</html>'
        ) % (title, header, body, footer)

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("OK:", OUT_PATH, os.path.getsize(OUT_PATH), "bytes,", fig_no[0], "figures")
