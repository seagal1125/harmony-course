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
    nav_html = ""
    for f in files:
        if not f.endswith('.md'): continue
        
        # Read file to get title (optional, or just use filename)
        with open(os.path.join(SOURCE_DIR, f), 'r', encoding='utf-8') as file:
            content = file.read()
            title = get_title(content)
            # Simplify title for nav: remove "第 X 章：" prefix if too long
            short_title = re.sub(r'^第 \d+ 章：', '', title).split('——')[0].strip()
            
        html_filename = clean_filename(f)
        nav_html += f'<li class="nav-item"><a href="{html_filename}" class="nav-link">{short_title}</a></li>\n'
    return nav_html

def convert_admonitions(html):
    """Convert blockquotes that start with [!NOTE] etc to styled divs if needed, 
    but basic blockquote styling in CSS handles it well enough for now.
    We can enhance this to simple replacements."""
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
        
        # Convert MD to HTML
        # extensions=['tables'] is crucial for the tables we used
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

    # Create Index page (copy of lesson_01 or a custom landing page)
    # Let's make index.html a copy of lesson_01 for now, or a simple welcome page
    # Actually, let's create a dedicated index.md content for the landing.
    landing_content = """
# 和聲的引力：從五度圈到音樂創作的完整指南

歡迎來到這套專為自學者設計的音樂理論課程。

## 課程特色
*   **視覺化學習**：拒絕死背，用幾何與物理理解音樂。
*   **實戰導向**：從古典 Passacaglia 到爵士 Autumn Leaves，每章都有經典範例。
*   **動手實作**：包含鍵盤練習，讓理論轉化為肌肉記憶。

## 開始學習
請點擊左側導覽列的 **[聲音的物理學](lesson_01.html)** 開始第一堂課。
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
