# GDR-GDS 文档更新工作流

## 何时使用

当你需要修改本仓库的 `gdr_gds.md` 或 `gdr_gds.html` 文档内容时使用本 skill。

## 核心原则

- **`gdr_gds.md` 是唯一真相来源 (source of truth)**
- 所有内容变更先编辑 `.md` 文件，再同步到 `.html` 文件
- 同步方式：运行 `python3 build_html.py` 自动重生成 `.html`

## 工作流步骤

### 1. 编辑 Markdown 源文件

编辑 `gdr_gds.md`，文档结构如下：

- 章节使用 `##`（h2，自动生成目录条目）
- 子章节使用 `###` 或 `####`
- 表格以 `|` 开头，连续行构成一个表格
- 代码块使用 ` ``` ` 包裹
- 插图为 `![描述](figs/figN.svg)` 格式
- 内联格式：`**粗体**`、`` `代码` ``、`[链接](url)`、`<自动链接>`

### 2. 同步 HTML 渲染

```bash
python3 build_html.py
```

此命令：
- 解析 `gdr_gds.md` 生成完整的 `gdr_gds.html`
- 将 SVG 图片内联嵌入（响应式缩放）
- 自动生成侧边栏目录（TOC）
- 嵌入 CSS 样式与 JS 交互（滚动高亮）
- 生成一个自包含的 HTML 文件（无外部依赖）

### 3. 验证

确认两条命令无报错输出：

```bash
python3 build_html.py
# 输出类似：Built gdr_gds.html (xxxxxx bytes, 16 sections)

git diff --stat HEAD -- gdr_gds.html
# 确认变更符合预期
```

## 图片 (SVG) 管理

- SVG 源文件位于 `figs/` 目录（`fig1.svg` ~ `fig8.svg`）
- 生成脚本：`gen_svgs.py`（修改 SVG 后运行此脚本重生成）
- 图片通过 `![描述](figs/figN.svg)` 在 md 中引用
- `build_html.py` 会自动将这些 SVG 内联嵌入 html

## 删除的文件

以下文件已删除（不再维护）：
- `gdr_gds.pptx` — PPT 交付物
- `build_pptx.py` — PPT 生成脚本

## 依赖

- Python 3（标准库，无需额外包）
- SVG 图片（`figs/*.svg`，由 `gen_svgs.py` 生成）