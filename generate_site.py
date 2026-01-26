import os
import markdown
import re

# Configuration
SOURCE_DIR = "."
OUTPUT_DIR = "docs"
TITLE = "和聲的引力"

# CSS Styles (Embedded for simplicity)
STYLES = """
:root {
    --bg-color: #fdfdfd;
    --text-color: #333;
    --sidebar-bg: #f7f7f7;
    --sidebar-width: 280px;
    --accent-color: #2c3e50;
    --link-color: #3498db;
    --font-heading: "Playfair Display", Georgia, serif;
    --font-body: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bg-color: #1a1a1a;
        --text-color: #e0e0e0;
        --sidebar-bg: #252525;
        --accent-color: #ecf0f1;
        --link-color: #5dade2;
    }
}

body {
    margin: 0;
    font-family: var(--font-body);
    background: var(--bg-color);
    color: var(--text-color);
    display: flex;
    min-height: 100vh;
}

/* Sidebar */
.sidebar {
    width: var(--sidebar-width);
    background: var(--sidebar-bg);
    border-right: 1px solid rgba(0,0,0,0.1);
    position: fixed;
    height: 100vh;
    overflow-y: auto;
    padding: 2rem 1.5rem;
    box-sizing: border-box;
    transition: transform 0.3s ease;
}

.sidebar h1 {
    font-family: var(--font-heading);
    font-size: 1.5rem;
    margin-bottom: 2rem;
    color: var(--accent-color);
}

.nav-links {
    list-style: none;
    padding: 0;
}

.nav-links li {
    margin-bottom: 0.8rem;
}

.nav-links a {
    text-decoration: none;
    color: var(--text-color);
    font-size: 0.95rem;
    opacity: 0.8;
    transition: all 0.2s;
    display: block;
    padding: 0.3rem 0;
}

.nav-links a:hover, .nav-links a.active {
    opacity: 1;
    color: var(--link-color);
    font-weight: 600;
    transform: translateX(5px);
}

/* Main Content */
.main-content {
    margin-left: var(--sidebar-width);
    flex: 1;
    padding: 4rem 10%;
    max-width: 800px;
}

.markdown-body {
    line-height: 1.8;
    font-size: 1.1rem;
}

.markdown-body h1, .markdown-body h2, .markdown-body h3 {
    font-family: var(--font-heading);
    color: var(--accent-color);
    margin-top: 2rem;
}

.markdown-body h1 { font-size: 2.5rem; border-bottom: 1px solid rgba(0,0,0,0.1); padding-bottom: 0.5rem; }
.markdown-body h2 { font-size: 1.8rem; }
.markdown-body blockquote {
    border-left: 4px solid var(--link-color);
    margin: 1.5rem 0;
    padding-left: 1rem;
    background: rgba(52, 152, 219, 0.1);
    border-radius: 0 4px 4px 0;
    padding: 1rem;
}

.markdown-body code {
    background: rgba(0,0,0,0.05);
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.9em;
}

.markdown-body pre code {
    background: transparent;
    padding: 0;
}

.markdown-body pre {
    background: #2d3436;
    color: #dfe6e9;
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
}

.nav-buttons {
    margin-top: 4rem;
    display: flex;
    justify-content: space-between;
    padding-top: 2rem;
    border-top: 1px solid rgba(0,0,0,0.1);
}

.btn {
    display: inline-block;
    padding: 0.6rem 1.2rem;
    border-radius: 6px;
    background: var(--sidebar-bg);
    color: var(--text-color);
    text-decoration: none;
    transition: background 0.2s;
    border: 1px solid rgba(0,0,0,0.1);
}

.btn:hover {
    background: rgba(0,0,0,0.05);
    color: var(--link-color);
}

/* Mobile */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        z-index: 1000;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2);
    }
    .sidebar.open {
        transform: translateX(0);
    }
    .main-content {
        margin-left: 0;
        padding: 2rem 1.5rem;
    }
    .menu-toggle {
        display: block;
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 1001;
        background: var(--bg-color);
        border: 1px solid rgba(0,0,0,0.1);
        padding: 0.5rem;
        border-radius: 4px;
        cursor: pointer;
    }
}
@media (min-width: 769px) {
    .menu-toggle { display: none; }
}
"""

TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {site_title}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>
        {styles}
    </style>
</head>
<body>
    <button class="menu-toggle" onclick="document.querySelector('.sidebar').classList.toggle('open')">☰</button>
    <nav class="sidebar">
        <h1><a href="index.html" style="color: inherit; text-decoration: none;">{site_title}</a></h1>
        <ul class="nav-links">
            {nav_items}
        </ul>
    </nav>
    <main class="main-content">
        <article class="markdown-body">
            {content}
        </article>
        <div class="nav-buttons">
            {prev_button}
            {next_button}
        </div>
    </main>
</body>
</html>
"""

def generate():
    # 1. Get List of Lessons
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.startswith("lesson_") and f.endswith(".md")])
    
    lessons = []
    for f in files:
        # Extract number for sorting just in case
        match = re.search(r'lesson_(\d+)', f)
        if match:
            num = int(match.group(1))
            # Read Title
            with open(os.path.join(SOURCE_DIR, f), 'r', encoding='utf-8') as file:
                content = file.read()
                # Find first h1
                h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = h1_match.group(1) if h1_match else f
                title = title.replace("第 ", "").replace("章：", ". ") # Clean up a bit
            lessons.append({'filename': f, 'num': num, 'title': title, 'raw_content': content})
    
    lessons.sort(key=lambda x: x['num'])
    
    # 2. Build Nav
    nav_html = ""
    for l in lessons:
        link = l['filename'].replace('.md', '.html')
        nav_html += f'<li><a href="{link}" id="nav-{l["num"]}">{l["title"]}</a></li>'
    
    # 3. Process Each Lesson
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'nl2br'])
    
    for i, l in enumerate(lessons):
        html_content = md.convert(l['raw_content'])
        
        # Determine Prev/Next
        prev_btn = ""
        next_btn = ""
        
        if i > 0:
            prev_l = lessons[i-1]
            link = prev_l['filename'].replace('.md', '.html')
            prev_btn = f'<a href="{link}" class="btn">← 上一章</a>'
        
        if i < len(lessons) - 1:
            next_l = lessons[i+1]
            link = next_l['filename'].replace('.md', '.html')
            next_btn = f'<a href="{link}" class="btn">下一章 →</a>'
            
        full_html = TEMPLATE.format(
            title=l['title'],
            site_title=TITLE,
            styles=STYLES,
            nav_items=nav_html.replace(f'href="{l["filename"].replace(".md", ".html")}"', f'class="active" href="{l["filename"].replace(".md", ".html")}"'),
            content=html_content,
            prev_button=prev_btn,
            next_button=next_btn
        )
        
        out_path = os.path.join(OUTPUT_DIR, l['filename'].replace('.md', '.html'))
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
            
    # 4. Generate Index (Redirect or Cover)
    # Let's make index.html a cover page that introduces the course and has the ToC
    index_content = """# 音樂理論自學教材：和聲的引力

歡迎來到這套專為自學設計的音樂理論課程。
我們將從物理聲學出發，一路探索到爵士和聲的高級色彩。

## 課程目錄
"""
    # Append list of lessons to index content
    for l in lessons:
        link = l['filename'].replace('.md', '.html')
        index_content += f"- [{l['title']}]({link})\n"
        
    index_html_content = md.convert(index_content)
    # Start button
    start_btn = f'<a href="lesson_01.html" class="btn" style="background: var(--accent-color); color: white;">開始第一章 →</a>'
    
    full_index = TEMPLATE.format(
        title="首頁",
        site_title=TITLE,
        styles=STYLES,
        nav_items=nav_html,
        content=index_html_content,
        prev_button="",
        next_button=start_btn
    )
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(full_index)

    print("Generation Complete.")

if __name__ == "__main__":
    generate()
