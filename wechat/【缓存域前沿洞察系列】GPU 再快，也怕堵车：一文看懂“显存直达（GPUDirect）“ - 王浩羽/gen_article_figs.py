#!/usr/bin/env python3
"""Generate 10 mobile-first SVG figures (+2x PNG) for the WeChat article.

Canvas width 750, fonts >= 13px, Microsoft YaHei rendered via WSL Windows fonts.
Color language: blue = direct/hero path, red = slow path, teal = control flow,
gray = hardware, amber = highlight. Brand tag "GPUDirect" at top-left.
"""

import os
import re
import subprocess

FONT = '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", sans-serif'

C_TXT = "#333333"
C_TITLE = "#0D47A1"
C_G_FL = "#E3F2FD"
C_G_BD = "#1565C0"
C_G_AR = "#1976D2"
C_B_FL = "#FFEBEE"
C_B_BD = "#EF5350"
C_B_AR = "#D32F2F"
C_CTRL = "#00838F"
C_CTDA = "#00838F"
C_C_FL = "#E0F2F1"
C_HW_FL = "#ECEFF1"
C_HW_BD = "#78909C"
C_GRAY = "#78909C"
C_USR_FL = "#FFFDE7"
C_USR_BD = "#FDD835"
C_AMB_FL = "#FFF3E0"
C_AMB_BD = "#FB8C00"
C_AMB_TX = "#E65100"
C_PURP = "#7B1FA2"
C_PURP_FL = "#F3E5F5"
C_UB = "#1565C0"
C_BG = "#FAFAFA"
C_B1 = "#64B5F6"
C_B2 = "#1E88E5"
C_B3 = "#1565C0"
C_B4 = "#0D47A1"

W = 750
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "figs")
FONTS_CONF = os.path.join(HERE, "fonts.conf")


def svg_start(h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
            f'viewBox="0 0 {W} {h}">')


def svg_markers():
    return """    <marker id="ag" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1976D2"/>
    </marker>
    <marker id="agb" markerWidth="12" markerHeight="9" refX="10" refY="4.5" orient="auto">
      <polygon points="0 0, 12 4.5, 0 9" fill="#1976D2"/>
    </marker>
    <marker id="ar" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#D32F2F"/>
    </marker>
    <marker id="ab" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#00838F"/>
    </marker>
    <marker id="abb" markerWidth="12" markerHeight="9" refX="10" refY="4.5" orient="auto">
      <polygon points="0 0, 12 4.5, 0 9" fill="#00838F"/>
    </marker>
    <marker id="agr" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#78909C"/>
    </marker>"""


def head(h, title):
    return [svg_start(h),
            "<defs>" + svg_markers() + "</defs>",
            f'<rect width="{W}" height="{h}" fill="{C_BG}"/>',
            rrect(20, 14, 112, 30, C_TITLE, C_TITLE, rx=15, ry=15, sw=1),
            txt(76, 34, "GPUDirect", 15, "#FFFFFF", b=True),
            txt(W / 2, 46, title, 26, C_TITLE, b=True)]


