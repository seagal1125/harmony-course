import os
import markdown
import re

# Config
SOURCE_DIR = "../Pro"
OUTPUT_DIR = "."
TEMPLATE = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | 和聲的引力</title>
    <link rel="stylesheet" href="styles.css">
    <style>
        .nav-link[href="{filename}"] {{
            background-color: #eff6ff;
            color: var(--primary-color);
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <nav class="sidebar">
        <a href="index.html" class="sidebar-title">🎵 和聲的引力</a>
        <ul class="nav-list">
            <li class="nav-item"><a href="index.html" class="nav-link">首頁</a></li>
            {nav_items}
        </ul>
    </nav>
    <main class="main-content">
        {content}
    </main>
</body>
</html>
"""

def get_title(content):
    """Extract h1 title from markdown content"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "Untitled"

def clean_filename(filename):
    return filename.replace('.md', '.html')

def build_nav(files):
    core_html = '<div class="nav-section-title">核心課程</div>\n'
    bonus_html = '<div class="nav-section-title" style="margin-top: 1.5rem;">補充教材</div>\n'
    
    for f in files:
        if not f.endswith('.md'): continue
        
        # Read file to get title
        with open(os.path.join(SOURCE_DIR, f), 'r', encoding='utf-8') as file:
            content = file.read()
            title = get_title(content)
            # Simplify title
            short_title = re.sub(r'^第 \d+ 章：', '', title).split('——')[0].split('(Bonus)')[0].strip()
            
        html_filename = clean_filename(f)
        link = f'<li class="nav-item"><a href="{html_filename}" class="nav-link">{short_title}</a></li>\n'
        
        # Check if it's a bonus lesson (14, 15...)
        if "14" in f or "15" in f:
            bonus_html += link
        else:
            core_html += link
            
    return core_html + bonus_html

def convert_admonitions(html):
    """Convert blockquotes that start with [!NOTE] etc to styled divs"""
    html = html.replace('<blockquote>\n<p>[!NOTE]', '<blockquote class="note"><p><strong>NOTE</strong>')
    html = html.replace('<blockquote>\n<p>[!TIP]', '<blockquote class="tip"><p><strong>TIP</strong>')
    html = html.replace('<blockquote>\n<p>[!IMPORTANT]', '<blockquote class="important"><p><strong>IMPORTANT</strong>')
    return html

def main():
    # Get all markdown files
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.md')])
    
    # Build Navigation
    nav_items = build_nav(files)
    
    # Process each file
    for f in files:
        print(f"Processing {f}...")
        input_path = os.path.join(SOURCE_DIR, f)
        output_path = os.path.join(OUTPUT_DIR, clean_filename(f))
        
        with open(input_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
            
        title = get_title(md_content)
        
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        html_content = convert_admonitions(html_content)
        
        # Fill Template
        final_html = TEMPLATE.format(
            title=title,
            nav_items=nav_items,
            content=html_content,
            filename=clean_filename(f)
        )
        
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(final_html)

    # Create Index page
    landing_content = """
# 和聲的引力：從五度圈到音樂創作的完整指南

歡迎來到這套專為自學者設計的音樂理論課程。

## 📚 核心課程 (Core Curriculum)
這些章節構成了一套完整的音樂理論體系，建議按順序學習。

*   **第一部分：建築基石** (Lesson 01-02)
    *   [第 1 章：聲音的物理學](lesson_01.html)
    *   [第 2 章：記譜與時間](lesson_02.html)
*   **第二部分：調性的宇宙** (Lesson 03-04)
    *   [第 3 章：五度圈解密](lesson_03.html)
    *   [第 4 章：小調的變體](lesson_04.html)
*   **第三部分：和聲的功能** (Lesson 05-07)
    *   [第 5 章：縱向結構](lesson_05.html)
    *   [第 6 章：和聲動力學](lesson_06.html)
    *   [第 7 章：橫向連接](lesson_07.html)
*   **第四部分：動態與結構** (Lesson 08-10)
    *   [第 8 章：模進的力量](lesson_08.html)
    *   [第 9 章：經典案例 I (Passacaglia)](lesson_09.html)
    *   [第 10 章：經典案例 II (Autumn Leaves)](lesson_10.html)
*   **第五部分：色彩與擴展** (Lesson 11-13)
    *   [第 11 章：副屬和弦](lesson_11.html)
    *   [第 12 章：調式互換](lesson_12.html)
    *   [第 13 章：進階和聲入門](lesson_13.html)

---

## 🎁 補充教材 (Bonus Tracks)
這些章節是針對特定主題的深度探討，可隨時選讀。

### [第 14 章：終止式武道館](lesson_14.html)
*   **內容**：各種讓音樂「降落」的方法 (10 種 Cadence)。
*   **關聯章節**：建議在學完 **第 6 章 (和聲動力學)** 後閱讀，也與 **第 12 章** 有關。

### [第 15 章：懸浮與釋放 (sus)](lesson_15.html)
*   **內容**：掛留和弦 (sus2, sus4) 的各種用法。
*   **關聯章節**：這是對 **第 5 章 (縱向結構)** 的重要補充。
    """
    
    landing_html = markdown.markdown(landing_content)
    final_index = TEMPLATE.format(
        title="首頁",
        nav_items=nav_items,
        content=landing_html,
        filename="index.html"
    )
    with open(os.path.join(OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as file:
        file.write(final_index)

    print("Build complete!")

if __name__ == "__main__":
    main()
