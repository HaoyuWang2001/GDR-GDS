#!/usr/bin/env python3
"""Generate 7 SVG diagrams for GPUDirect RDMA/GDS technical documentation."""

import os

FONT = '"Noto Sans SC", "Microsoft YaHei", "PingFang SC", sans-serif'

# ── Colors ────────────────────────────────────────────────────────────────────
C_TXT = "#333333"
C_TITLE = "#1B5E20"

C_G_FL = "#E8F5E9"          # good fill
C_G_BD = "#4CAF50"          # good border
C_G_AR = "#76B900"          # good arrow

C_B_FL = "#FFEBEE"          # bad fill
C_B_BD = "#EF5350"          # bad border
C_B_AR = "#D32F2F"          # bad arrow

C_CTRL = "#42A5F5"          # control border
C_CTDA = "#1976D2"          # control dashed

C_HW_FL = "#ECEFF1"         # hardware fill
C_HW_BD = "#78909C"         # hardware border

C_USR_FL = "#FFFDE7"        # userspace fill
C_USR_BD = "#FDD835"        # userspace border

C_KRN_FL = "#E3F2FD"        # kernel fill
C_KRN_BD = "#64B5F6"        # kernel border

C_GRAY = "#78909C"
C_BG = "#FAFAFA"


# ── SVG Helpers ────────────────────────────────────────────────────────────────
def svg_start(w, h):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'

def svg_markers():
    return """    <!-- green arrow -->
    <marker id="ag" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#76B900"/>
    </marker>
    <!-- red arrow -->
    <marker id="ar" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#D32F2F"/>
    </marker>
    <!-- blue arrow -->
    <marker id="ab" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#1976D2"/>
    </marker>
    <!-- gray arrow -->
    <marker id="agr" markerWidth="10" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#78909C"/>
    </marker>
    <!-- big green arrow -->
    <marker id="agb" markerWidth="12" markerHeight="8" refX="10" refY="4" orient="auto">
      <polygon points="0 0, 12 4, 0 8" fill="#76B900"/>
    </marker>
    <!-- big blue arrow -->
    <marker id="abb" markerWidth="12" markerHeight="8" refX="10" refY="4" orient="auto">
      <polygon points="0 0, 12 4, 0 8" fill="#1976D2"/>
    </marker>"""

def svg_end():
    return "</svg>"