def rrect(x, y, w, h, f, s, rx=8, ry=8, sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{ry}" fill="{f}" stroke="{s}" stroke-width="{sw}"/>'


def txt(x, y, s, fs=16, c=C_TXT, a="middle", b=False):
    w = ' font-weight="bold"' if b else ''
    return f"<text x='{x}' y='{y}' font-family='{FONT}' font-size='{fs}' fill='{c}' text-anchor='{a}'{w}>{esc(s)}</text>"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def aline(x1, y1, x2, y2, c, sw=2, dash=None, marker=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}"{d}{m}/>'


def circle(cx, cy, r, f, s=None, sw=2):
    st = f' stroke="{s}" stroke-width="{sw}"' if s else ""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{f}"{st}/>'


def pill(x, y, w, h, label, f, s, tc, fs=14, b=True):
    return [rrect(x, y, w, h, f, s, rx=h / 2, ry=h / 2, sw=1.8),
            txt(x + w / 2, y + h / 2 + fs * 0.36, label, fs, tc, b=b)]


def takeaway(y, text, fl=C_G_FL, bd=C_G_BD, tc=C_TXT, w=620):
    x = (W - w) / 2
    return [rrect(x, y, w, 56, fl, bd, sw=1.8),
            txt(W / 2, y + 34, text, 17, tc, b=True)]


def icon_two_boxes(x0, cy, lw, rw, arr_c, label=None, arr2=False, both_blue=False):
    out = [rrect(x0 + 25, cy - 26, 72, 52, C_G_FL if both_blue else "#FFFFFF", C_G_BD if both_blue else C_HW_BD, sw=1.8),
           txt(x0 + 61, cy + 6, lw, 14, C_TXT, b=True)]
    out.append(aline(x0 + 103, cy - 10, x0 + 193, cy - 10, arr_c, 3, marker="ag" if arr_c == C_G_AR else "ab"))
    if arr2:
        out.append(aline(x0 + 197, cy + 12, x0 + 107, cy + 12, arr_c, 3, marker="ag" if arr_c == C_G_AR else "ab"))
    out.append(rrect(x0 + 203, cy - 26, 72, 52, C_G_FL if arr_c == C_G_AR else "#FFFFFF", C_G_BD if arr_c == C_G_AR else C_HW_BD, sw=1.8))
    out.append(txt(x0 + 239, cy + 6, rw, 14, C_TXT, b=True))
    if label:
        out.append(txt(x0 + 150, cy + 36 if arr2 else cy + 14, label, 13, C_GRAY))
    return out


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 1: 中转 vs 直达 + 三重税
# ═════════════════════════════════════════════════════════════════════════════
def make_fig1():
    H = 610
    p = head(H, "同一次搬运，两条路")

    p.append(txt(70, 92, "老路 · 趟趟中转", 18, C_B_AR, "start", True))
    p.append(rrect(70, 106, 160, 70, C_B_FL, C_B_BD))
    p.append(txt(150, 136, "货车", 17))
    p.append(txt(150, 160, "（网卡 / 硬盘）", 13, C_GRAY))
    p.append(aline(230, 141, 310, 141, C_B_AR, 3, marker="ar"))
    p.append(txt(270, 128, "搬卸①", 14, C_B_AR))
    p.append(rrect(310, 101, 190, 80, C_B_FL, C_B_BD))
    p.append(txt(405, 131, "物业中转站", 17, b=True))
    p.append(txt(405, 154, "（CPU · 内存）", 13, C_GRAY))
    p.append(aline(500, 141, 570, 141, C_B_AR, 3, marker="ar"))
    p.append(txt(535, 128, "搬卸②", 14, C_B_AR))
    p.append(rrect(570, 106, 150, 70, C_B_FL, C_B_BD))
    p.append(txt(645, 136, "GPU 仓库", 17))
    p.append(txt(645, 160, "（显存）", 13, C_GRAY))
    p.append(txt(395, 212, "两次搬运 · 必经窄门 · CPU 被抓来帮忙", 15, C_B_AR, b=True))

    p.append(txt(70, 268, "新路 · 直达高速", 18, C_G_AR, "start", True))
    p.append(rrect(70, 282, 160, 70, C_G_FL, C_G_BD))
    p.append(txt(150, 312, "货车", 17))
    p.append(txt(150, 336, "（网卡 / 硬盘）", 13, C_GRAY))
    p.append(aline(240, 317, 560, 317, C_G_AR, 5, marker="agb"))
    p.append(txt(400, 298, "直达高速 · 一次到位", 17, C_G_AR, b=True))
    p.append(rrect(570, 282, 150, 70, C_G_FL, C_G_BD))
    p.append(txt(645, 312, "GPU 仓库", 17))
    p.append(txt(645, 336, "（显存开窗收货）", 13, C_G_AR))
    p.append(txt(395, 388, "一次搬运 · 不过窄门 · CPU 继续干正事", 15, C_G_AR, b=True))

    taxes = [("税① 多搬一倍", 70), ("税② 必经窄门", 300), ("税③ 抓壮丁", 530)]
    for label, tx in taxes:
        p.append(rrect(tx, 432, 190, 58, C_B_FL, C_B_BD, sw=1.8))
        p.append(txt(tx + 95, 468, label, 17, C_B_AR, b=True))

    p.append(rrect(70, 522, 610, 56, "#FFFFFF", C_GRAY, sw=1.5))
    p.append(txt(375, 556, "根源：显存对其他设备不设门牌——谁来都得先寄存在物业", 16))
    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 2: GPUDirect family
# ═════════════════════════════════════════════════════════════════════════════
def make_fig2():
    H = 830
    p = head(H, "GPUDirect 家族：条条大路通显存")
    p.append(rrect(160, 84, 430, 66, C_HW_FL, C_HW_BD, sw=2.5))
    p.append(txt(375, 124, "GPU 显存（工厂的仓库）", 20, b=True))

    p.append(aline(195, 150, 195, 200, C_GRAY, 1.5, dash="5,4"))
    p.append(aline(555, 150, 555, 200, C_GRAY, 1.5, dash="5,4"))
    p.append(aline(195, 470, 195, 500, C_GRAY, 1.5, dash="5,4"))
    p.append(aline(555, 470, 555, 500, C_GRAY, 1.5, dash="5,4"))

    cards = [
        (45, 200, "GDR · 网络直达", "跨机器的网卡直接读写显存",
         "本文主角", C_G_BD, 3, "gdr"),
        (405, 200, "GDS · 存储直达", "硬盘数据直接装进显存",
         "数据装载", C_HW_BD, 1.8, "gds"),
        (45, 500, "P2P · 显卡互达", "同机显卡之间直接互访显存",
         "同机互通", C_HW_BD, 1.8, "p2p"),
        (405, 500, "Async · 自动接力", "数据一到自动开工，算完自动存盘",
         "无人值守", C_HW_BD, 1.8, "async"),
    ]
    for x0, y0, name, desc, tag, bd, sw, icon in cards:
        p.append(rrect(x0, y0, 300, 270, "#FFFFFF", bd, sw=sw))
        cy = y0 + 62
        if icon == "gdr":
            p += icon_two_boxes(x0, cy, "网卡", "显存", C_G_AR, "跨机器")
        elif icon == "gds":
            p += icon_two_boxes(x0, cy, "硬盘", "显存", C_G_AR)
        elif icon == "p2p":
            p += icon_two_boxes(x0, cy, "显存", "显存", C_G_AR, "同机", arr2=True, both_blue=True)
        else:
            p.append(rrect(x0 + 25, cy - 26, 72, 52, "#FFFFFF", C_HW_BD, sw=1.8))
            p.append(txt(x0 + 61, cy + 6, "数据", 14, b=True))
            p.append(circle(x0 + 150, cy, 28, C_USR_FL, C_USR_BD, 2.5))
            p.append(f'<polygon points="{x0+143},{cy-12} {x0+143},{cy+12} {x0+163},{cy}" fill="{C_AMB_TX}"/>')
            p.append(rrect(x0 + 203, cy - 26, 72, 52, C_G_FL, C_G_BD, sw=1.8))
            p.append(txt(x0 + 239, cy + 6, "GPU", 14, b=True))
        p.append(txt(x0 + 150, y0 + 140, name, 19, C_TXT, b=True))
        p.append(txt(x0 + 150, y0 + 176, desc, 15))
        tf, tb, tc = (C_G_FL, C_G_BD, C_G_AR) if icon == "gdr" else (C_HW_FL, C_HW_BD, C_TXT)
        p += pill(x0 + 70, y0 + 205, 160, 36, tag, tf, tb, tc)
    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 3: evolution timeline
# ═════════════════════════════════════════════════════════════════════════════
def make_fig3():
    H = 790
    p = head(H, "十余年演进：从专用通道到开放标准")
    p.append(aline(150, 110, 150, 730, C_GRAY, 4))
    stations = [
        (170, C_B1, "2012 前后 · 网络直达诞生", "网卡第一次绕过中转，直接读写显存（GDR）", "起点", C_G_FL, C_B1, C_B3),
        (340, C_B2, "2020 前后 · 存储直达加入", "硬盘数据不再先落内存，直达显存（GDS）", "扩员", C_G_FL, C_B2, C_B3),
        (510, C_B3, "近几年 · 自动接力出现", "数据一到自动开工，算完自动存盘（Async）", "联动", C_G_FL, C_B3, C_B4),
        (680, C_B4, "现在与未来 · 走向开放标准", "从厂商各自修路，到行业统一标准", "开放", C_G_FL, C_B4, C_B4),
    ]
    for y, dot, title, desc, tag, tf, tb, tc in stations:
        p.append(circle(150, y, 13, dot))
        p.append(txt(190, y - 6, title, 19, C_TXT, "start", True))
        p.append(txt(190, y + 24, desc, 15, C_TXT, "start"))
        p += pill(560, y - 34, 130, 34, tag, tf, tb, tc)
    p.append(txt(190, 750, "（年份为约数，依官方版本推算）", 13, C_GRAY, "start"))
    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 4: GPU memory window
# ═════════════════════════════════════════════════════════════════════════════
def make_fig4():
    H = 660
    p = head(H, "显存开了一扇窗，挂上门牌")

    p.append(rrect(400, 90, 300, 310, C_HW_FL, C_HW_BD, sw=2.5))
    p.append(txt(550, 118, "GPU（工厂）", 17, C_TXT, b=True))
    p.append(rrect(440, 150, 220, 170, C_G_FL, C_G_BD, sw=2))
    p.append(txt(550, 178, "显存（仓库）", 16, C_TXT, b=True))

    p.append(rrect(420, 205, 40, 80, "#FFFFFF", C_G_BD, sw=2.5))
    for i, ch in enumerate("取货窗"):
        p.append(txt(440, 231 + i * 18, ch, 13, C_G_AR, b=True))

    p.append(aline(443, 289, 468, 326, C_GRAY, 1.5, dash="3,2"))
    p.append(rrect(415, 330, 140, 36, C_AMB_FL, C_AMB_BD, sw=2))
    p.append(txt(485, 353, "门牌·显存段", 14, C_AMB_TX, b=True))

    p.append(rrect(60, 208, 130, 78, "#FFFFFF", C_HW_BD, sw=2))
    p.append(txt(125, 238, "货车", 16, b=True))
    p.append(txt(125, 262, "（网卡 / 硬盘）", 13, C_GRAY))
    p.append(circle(100, 300, 14, C_GRAY))
    p.append(circle(100, 300, 6, "#FFFFFF"))
    p.append(circle(160, 300, 14, C_GRAY))
    p.append(circle(160, 300, 6, "#FFFFFF"))

    p.append(aline(198, 245, 412, 245, C_G_AR, 5, marker="ag"))
    p.append(txt(307, 225, "按门牌直达 · 窗口交货", 15, C_G_AR, b=True))

    p.append(rrect(60, 435, 630, 105, C_B_FL, C_B_BD, sw=1.5))
    p.append(txt(78, 480, "以前", 16, C_B_AR, "start", True))
    p.append(rrect(150, 449, 105, 52, "#FFFFFF", C_B_BD, sw=1.5))
    p.append(txt(202, 481, "货车", 13))
    p.append(aline(255, 475, 320, 475, C_B_AR, 2.5, marker="ar"))
    p.append(rrect(320, 449, 155, 52, "#FFFFFF", C_B_BD, sw=1.5))
    p.append(txt(397, 470, "内存中转站", 13, b=True))
    p.append(txt(397, 491, "（先寄存）", 11, C_GRAY))
    p.append(aline(475, 475, 540, 475, C_B_AR, 2.5, marker="ar"))
    p.append(rrect(540, 449, 95, 52, "#FFFFFF", C_B_BD, sw=1.5))
    p.append(txt(587, 481, "显存", 13))
    p.append(txt(375, 523, "数据先绕道内存中转站，再由 CPU 转交显存", 14, C_B_AR))

    p += takeaway(572, "显存在总线上挂了门牌——设备按地址直达，不再需要中转")
    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 5: three steps
# ═════════════════════════════════════════════════════════════════════════════
def make_fig5():
    H = 870
    p = head(H, "一次直达传输的三部曲")
    panels = [
        (85, "1", "拿钥匙 · 登记", C_C_FL, C_CTRL, C_CTDA,
         "登记一段显存，领两把钥匙；这段显存同时被『钉住』——搬运途中不许挪动"),
        (330, "2", "换钥匙 · 递纸条", C_C_FL, C_CTRL, C_CTDA,
         "两台机器互发小纸条，交换门牌和远程钥匙——只递纸条，不搬货"),
        (575, "3", "直达运输 · 货自己跑", C_G_FL, C_G_BD, C_G_AR,
         "网卡拿钥匙按门牌直达显存；CPU 只下单和收回执，全程不碰货"),
    ]
    for y, num, title, fl, bd, tc, note in panels:
        p.append(rrect(55, y, 640, 215, fl, bd, sw=2))
        p.append(circle(95, y + 45, 20, bd))
        p.append(txt(95, y + 52, num, 20, "#FFFFFF", b=True))
        p.append(txt(130, y + 52, title, 19, tc, "start", True))
        if num == "1":
            p.append(rrect(95, y + 85, 130, 56, "#FFFFFF", C_CTRL, sw=1.8))
            p.append(txt(160, y + 118, "应用程序", 15))
            p.append(aline(225, y + 113, 305, y + 113, C_CTDA, 2, dash="5,3", marker="ab"))
            p.append(rrect(305, y + 85, 150, 56, "#FFFFFF", C_CTRL, sw=1.8))
            p.append(txt(380, y + 118, "系统登记处", 15))
            p += pill(495, y + 78, 140, 34, "本地钥匙", C_AMB_FL, C_AMB_BD, C_AMB_TX, 13)
            p += pill(495, y + 118, 140, 34, "远程钥匙", C_AMB_FL, C_AMB_BD, C_AMB_TX, 13)
            p.append(aline(455, y + 95, 493, y + 95, C_CTDA, 1.5, dash="4,3"))
            p.append(aline(455, y + 135, 493, y + 135, C_CTDA, 1.5, dash="4,3"))
        elif num == "2":
            p.append(rrect(110, y + 85, 140, 56, "#FFFFFF", C_CTRL, sw=1.8))
            p.append(txt(180, y + 118, "A 机", 15))
            p.append(rrect(500, y + 85, 140, 56, "#FFFFFF", C_CTRL, sw=1.8))
            p.append(txt(570, y + 118, "B 机", 15))
            p.append(aline(250, y + 103, 500, y + 103, C_CTDA, 2, dash="5,3", marker="ab"))
            p.append(aline(500, y + 127, 250, y + 127, C_CTDA, 2, dash="5,3", marker="ab"))
            p.append(txt(375, y + 92, "小纸条：门牌 + 远程钥匙", 14, C_CTDA, b=True))
        else:
            p.append(rrect(110, y + 85, 150, 56, "#FFFFFF", C_G_BD, sw=1.8))
            p.append(txt(185, y + 110, "网卡（货车）", 15))
            p.append(txt(185, y + 130, "", 12))
            p.append(rrect(480, y + 85, 160, 56, C_G_FL, C_G_BD, sw=1.8))
            p.append(txt(560, y + 118, "显存窗口", 15, b=True))
            p.append(aline(260, y + 113, 478, y + 113, C_G_AR, 5, marker="agb"))
            p.append(txt(369, y + 100, "直达读写", 15, C_G_AR, b=True))
            p.append(rrect(290, y + 148, 170, 32, C_USR_FL, C_USR_BD, sw=1.5))
            p.append(txt(375, y + 169, "CPU：只下单、收回执", 13))
        p.append(txt(375, y + 192, note, 15))
    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 6: cross-node journey
# ═════════════════════════════════════════════════════════════════════════════
def make_fig6():
    H = 870
    p = head(H, "一份数据的跨机之旅：五跳全是硬件")
    nodes = [
        (95, "A 机 · 显存仓库", "（起点）", C_G_FL, C_G_BD),
        (235, "A 机 · 网卡货车", "（数据上车）", C_HW_FL, C_HW_BD),
        (375, "跨机网络", "（高速干道）", "#FFFFFF", C_CTRL),
        (515, "B 机 · 网卡货车", "（收货）", C_HW_FL, C_HW_BD),
        (655, "B 机 · 显存仓库", "（终点 · 直接写入）", C_G_FL, C_G_BD),
    ]
    for i, (y, t1, t2, fl, bd) in enumerate(nodes):
        if i == 2:
            p.append(rrect(170, y, 260, 72, fl, bd, sw=2.5))
            cx = 300
        else:
            p.append(rrect(130, y, 340, 72, fl, bd, sw=2.5))
            cx = 300
        p.append(txt(cx, y + 32, t1, 19, b=True))
        p.append(txt(cx, y + 56, t2, 13, C_GRAY))
        if i < 4:
            p.append(aline(300, y + 74, 300, nodes[i + 1][0] - 3, C_G_AR, 4, marker="agb"))

    p.append(rrect(520, 300, 190, 210, "#FFFFFF", C_GRAY, sw=1.5))
    p.append(txt(615, 336, "两端 CPU 内存", 16, C_GRAY, b=True))
    p.append(txt(615, 364, "（物业中转站）", 13, C_GRAY))
    p.append(txt(615, 402, "全程未参与", 17, C_TXT, b=True))
    p.append(txt(615, 430, "数据一次都没落地", 14, C_TXT))
    p.append(aline(472, 340, 518, 340, C_GRAY, 1.5, dash="4,3"))
    p.append(aline(472, 470, 518, 470, C_GRAY, 1.5, dash="4,3"))

    p += takeaway(778, "五跳全部硬件直运——两端 CPU 内存，一次都没碰")
    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 7: supernode & UnifiedBus
# ═════════════════════════════════════════════════════════════════════════════
def make_fig7():
    H = 750
    p = head(H, "从『手拉手』到『一台大电脑』")

    p.append(txt(65, 88, "传统集群 · 一台台手拉手", 17, C_GRAY, "start", True))
    for i, x in enumerate([65, 225, 385, 545]):
        p.append(rrect(x, 102, 140, 110, C_HW_FL, C_HW_BD))
        p.append(rrect(x + 15, 117, 50, 36, "#FFFFFF", C_HW_BD, sw=1.2))
        p.append(txt(x + 40, 141, "GPU", 11, C_GRAY))
        p.append(rrect(x + 75, 117, 50, 36, "#FFFFFF", C_HW_BD, sw=1.2))
        p.append(txt(x + 100, 141, "GPU", 11, C_GRAY))
        p.append(txt(x + 70, 185, "服务器", 14))
        if i < 3:
            p.append(aline(x + 140, 157, x + 180, 157, C_GRAY, 2, dash="5,4"))
    p.append(txt(375, 243, "路远、还得层层换乘——跨机通信越频繁，越吃亏", 15, C_GRAY))

    p.append(aline(375, 262, 375, 322, C_G_AR, 5, marker="agb"))
    p.append(txt(392, 298, "超节点化", 16, C_G_AR, "start", True))

    p.append(rrect(60, 330, 630, 380, C_G_FL, C_G_BD, sw=3))
    p.append(txt(375, 364, "超节点（机柜连成一台大电脑）", 18, b=True))

    p.append(f'<rect x="150" y="470" width="460" height="130" rx="65" ry="65" fill="none" stroke="{C_UB}" stroke-width="12"/>')
    p.append(txt(380, 543, "灵衢总线 · 高架环线", 17, C_UB, b=True))
    for x in [165, 285, 405, 525]:
        p.append(rrect(x, 412, 100, 40, "#FFFFFF", C_HW_BD, sw=1.5))
        p.append(txt(x + 50, 437, "节点", 14))
        p.append(aline(x + 50, 452, x + 50, 476, C_GRAY, 2))
        p.append(rrect(x, 618, 100, 40, "#FFFFFF", C_HW_BD, sw=1.5))
        p.append(txt(x + 50, 643, "节点", 14))
        p.append(aline(x + 50, 600, x + 50, 622, C_GRAY, 2))
    p.append(txt(375, 690, "环线上：访问别的机器的内存，像访问自己的一样自然", 15, C_TXT))
    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 8: UB-GDR three-layer architecture
# ═════════════════════════════════════════════════════════════════════════════
def make_fig8():
    H = 770
    p = head(H, "让灵衢直达显存：三层各司其职")

    p.append(rrect(60, 90, 460, 92, C_USR_FL, C_USR_BD))
    p.append(txt(290, 122, "① 应用程序", 18, b=True))
    p.append(txt(290, 152, "『我要读写远端那段显存』", 15))
    p.append(aline(290, 182, 290, 218, C_CTDA, 2.5, dash="6,3", marker="ab"))

    p.append(rrect(60, 222, 460, 150, C_C_FL, C_CTRL))
    p.append(txt(290, 250, "② 通信软件 · 办手续", 18, b=True))
    for x, label in [(86, "显存段挂牌"), (232, "地址钉住"), (378, "建翻译表")]:
        p.append(rrect(x, 272, 116, 44, "#FFFFFF", C_CTRL, sw=1.8))
        p.append(txt(x + 58, 300, label, 14))
    p.append(aline(206, 294, 228, 294, C_CTDA, 1.5, marker="ab"))
    p.append(aline(352, 294, 374, 294, C_CTDA, 1.5, marker="ab"))
    p.append(txt(290, 348, "登记 · 锁页 · 建表，一次办好", 14, C_CTDA))
    p.append(aline(290, 372, 290, 408, C_CTDA, 2.5, dash="6,3", marker="ab"))

    p.append(rrect(60, 412, 460, 92, C_G_FL, C_G_BD))
    p.append(txt(290, 444, "③ 灵衢搬运引擎", 18, b=True))
    p.append(txt(290, 474, "按翻译表，直达读写显存", 15))
    p.append(aline(290, 506, 290, 552, C_G_AR, 3.5, marker="ag"))

    p.append(rrect(160, 560, 260, 84, C_G_FL, C_G_BD, sw=2.5))
    p.append(txt(290, 592, "远端 GPU 显存", 18, b=True))
    p.append(txt(290, 620, "（仓库 · 直达窗口）", 13, C_G_AR))

    p.append(rrect(545, 240, 165, 150, C_AMB_FL, C_AMB_BD, sw=2))
    p.append(txt(627, 268, "桥接小屋", 17, C_AMB_TX, b=True))
    p.append(txt(627, 298, "厂商专用接口", 14))
    p.append(txt(627, 322, "只在小屋里调用", 14))
    p.append(txt(627, 352, "主路保持开放", 14, C_AMB_TX, b=True))
    p.append(aline(520, 315, 543, 315, C_AMB_BD, 2, dash="5,3"))

    p.append(rrect(60, 668, 630, 56, "#FFFFFF", C_GRAY, sw=1.5))
    p.append(txt(375, 702, "手续一次办好，之后每次搬运都走直达——数据不再经内存中转", 16, b=True))
    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 9: value badges
# ═════════════════════════════════════════════════════════════════════════════
def make_fig9():
    H = 700
    p = head(H, "直达显存，到底有多值？")
    badges = [
        (170, "更快", "带宽翻倍级", "少一次搬运、少一道窄门", C_G_FL, C_G_BD, C_G_AR),
        (375, "更省", "CPU 归位", "卸下搬运活，专心调度", C_C_FL, C_CTRL, C_CTDA),
        (580, "更稳", "延迟平稳", "不排队过门岗，可预期", C_AMB_FL, C_AMB_BD, C_AMB_TX),
    ]
    for cx, big, sub, cap, fl, bd, tc in badges:
        p.append(circle(cx, 172, 62, fl, bd, 3))
        p.append(txt(cx, 166, big, 30, tc, b=True))
        p.append(txt(cx, 200, sub, 13, tc))
        p.append(txt(cx, 266, cap, 15, C_TXT))
    p.append(aline(75, 300, 675, 300, C_GRAY, 1, dash="6,4"))

    scenarios = [
        (60, "分布式训练", "多机 GPU 高速互换数据", "大模型训练提速", "train"),
        (290, "推理服务", "模型缓存秒级进显存", "用户少等一拍", "infer"),
        (520, "存档读写", "训练快照直达硬盘", "存取不再排队", "save"),
    ]
    for x, name, d1, d2, icon in scenarios:
        p.append(rrect(x, 330, 200, 230, "#FFFFFF", C_HW_BD, sw=1.8))
        cy = x + 100
        if icon == "train":
            for i, bx in enumerate([x + 18, x + 76, x + 134]):
                p.append(rrect(bx, 358, 50, 40, C_G_FL, C_G_BD, sw=1.5))
                p.append(txt(bx + 25, 383, "GPU", 11, C_G_AR, b=True))
                if i < 2:
                    p.append(aline(bx + 50, 378, bx + 58, 378, C_G_AR, 2, marker="ag"))
        elif icon == "infer":
            p.append(rrect(cy - 76, 362, 60, 34, "#FFFFFF", C_HW_BD, sw=1.5))
            p.append(txt(cy - 46, 384, "模型", 12))
            p.append(aline(cy - 14, 379, cy + 14, 379, C_G_AR, 3, marker="ag"))
            p.append(rrect(cy + 16, 362, 60, 34, C_G_FL, C_G_BD, sw=1.5))
            p.append(txt(cy + 46, 384, "显存", 12, C_G_AR, b=True))
        else:
            p.append(rrect(cy - 76, 362, 60, 34, C_G_FL, C_G_BD, sw=1.5))
            p.append(txt(cy - 46, 384, "显存", 12, C_G_AR, b=True))
            p.append(aline(cy - 14, 379, cy + 14, 379, C_G_AR, 3, marker="ag"))
            p.append(circle(cy + 32, 379, 20, "#FFFFFF", C_HW_BD, 2))
            p.append(circle(cy + 32, 379, 6, C_HW_BD))
        p.append(txt(cy, 448, name, 18, C_TXT, b=True))
        p.append(txt(cy, 478, d1, 14))
        p.append(txt(cy, 504, d2, 14))

    p += takeaway(596, "无论传统网络，还是超节点总线——消灭中转，收益都成立")
    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  FIG 10: ping-pong test & scorecard
# ═════════════════════════════════════════════════════════════════════════════
def make_fig10():
    H = 570
    p = head(H, "实测：直达显存 vs CPU 中转")

    for x, name in [(80, "A 机"), (460, "B 机")]:
        p.append(rrect(x, 100, 210, 170, C_HW_FL, C_HW_BD, sw=2.5))
        p.append(txt(x + 105, 130, name, 18, b=True))
        p.append(rrect(x + 30, 150, 150, 70, C_G_FL, C_G_BD, sw=2))
        p.append(txt(x + 105, 191, "显存段", 17, b=True))

    p.append(aline(272, 177, 478, 177, C_G_AR, 3, marker="ag"))
    p.append(aline(478, 193, 272, 193, C_G_AR, 3, marker="ag"))
    p.append(txt(375, 163, "一记『写』过去", 14, C_G_AR, "middle"))
    p.append(txt(375, 213, "一记『写』回来", 14, C_G_AR, "middle"))

    p.append(aline(75, 310, 675, 310, C_GRAY, 1, dash="6,4"))
    p.append(txt(375, 340, "实测数据（V100 显卡）", 17, C_TXT, b=True))

    p.append(rrect(60, 362, 200, 170, "#FFFFFF", C_G_BD, sw=1.8))
    p.append(txt(160, 390, "大压力 · 带宽", 14, C_TXT, b=True))
    p.append(rrect(85, 406, 150, 28, C_G_AR, C_G_AR, rx=4, ry=4, sw=0.5))
    p.append(txt(160, 425, "直达 12.37 GB/s", 12, "#FFFFFF", b=True))
    p.append(rrect(85, 446, 31, 28, C_B_AR, C_B_AR, rx=4, ry=4, sw=0.5))
    p.append(txt(124, 465, "中转 2.59 GB/s", 12, C_B_AR, "start", b=True))
    p.append(txt(160, 512, "4.78×", 26, C_G_AR, b=True))

    p.append(rrect(290, 362, 200, 170, "#FFFFFF", C_G_BD, sw=1.8))
    p.append(txt(390, 390, "大压力 · 时延", 14, C_TXT, b=True))
    p.append(txt(390, 468, "↓79%", 32, C_G_AR, b=True))
    p.append(txt(390, 512, "并发拉满，仍快近八成", 13, C_GRAY))

    p.append(rrect(520, 362, 200, 170, "#FFFFFF", C_G_BD, sw=1.8))
    p.append(txt(620, 390, "小压力 · 平均时延", 14, C_TXT, b=True))
    p.append(txt(620, 468, "↓31%", 32, C_G_AR, b=True))
    p.append(txt(620, 512, "轻载单次往返快三成", 13, C_GRAY))

    p.append("</svg>")
    return "\n".join(p)


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═════════════════════════════════════════════════════════════════════════════
def check_overflow(svg, name):
    m = re.search(r'height="(\d+)"', svg)
    H = int(m.group(1))
    problems = []
    for mm in re.finditer(r"<text x='([\d.]+)' y='([\d.]+)'[^>]*font-size='([\d.]+)'[^>]*"
                          r"text-anchor='(\w+)'[^>]*>([^<]*)</text>", svg):
        x, y, fs, anchor, content = float(mm.group(1)), float(mm.group(2)), float(mm.group(3)), mm.group(4), mm.group(5)
        import html
        content = html.unescape(content)
        if not content:
            continue
        w = sum(fs if ord(ch) > 0x2E7F else fs * 0.55 for ch in content)
        if anchor == "middle":
            left, right = x - w / 2, x + w / 2
        elif anchor == "end":
            left, right = x - w, x
        else:
            left, right = x, x + w
        if left < 4 or right > W - 4 or y > H - 4:
            problems.append(f"  [{name}] y={y:.0f} anchor={anchor} '{content[:24]}' -> [{left:.0f},{right:.0f}]")
    return problems


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    figures = [make_fig1, make_fig2, make_fig3, make_fig4, make_fig5, make_fig6,
               make_fig7, make_fig8, make_fig9, make_fig10]
    all_problems = []
    env = {**os.environ, "FONTCONFIG_FILE": FONTS_CONF}
    for i, fn in enumerate(figures, 1):
        svg = fn()
        svg_path = os.path.join(OUTDIR, f"fig{i}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        png_path = os.path.join(OUTDIR, f"fig{i}.png")
        subprocess.run(["cairosvg", svg_path, "-o", png_path, "--output-width", "1500"],
                       env=env, check=True)
        all_problems += check_overflow(svg, f"fig{i}")
        print(f"fig{i}: svg + png ok")
    if all_problems:
        print("\nOVERFLOW WARNINGS:")
        print("\n".join(all_problems))
    else:
        print("\nno overflow warnings")


if __name__ == "__main__":
    main()