def rrect(x, y, w, h, f, s, rx=6, ry=6, sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" ry="{ry}" fill="{f}" stroke="{s}" stroke-width="{sw}"/>'

def txt(x, y, s, fs=13, c=C_TXT, a="middle", b=False):
    w = ' font-weight="bold"' if b else ''
    return f"<text x='{x}' y='{y}' font-family='{FONT}' font-size='{fs}' fill='{c}' text-anchor='{a}'{w}>{_esc(s)}</text>"

def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def aline(x1, y1, x2, y2, c, sw=2, dash=None, marker=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{sw}"{d}{m}/>'

def legend(x, y, items, w=280, rh=22):
    """items: list of (color_hex, label_text)"""
    lines = [rrect(x, y, w, len(items) * rh + 10, "#FFFFFF", C_GRAY, sw=1.5)]
    for i, (c, label) in enumerate(items):
        ly = y + 12 + i * rh
        lines.append(rrect(x + 10, ly - 6, 14, 14, c, c, rx=2, ry=2, sw=1))
        lines.append(txt(x + 32, ly + 3, label, 11, C_TXT, "start"))
    return "\n".join(lines)

def brace_text(x, y, label, c=C_TXT):
    """Decorative brace label: [ label ]"""
    return txt(x, y, f"{{  {label}  }}", 13, c, "middle", True)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 1: Traditional vs GPUDirect
# ═══════════════════════════════════════════════════════════════════════════════
def make_fig1():
    W, H = 900, 440
    p = []
    p.append(svg_start(W, H))
    p.append("<defs>")
    p.append(svg_markers())
    p.append("</defs>")
    p.append(f'<rect width="{W}" height="{H}" fill="{C_BG}"/>')

    p.append(txt(W / 2, 35, "图1: 传统路径 vs GPUDirect 直连路径对比", 16, C_TITLE, b=True))

    # ── Left labels ──
    p.append(txt(35, 118, "传统", 13, C_B_AR, "middle", True))
    p.append(txt(35, 248, "GPUDirect", 13, C_G_AR, "middle", True))

    # ── Traditional row (red) ──
    ty = 90
    p.append(rrect(80, ty, 150, 56, C_B_FL, C_B_BD))
    p.append(txt(155, ty + 22, "存储设备 (NVMe/NIC)", 12, C_TXT))
    p.append(txt(155, ty + 40, "CPU Bounce Buffer", 11, C_B_AR))

    p.append(aline(230, ty + 28, 340, ty + 28, C_B_AR, 2.5, marker="ar"))
    p.append(txt(285, ty - 8, "PCIe", 10, C_B_AR))

    p.append(rrect(340, ty, 150, 56, C_B_FL, C_B_BD))
    p.append(txt(415, ty + 22, "CPU Bounce", 12, C_TXT, b=True))
    p.append(txt(415, ty + 40, "Buffer (系统内存)", 11, C_B_AR))

    p.append(aline(490, ty + 28, 600, ty + 28, C_B_AR, 2.5, marker="ar"))
    p.append(txt(545, ty - 8, "PCIe", 10, C_B_AR))

    p.append(rrect(600, ty, 180, 56, C_B_FL, C_B_BD))
    p.append(txt(690, ty + 22, "GPU 显存", 12, C_TXT))
    p.append(txt(690, ty + 40, "(需 CPU 中转)", 11, C_B_AR))

    p.append(txt(470, ty + 75, "×2 拷贝，CPU 瓶颈，高延迟", 12, C_B_AR, b=True))

    # ── GPUDirect row (green) ──
    gy = 220
    p.append(rrect(80, gy, 150, 56, C_G_FL, C_G_BD))
    p.append(txt(155, gy + 30, "存储设备 (NVMe/NIC)", 12, C_TXT))

    p.append(aline(230, gy + 28, 600, gy + 28, C_G_AR, 3.5, marker="agb"))
    p.append(txt(415, gy + 10, "PCIe P2P DMA (直通)", 12, C_G_AR, b=True))

    p.append(rrect(600, gy, 180, 56, C_G_FL, C_G_BD))
    p.append(txt(690, gy + 22, "GPU BAR1 显存", 12, C_TXT))
    p.append(txt(690, gy + 40, "(直接写入)", 11, C_G_AR))

    p.append(txt(470, gy + 75, "零拷贝，绕过 CPU，低延迟", 12, C_G_AR, b=True))

    # ── Middle brace ──
    p.append(brace_text(470, 195, "消除 Bounce Buffer / 带宽提升 2×", C_TXT))

    # Dashed lines around the brace
    p.append(aline(155, 175, 155, 185, C_GRAY, 1, dash="4,2"))
    p.append(aline(780, 175, 780, 185, C_GRAY, 1, dash="4,2"))

    p.append(legend(620, H - 100, [
        (C_B_FL, "传统路径 (CPU 中转)"),
        (C_G_FL, "GPUDirect 直连路径"),
        (C_HW_FL, "PCIe Switch 交换"),
    ]))

    p.append(svg_end())
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 2: GDR Software Stack
# ═══════════════════════════════════════════════════════════════════════════════
def make_fig2():
    W, H = 680, 570
    p = []
    p.append(svg_start(W, H))
    p.append("<defs>" + svg_markers() + "</defs>")
    p.append(f'<rect width="{W}" height="{H}" fill="{C_BG}"/>')
    p.append(txt(W / 2, 32, "图2: GDR 软件栈分层架构", 16, C_TITLE, b=True))

    layers = [
        ("层5 用户态", "CUDA + libibverbs + libmlx5", C_USR_FL, C_USR_BD),
        ("层4 内核 RDMA", "ib_core (peer-memory) + mlx5_ib + mlx5_core", C_KRN_FL, C_KRN_BD),
        ("层3 内核桥接", "nvidia-peermem.ko (peer memory client)", C_G_FL, C_G_BD),
        ("层2 内核 GPU", "nvidia.ko (BAR1 暴露, pin/unpin, DMA 映射)", C_HW_FL, C_HW_BD),
        ("层1 硬件", "ConnectX HCA  ←──PCIe P2P DMA──→  GPU BAR1", C_HW_FL, C_HW_BD),
    ]

    lx, lw = 80, 420
    ly_start = 60
    lh = 70
    gap = 14

    for i, (label, desc, fl, bd) in enumerate(layers):
        y = ly_start + i * (lh + gap)
        p.append(rrect(lx, y, lw, lh, fl, bd))
        p.append(txt(lx + 40, y + lh / 2 - 8, label, 11, C_TXT, "middle"))

        # Desc box
        p.append(rrect(lx + 90, y + 8, lw - 100, lh - 16, "#FFFFFF", bd, sw=1))
        p.append(txt(lx + lw / 2 + 40, y + lh / 2 + 4, desc, 11, C_TXT))

    # ── Left: control plane (blue dashed, downward) ──
    cpx = 55
    cp_top = ly_start + 35
    cp_bot = ly_start + 4 * (lh + gap) + lh - 35
    p.append(aline(cpx, cp_top, cpx, cp_bot, C_CTDA, 2, dash="6,4", marker="abb"))
    p.append(txt(cpx, cp_top - 14, "控制面", 10, C_CTDA, b=True))
    # horizontal stubs to each layer
    for i in range(5):
        sy = ly_start + i * (lh + gap) + lh / 2
        p.append(aline(cpx - 2, sy, lx, sy, C_CTDA, 1.5, dash="4,3"))

    # ── Right: data plane (green thick, downward) ──
    dpx = 540
    p.append(aline(dpx, cp_top, dpx, cp_bot, C_G_AR, 3.5, marker="agb"))
    p.append(txt(dpx, cp_top - 14, "数据面", 10, C_G_AR, b=True))

    # Data path annotation between layers 4→3 and 3→2 (green arrows pointing down through layers)
    # The thick data line already covers this.

    # Right side annotations
    p.append(txt(dpx + 60, ly_start + 35, "Pin GPU 页", 10, C_G_AR))
    p.append(txt(dpx + 60, ly_start + 35 + lh + gap, "查询页表", 10, C_G_AR))
    p.append(txt(dpx + 60, ly_start + 35 + 2 * (lh + gap), "DMA 映射", 10, C_G_AR))

    p.append(legend(30, H - 105, [
        (C_USR_FL, "用户态层"),
        (C_KRN_FL, "内核态层"),
        (C_HW_FL, "硬件层"),
        (C_G_FL, "桥接连通层"),
    ]))

    p.append(svg_end())
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 3: Third-party Driver GDR Data Path
# ═══════════════════════════════════════════════════════════════════════════════
def make_fig3():
    W, H = 880, 460
    p = []
    p.append(svg_start(W, H))
    p.append("<defs>" + svg_markers() + "</defs>")
    p.append(f'<rect width="{W}" height="{H}" fill="{C_BG}"/>')
    p.append(txt(W / 2, 32, "图3: 第三方驱动接入 GDR 数据路径", 16, C_TITLE, b=True))

    # ── Band labels ──
    p.append(txt(70, 68, "用户态", 12, C_USR_BD, "start", True))
    p.append(txt(70, 185, "内核态", 12, C_KRN_BD, "start", True))
    p.append(txt(70, 310, "数据面", 12, C_G_AR, "start", True))

    # ── Userspace band ──
    uy = 75
    p.append(rrect(65, uy - 6, 780, 62, C_USR_FL, C_USR_BD, sw=1.5))
    p.append(rrect(130, uy, 160, 42, "#FFFFFF", C_USR_BD, sw=1.5))
    p.append(txt(210, uy + 25, "cudaMalloc(GPU VA)", 12, C_TXT))
    p.append(aline(290, uy + 21, 340, uy + 21, C_CTDA, 2, marker="ab"))
    p.append(rrect(340, uy, 220, 42, "#FFFFFF", C_USR_BD, sw=1.5))
    p.append(txt(450, uy + 15, "通信库判定 →", 11, C_TXT))
    p.append(txt(450, uy + 30, "SYNC_MEMOPS", 11, C_TXT, b=True))
    p.append(aline(560, uy + 21, 610, uy + 21, C_CTDA, 2, marker="ab"))
    p.append(rrect(610, uy, 180, 42, "#FFFFFF", C_USR_BD, sw=1.5))
    p.append(txt(700, uy + 25, "IOCTL(VA, size)", 12, C_TXT))

    # ── Kernel band ──
    ky = 192
    p.append(rrect(65, ky - 6, 780, 84, C_KRN_FL, C_KRN_BD, sw=1.5))

    # Box 1: 自研驱动
    p.append(rrect(90, ky, 130, 62, "#FFFFFF", C_KRN_BD, sw=1.5))
    p.append(txt(155, ky + 22, "自研驱动", 12, C_TXT, b=True))
    p.append(txt(155, ky + 42, "(入口函数)", 10, C_TXT))
    p.append(aline(220, ky + 31, 270, ky + 31, C_CTDA, 2, marker="ab"))

    # Box 2: nvidia_p2p_get_pages
    p.append(rrect(270, ky, 210, 62, "#FFFFFF", C_G_BD, sw=1.5))
    p.append(txt(375, ky + 18, "nvidia_p2p_get_pages()", 11, C_TXT, b=True))
    p.append(txt(375, ky + 40, "→ page_table (GPU 物理/BAR 地址)", 10, C_TXT))
    p.append(aline(480, ky + 31, 530, ky + 31, C_CTDA, 2, marker="ab"))

    # Box 3: DMA map
    p.append(rrect(530, ky, 200, 62, "#FFFFFF", C_G_BD, sw=1.5))
    p.append(txt(630, ky + 15, "nvidia_p2p_dma_map_pages()", 11, C_TXT, b=True))
    p.append(txt(630, ky + 38, "→ scatter-gather 写入 DMA 寄存器", 10, C_TXT))

    p.append(aline(730, ky + 62, 780, ky + 62, C_CTDA, 2, marker="ab"))

    # ── Data plane band ──
    dy = 305
    p.append(rrect(65, dy - 6, 780, 52, C_HW_FL, C_HW_BD, sw=1.5))
    p.append(rrect(90, dy, 620, 36, "#FFFFFF", C_HW_BD, sw=1.5))
    p.append(txt(400, dy + 23, "自研 PCIe 设备 DMA 引擎  ←───PCIe P2P DMA───→  GPU BAR1 显存", 12, C_TXT))

    # ── Control plane arrow from userspace down to kernel ──
    p.append(aline(410, uy + 42, 410, ky, C_CTDA, 2, dash="6,3", marker="abb"))
    p.append(txt(430, uy + 85, "控制面 (IOCTL)", 9, C_CTDA, "start"))

    # ── Data plane arrow from kernel down to data plane ──
    p.append(aline(600, ky + 84, 600, dy, C_G_AR, 3, marker="agb"))
    p.append(txt(620, ky + 115, "数据面", 9, C_G_AR, "start"))

    # ── Bottom annotations ──
    p.append(txt(W / 2, 395, "控制面 (蓝虚线): 用户 → 内核 → 寄存器编程", 11, C_CTDA))
    p.append(txt(W / 2, 412, "数据面 (绿实线): 设备 DMA 直读 / 写 GPU BAR", 11, C_G_AR))

    p.append(legend(650, H - 90, [
        (C_USR_FL, "用户态"),
        (C_KRN_FL, "内核态"),
        (C_HW_FL, "数据面硬件"),
    ], w=210, rh=18))

    p.append(svg_end())
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 4: Cross-node GDR Data Plane Sequence
# ═══════════════════════════════════════════════════════════════════════════════
def make_fig4():
    W, H = 820, 580
    p = []
    p.append(svg_start(W, H))
    p.append("<defs>" + svg_markers() + "</defs>")
    p.append(f'<rect width="{W}" height="{H}" fill="{C_BG}"/>')
    p.append(txt(W / 2, 32, "图4: 跨节点 GDR 数据面时序流程", 16, C_TITLE, b=True))

    # ── Column headers ──
    p.append(txt(180, 68, "节点 A (发起方)", 14, C_TXT, b=True))
    p.append(txt(620, 68, "节点 B (被动方)", 14, C_TXT, b=True))

    # ── Network band in center ──
    nx = 370
    nw = 80
    ny = 80
    nh = 400
    p.append(rrect(nx, ny, nw, nh, "#ECEFF1", C_GRAY, sw=1.5))
    p.append(txt(nx + nw / 2, ny + nh / 2 - 20, "网", 14, C_GRAY, b=True))
    p.append(txt(nx + nw / 2, ny + nh / 2, "络", 14, C_GRAY, b=True))

    # ── Left column (Node A) ──
    lx = 30
    lw = 310
    bh = 50
    steps_a = [
        "1. 外部应用 ibv_post_send(RDMA_WRITE)",
        "2. libibverbs → libmlx5",
        "3. ConnectX HCA 查询 A 的 mkey 表",
        "4. HCA DMA: 读 GPU A BAR1 (源)",
        "5. CQ 产生 CQE → ibv_poll_cq 完成",
    ]
    ys_a = []
    for i, s in enumerate(steps_a):
        y = 90 + i * 70
        ys_a.append(y)
        clr = C_KRN_BD if "控制" in s or "mkey" in s or "lib" in s else C_G_BD
        fl = C_KRN_FL if "控制" in s or "mkey" in s or "lib" in s else C_G_FL
        p.append(rrect(lx, y, lw, bh, fl, clr))
        # Truncate long text or use smaller font
        fs = 10 if len(s) > 28 else 11
        p.append(txt(lx + lw / 2, y + bh / 2 + 4, s, fs, C_TXT))

    # ── Right column (Node B) ──
    rx = 480
    rw = 310
    steps_b = [
        "1. ConnectX HCA 收到报文",
        "2. HCA 查询 B 的 mkey 表 (用 B 的 rkey)",
        "3. HCA DMA: 写 GPU B BAR1 (目的)",
        "4. B 端 CPU 不参与，被动完成",
    ]
    ys_b = []
    for i, s in enumerate(steps_b):
        y = 90 + i * 70
        ys_b.append(y)
        clr = C_KRN_BD if "mkey" in s else C_G_BD
        fl = C_KRN_FL if "mkey" in s else C_G_FL
        p.append(rrect(rx, y, rw, bh, fl, clr))
        fs = 10 if len(s) > 30 else 11
        p.append(txt(rx + rw / 2, y + bh / 2 + 4, s, fs, C_TXT))

    # ── Control plane arrows (blue dashed) from A→B ──
    # Step 3 (mkey) → network → step 2 (mkey)
    ay = ys_a[2] + bh // 2
    by = ys_b[1] + bh // 2
    p.append(aline(lx + lw, ay, nx, ay, C_CTDA, 1.5, dash="5,3"))
    p.append(aline(nx + nw, by, rx, by, C_CTDA, 1.5, dash="5,3"))
    # Vertical connection within network
    p.append(aline(nx + nw / 2, ay, nx + nw / 2, by, C_CTDA, 1.5, dash="5,3", marker="ab"))
    p.append(txt(nx + nw / 2 + 50, (ay + by) / 2, "控制面\n(蓝虚线)", 9, C_CTDA, "start"))

    # ── Data plane arrow (green thick) from A step 4 → B step 3 ──
    ay4 = ys_a[3] + bh // 2
    by3 = ys_b[2] + bh // 2
    p.append(aline(lx + lw, ay4, nx, ay4, C_G_AR, 3, marker="agb"))
    p.append(aline(nx + nw, by3, rx, by3, C_G_AR, 3, marker="agb"))
    p.append(aline(nx + nw / 2, ay4, nx + nw / 2, by3, C_G_AR, 3, marker="agb"))
    p.append(txt(nx + nw / 2 + 50, (ay4 + by3) / 2, "数据面\n(绿粗线)", 9, C_G_AR, "start"))

    # ── Network annotation ──
    p.append(txt(nx + nw / 2, ny + nh + 16, "RDMA WRITE 报文 (InfiniBand / RoCE)", 11, C_TXT))

    p.append(legend(30, H - 105, [
        (C_G_FL, "DMA 数据面 (实线绿框)"),
        (C_KRN_FL, "控制面 (蓝色虚线)"),
        (C_HW_FL, "硬件 HCA / 网络"),
    ]))

    p.append(svg_end())
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 5: GDS Software Stack
# ═══════════════════════════════════════════════════════════════════════════════
def make_fig5():
    W, H = 680, 660
    p = []
    p.append(svg_start(W, H))
    p.append("<defs>" + svg_markers() + "</defs>")
    p.append(f'<rect width="{W}" height="{H}" fill="{C_BG}"/>')
    p.append(txt(W / 2, 32, "图5: GDS 软件栈分层架构", 16, C_TITLE, b=True))

    layers = [
        ("层6 用户态 (cuFile API)", "外部应用", C_USR_FL, C_USR_BD, "①"),
        ("层5 用户态 (lib)", "libcufile.so ←→ libcuda.so (stream)", C_USR_FL, C_USR_BD, "②"),
        ("层4 内核 GDS", "nvidia-fs.ko (GPLv2)", C_G_FL, C_G_BD, "③"),
        ("层3 内核 VFS", "Linux VFS (虚拟文件系统)", C_KRN_FL, C_KRN_BD, "④"),
        ("层2 内核存储驱动", "ext4/XFS/厂商FS + NVMe 驱动/NVMe-oF/NIC", C_KRN_FL, C_KRN_BD, "⑤⑥"),
        ("层1 硬件", "DMA/RDMA 引擎 (NVMe 控制器 / ConnectX HCA)", C_HW_FL, C_HW_BD, "⑦"),
    ]

    lx, lw = 70, 440
    ly0 = 56
    lh = 58
    gap = 12

    for i, (label, desc, fill, bd, step) in enumerate(layers):
        y = ly0 + i * (lh + gap)
        p.append(rrect(lx, y, lw, lh, fill, bd))
        p.append(txt(lx + 15, y + lh / 2 - 8, f"({step})", 10, C_TXT, "start"))
        p.append(txt(lx + 40, y + lh / 2 + 2, label, 10, C_TXT, "start"))
        # right-side description
        p.append(txt(lx + lw - 15, y + lh / 2 + 2, desc, 10, C_TXT, "end"))

    # ── GPU BAR1 at bottom ──
    gpu_y = ly0 + len(layers) * (lh + gap) + 20
    p.append(rrect(lx, gpu_y, lw, 44, "#E8EAF6", C_G_BD, sw=2))
    p.append(txt(lx + lw / 2, gpu_y + 27, "GPU BAR1 显存 (DMA 目的地 / 源)", 12, C_TXT, b=True))

    # ── PCIe P2P DMA arrow ──
    p.append(aline(lx + lw / 2, gpu_y - 6, lx + lw / 2, gpu_y - 30, C_G_AR, 3, marker="agb"))
    p.append(txt(lx + lw / 2 + 40, gpu_y - 18, "PCIe P2P DMA", 9, C_G_AR, "start"))

    # ── Step annotations on the right side ──
    step_notes = [
        (ly0 + lh / 2, "调用 cuFile API"),
        (ly0 + lh + gap + lh / 2, "IOCTL 下发"),
        (ly0 + 2 * (lh + gap) + lh / 2, "callback: nvfs_io_complete"),
        (ly0 + 3 * (lh + gap) + lh / 2, "VFS 路由"),
        (ly0 + 4 * (lh + gap) + lh / 2, "块设备 I/O"),
        (ly0 + 5 * (lh + gap) + lh / 2, "DMA 传输"),
    ]
    sn_x = lx + lw + 20
    for sy, note in step_notes:
        p.append(aline(lx + lw, sy, sn_x, sy, C_CTDA, 1, dash="4,2"))
        p.append(txt(sn_x + 5, sy + 4, note, 9, C_CTDA, "start"))

    # ── Bottom note ──
    p.append(txt(W / 2, gpu_y + 60, "CUDA 12.8+ NVMe 可绕过 nvidia-fs.ko (上游 PCI P2PDMA)", 10, C_TXT, b=True))

    p.append(legend(50, gpu_y + 20, [
        (C_USR_FL, "用户态"),
        (C_KRN_FL, "内核态"),
        (C_HW_FL, "硬件"),
        (C_G_FL, "GDS 专用层"),
    ], w=250))

    p.append(svg_end())
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 6: Phoenix Architecture Comparison
# ═══════════════════════════════════════════════════════════════════════════════
def make_fig6():
    W, H = 880, 445
    p = []
    p.append(svg_start(W, H))
    p.append("<defs>" + svg_markers() + "</defs>")
    p.append(f'<rect width="{W}" height="{H}" fill="{C_BG}"/>')
    p.append(txt(W / 2, 32, "图6: Phoenix 架构对比", 16, C_TITLE, b=True))

    # ── Left: Current GDS ──
    lx, ly = 30, 60
    lw, lh_box = 380, 48
    # Red border wrapper
    p.append(rrect(lx - 8, ly - 8, lw + 16, 260, "#FFFFFF", C_B_BD, sw=3, rx=8, ry=8))
    p.append(txt(lx + lw / 2, ly + 16, "当前 GDS (有 Phony Buffer)", 14, C_B_AR, b=True))
    p.append(txt(lx + lw / 2, ly + 34, "⚠ 软件开销高 / 额外资源消耗 / 部署复杂", 10, C_B_AR))

    y0 = ly + 50
    boxes_left = [
        ("App", C_USR_FL, C_USR_BD),
        ("libcufile / cuFile API", C_USR_FL, C_USR_BD),
        ("⚠ Phony Buffer\n(host memory)", C_B_FL, C_B_BD),
        ("VFS / 文件系统", C_KRN_FL, C_KRN_BD),
        ("NVMe 存储", C_HW_FL, C_HW_BD),
    ]
    bx = lx + 15
    bw = lw - 30
    for i, (label, fl, bd) in enumerate(boxes_left):
        by = y0 + i * 38
        p.append(rrect(bx, by, bw, 32, fl, bd))
        lines = label.split("\n")
        cy = by + 16
        for j, ln in enumerate(lines):
            fsize = 11 if "⚠" in ln else 11
            c = C_B_AR if "⚠" in ln else C_TXT
            p.append(txt(bx + bw / 2, by + 14 + j * 12, ln, fsize, c))
        if i < len(boxes_left) - 1:
            ny = by + 32 + 3
            p.append(aline(bx + bw / 2, ny, bx + bw / 2, ny + 12, C_B_AR, 2, marker="ar"))

    # ── Right: Phoenix ──
    rx, ry = 460, 60
    rw = 380
    p.append(rrect(rx - 8, ry - 8, rw + 16, 260, "#FFFFFF", C_G_BD, sw=3, rx=8, ry=8))
    p.append(txt(rx + rw / 2, ry + 16, "Phoenix (ZONE_DEVICE 无 Phony Buffer)", 14, C_G_AR, b=True))
    p.append(txt(rx + rw / 2, ry + 34, "✓ 零 bounce buffer / 内核直接寻址 GPU 页", 10, C_G_AR))

    y0 = ry + 50
    boxes_right = [
        ("App", C_USR_FL, C_USR_BD),
        ("libcufile / cuFile API", C_USR_FL, C_USR_BD),
        ("ZONE_DEVICE GPU 显存映射\n(启动时注册)", C_G_FL, C_G_BD),
        ("VFS / 文件系统", C_KRN_FL, C_KRN_BD),
        ("NVMe 存储", C_HW_FL, C_HW_BD),
    ]
    bx = rx + 15
    bw = rw - 30
    for i, (label, fl, bd) in enumerate(boxes_right):
        by = y0 + i * 38
        p.append(rrect(bx, by, bw, 32, fl, bd))
        lines = label.split("\n")
        for j, ln in enumerate(lines):
            p.append(txt(bx + bw / 2, by + 14 + j * 12, ln, 11, C_TXT))
        if i < len(boxes_right) - 1:
            ny = by + 32 + 3
            p.append(aline(bx + bw / 2, ny, bx + bw / 2, ny + 12, C_G_AR, 2, marker="ag"))

    # ── Center arrow: 消除 Phony Buffer ──
    cx = lx + lw + 8 + (rx - lx - lw) / 2
    p.append(aline(lx + lw + 10, ly + 170, rx - 10, ry + 170, C_G_AR, 3, marker="agb"))
    p.append(txt(cx, ly + 150, "消除 Phony Buffer", 12, C_G_AR, b=True))

    # ── Performance data ──
    p.append(rrect(120, 345, 640, 36, "#FFFFFF", C_GRAY, sw=1))
    p.append(txt(440, 368, "性能数据:  软件开销 ↓70.3%  |  KV-cache 2.29×  |  Checkpoint 4.11×", 12, C_TXT, b=True))

    p.append(legend(30, H - 105, [
        (C_B_FL, "Phony Buffer (问题)"),
        (C_G_FL, "ZONE_DEVICE (改进)"),
        (C_KRN_FL, "内核层"),
        (C_HW_FL, "硬件层"),
    ]))

    p.append(svg_end())
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 7: GDR Full Lifecycle (5 Stages)
# ═══════════════════════════════════════════════════════════════════════════════
def make_fig7():
    W, H = 960, 340
    p = []
    p.append(svg_start(W, H))
    p.append("<defs>" + svg_markers() + "</defs>")
    p.append(f'<rect width="{W}" height="{H}" fill="{C_BG}"/>')
    p.append(txt(W / 2, 30, "图7: GDR 全生命周期五阶段时序", 16, C_TITLE, b=True))

    stages = [
        ("阶段0\n启动就绪", [
            "BIOS BAR 分配",
            "OS 加载 nvidia.ko",
            "MLNX_OFED 栈",
            "peermem 注册",
        ], C_HW_FL, C_HW_BD),
        ("阶段1\n内存注册", [
            "cudaMalloc",
            "ibv_reg_mr",
            "peermem 回调",
            "nvidia.ko pin",
            "mkey 表编程",
        ], C_KRN_FL, C_KRN_BD),
        ("阶段2\n元数据交换", [
            "RC QP 建立",
            "互换 rkey+VA",
            "(纯控制面)",
        ], C_KRN_FL, C_CTRL),
        ("阶段3\n数据传输", [
            "ibv_post_send",
            "HCA DMA 读/写 GPU BAR",
            "CQ 完成",
            "(数据面不经 CPU)",
        ], C_G_FL, C_G_BD),
        ("阶段4\n销毁回收", [
            "ibv_dereg_mr",
            "nvidia.ko unpin",
            "cudaFree",
            "free_callback 兜底",
        ], C_B_FL, C_B_BD),
    ]

    bx_y = 65
    bx_h = 155
    bx_w = 160
    gap = 22
    total_w = len(stages) * bx_w + (len(stages) - 1) * gap
    start_x = (W - total_w) / 2

    for i, (title, items, fill, bd) in enumerate(stages):
        x = start_x + i * (bx_w + gap)
        p.append(rrect(x, bx_y, bx_w, bx_h, fill, bd, sw=2.5))
        # Title
        title_lines = title.split("\n")
        for j, tl in enumerate(title_lines):
            tc = C_G_AR if "阶段3" in title else (C_B_AR if "阶段4" in title else C_CTDA)
            p.append(txt(x + bx_w / 2, bx_y + 20 + j * 16, tl, 12, tc, b=True))
        # Items
        y_line = bx_y + 50
        for item in items:
            is_comment = item.startswith("(")
            c = C_B_AR if "阶段4" in title else C_TXT
            fs = 10 if is_comment else 11
            p.append(txt(x + bx_w / 2, y_line, item, fs, c))
            y_line += 16
        # Arrow to next stage
        if i < len(stages) - 1:
            ax1 = x + bx_w
            ax2 = start_x + (i + 1) * (bx_w + gap)
            p.append(aline(ax1 + 2, bx_y + bx_h / 2, ax2 - 2, bx_y + bx_h / 2, C_GRAY, 3, marker="agr"))

    # ── Bottom annotations ──
    annot_y = bx_y + bx_h + 22
    p.append(txt(W / 2 - 160, annot_y, "启动/回收 (灰/橙色)", 10, C_HW_BD, b=True))
    p.append(txt(W / 2, annot_y, "控制面 (蓝色阶段 1-2)", 10, C_CTDA, b=True))
    p.append(txt(W / 2 + 180, annot_y, "数据面 (绿色阶段 3)", 10, C_G_AR, b=True))

    p.append(legend(30, annot_y - 16, [
        (C_HW_FL, "启动 / 就绪"),
        (C_KRN_FL, "控制面"),
        (C_G_FL, "数据面"),
        (C_B_FL, "销毁 / 回收"),
    ], w=220, rh=18))

    p.append(svg_end())
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIGURE 8: Control Plane vs Data Plane
# ═══════════════════════════════════════════════════════════════════════════════
def make_fig8():
    W, H = 900, 540
    p = []
    p.append(svg_start(W, H))
    p.append("<defs>" + svg_markers() + "</defs>")
    p.append(f'<rect width="{W}" height="{H}" fill="{C_BG}"/>')
    p.append(txt(W / 2, 30, "图8: 控制面 vs 数据面核心范式", 16, C_TITLE, b=True))

    # ── Control Plane ──
    p.append(txt(20, 60, "控制面 (Control Plane)", 13, C_CTDA, "start", b=True))
    bx_h, bx_w = 48, 160
    ax, ay = 30, 80
    # App
    p.append(rrect(ax, ay, bx_w, bx_h, C_USR_FL, C_USR_BD))
    p.append(txt(ax + bx_w/2, ay + 20, "外部应用", 12, C_TXT, b=True))
    p.append(txt(ax + bx_w/2, ay + 36, "(CPU 侧代码)", 10, C_TXT))
    # arrow
    p.append(aline(ax + bx_w, ay + bx_h/2, ax + bx_w + 55, ay + bx_h/2, C_CTDA, 2, dash="5,3", marker="abb"))
    # Lib
    lx = ax + bx_w + 65
    p.append(rrect(lx, ay, bx_w + 30, bx_h, C_USR_FL, C_USR_BD))
    p.append(txt(lx + (bx_w+30)/2, ay + 20, "用户态驱动库", 12, C_TXT, b=True))
    p.append(txt(lx + (bx_w+30)/2, ay + 36, "(libcufile / libibverbs)", 10, C_TXT))
    # arrow
    p.append(aline(lx + bx_w + 30, ay + bx_h/2, lx + bx_w + 85, ay + bx_h/2, C_CTDA, 2, dash="5,3", marker="abb"))
    # Kernel
    kx = lx + bx_w + 95
    p.append(rrect(kx, ay, bx_w + 50, bx_h, C_KRN_FL, C_KRN_BD))
    p.append(txt(kx + (bx_w+50)/2, ay + 20, "内核驱动", 12, C_TXT, b=True))
    p.append(txt(kx + (bx_w+50)/2, ay + 36, "(nvidia.ko / nvidia-fs.ko)", 10, C_TXT))

    # control ops labels below
    op_y = ay + bx_h + 16
    p.append(txt(ax + bx_w/2, op_y, "pin / unpin", 10, C_CTDA, b=True))
    p.append(txt(lx + (bx_w+30)/2 - 40, op_y + 14, "callback 注册", 10, C_CTDA))
    p.append(txt(lx + (bx_w+30)/2 + 60, op_y + 14, "IOCTL 下发", 10, C_CTDA))
    p.append(txt(kx + (bx_w+50)/2, op_y, "DMA 寄存器编程", 10, C_CTDA, b=True))

    # Control plane summary box
    c_box_y = op_y + 30
    p.append(rrect(ax, c_box_y, W - 2*ax, 26, "#E3F2FD", C_CTRL, sw=1.5))
    p.append(txt(W/2, c_box_y + 17, "控制面 = CPU 侧软件建立通路（建立映射 → 下发指令 → 处理回调）。数据 DMA 不走此路径。", 11, C_CTDA, b=True))

    # ── CPU Boundary ──
    bound_y = c_box_y + 45
    p.append(aline(ax, bound_y, W - ax, bound_y, C_GRAY, 2, dash="8,4"))
    p.append(rrect(W/2 - 50, bound_y - 11, 100, 22, C_BG, C_GRAY, sw=1))
    p.append(txt(W/2, bound_y + 4, "CPU 边界", 11, C_GRAY, b=True))

    # ── Data Plane ──
    dp_y = bound_y + 22
    p.append(txt(20, dp_y, "数据面 (Data Plane)", 13, C_G_AR, "start", b=True))
    dp_y += 12
    rh = 38

    # Row ①
    r1_y = dp_y + 10
    p.append(txt(ax, r1_y + rh/2 + 4, "①", 14, C_B_AR, "start", b=True))
    p.append(rrect(ax + 25, r1_y, 130, rh, C_B_FL, C_B_BD))
    p.append(txt(ax + 25 + 65, r1_y + rh/2 + 4, "GPU DMA 引擎", 11, C_TXT, b=True))
    p.append(aline(ax + 25 + 130, r1_y + rh/2, ax + 25 + 185, r1_y + rh/2, C_B_AR, 2, marker="ar"))
    p.append(rrect(ax + 25 + 195, r1_y, 150, rh, C_B_FL, C_B_BD))
    p.append(txt(ax + 25 + 195 + 75, r1_y + rh/2 + 4, "CPU Bounce Buffer", 11, C_B_AR, b=True))
    p.append(aline(ax + 25 + 345, r1_y + rh/2, ax + 25 + 395, r1_y + rh/2, C_B_AR, 2, marker="ar"))
    p.append(rrect(ax + 25 + 405, r1_y, 80, rh, C_B_FL, C_B_BD))
    p.append(txt(ax + 25 + 405 + 40, r1_y + rh/2 + 4, "存储/网络", 11, C_B_AR, b=True))
    p.append(txt(W - 20, r1_y + rh/2 + 4, "需要 bounce buffer ✗", 10, C_B_AR, "end"))

    # Row ②
    r2_y = r1_y + rh + 12
    p.append(txt(ax, r2_y + rh/2 + 4, "②", 14, C_B_AR, "start", b=True))
    p.append(rrect(ax + 25, r2_y, 130, rh, C_B_FL, C_B_BD))
    p.append(txt(ax + 25 + 65, r2_y + rh/2 + 4, "CPU load/store", 11, C_TXT, b=True))
    p.append(aline(ax + 25 + 130, r2_y + rh/2, ax + 25 + 185, r2_y + rh/2, C_B_AR, 2, marker="ar"))
    p.append(rrect(ax + 25 + 195, r2_y, 150, rh, C_B_FL, C_B_BD))
    p.append(txt(ax + 25 + 195 + 75, r2_y + rh/2 + 4, "CPU Bounce Buffer", 11, C_B_AR, b=True))
    p.append(aline(ax + 25 + 345, r2_y + rh/2, ax + 25 + 395, r2_y + rh/2, C_B_AR, 2, marker="ar"))
    p.append(rrect(ax + 25 + 405, r2_y, 80, rh, C_B_FL, C_B_BD))
    p.append(txt(ax + 25 + 405 + 40, r2_y + rh/2 + 4, "存储/网络", 11, C_B_AR, b=True))
    p.append(txt(W - 20, r2_y + rh/2 + 4, "需要 bounce buffer ✗", 10, C_B_AR, "end"))

    # Row ③ (green, direct)
    r3_y = r2_y + rh + 12
    p.append(txt(ax, r3_y + rh/2 + 4, "③", 14, C_G_AR, "start", b=True))
    p.append(rrect(ax + 25, r3_y, 140, rh, C_G_FL, C_G_BD))
    p.append(txt(ax + 25 + 70, r3_y + 14, "存储侧 DMA 引擎", 11, C_TXT, b=True))
    p.append(txt(ax + 25 + 70, r3_y + 30, "(NVMe / NIC / RAID)", 9, C_G_AR))
    p.append(aline(ax + 25 + 140, r3_y + rh/2, ax + 25 + 470, r3_y + rh/2, C_G_AR, 4, marker="agb"))
    p.append(txt(ax + 25 + 305, r3_y + rh/2 - 8, "PCIe P2P DMA  直通，不经 CPU", 11, C_G_AR, b=True))
    p.append(rrect(ax + 25 + 490, r3_y, 130, rh, C_G_FL, C_G_BD))
    p.append(txt(ax + 25 + 490 + 65, r3_y + rh/2 + 4, "GPU BAR1 显存", 11, C_G_AR, b=True))
    p.append(txt(W - 20, r3_y + rh/2 + 4, "无需 bounce buffer ✓", 11, C_G_AR, "end", b=True))

    # Data plane summary box
    d_box_y = r3_y + rh + 14
    p.append(rrect(ax, d_box_y, W - 2*ax, 26, C_G_FL, C_G_BD, sw=1.5))
    p.append(txt(W/2, d_box_y + 17, "数据面 = 设备 DMA 引擎直接搬数据，不经 CPU 内存 → 这就是 GDR/GDS 的核心价值", 11, C_G_AR, b=True))

    # ── Legend ──
    p.append(legend(W/2 - 160, d_box_y + 38, [
        (C_CTDA, "控制面（CPU 侧，蓝虚线）"),
        (C_B_AR, "传统路径（需 bounce buffer）"),
        (C_G_AR, "GPUDirect 直连（零拷贝，绿色粗线）"),
    ], w=320, rh=20))

    p.append(svg_end())
    return "\n".join(p)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    outdir = "/home/haoyu/gdr_gds/figs"
    os.makedirs(outdir, exist_ok=True)

    figures = [
        (1, make_fig1, "900×440"),
        (2, make_fig2, "680×570"),
        (3, make_fig3, "880×460"),
        (4, make_fig4, "820×580"),
        (5, make_fig5, "680×660"),
        (6, make_fig6, "880×445"),
        (7, make_fig7, "960×340"),
        (8, make_fig8, "900×540"),
    ]

    for idx, fn, dims in figures:
        svg = fn()
        fpath = os.path.join(outdir, f"fig{idx}.svg")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Generated fig{idx}.svg ({dims})")


if __name__ == "__main__":
    main()
