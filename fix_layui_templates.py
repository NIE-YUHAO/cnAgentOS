import os
import re

def fix_template(filepath):
    """修复单个模板文件中的 Layui 模板语法"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 先移除之前的转义，恢复原始状态
    content = content.replace('{{ "{{', '{{')
    content = content.replace('}}" }}', '}}')
    content = content.replace('}}"}}', '}}')
    content = content.replace('{{ "{{#" }}', '{{#')
    content = content.replace('{{% raw %}}', '')
    content = content.replace('{{% endraw %}}', '')
    content = content.replace(' {% raw %}', '')
    content = content.replace('{% endraw %}', '')
    
    # 找到所有 <script type="text/html"> 标签
    script_pattern = r'<script type="text/html"([^>]*)>(.*?)</script>'
    
    def escape_layui(match):
        attrs = match.group(1)
        script_content = match.group(2)
        # 使用 HTML 实体转义 {{ 和 }}
        script_content = script_content.replace('{{', '&#123;&#123;')
        script_content = script_content.replace('}}', '&#125;&#125;')
        return f'<script type="text/html"{attrs}>{script_content}</script>'
    
    content = re.sub(script_pattern, escape_layui, content, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Fixed: {os.path.basename(filepath)}')

# 处理所有模板文件
template_dir = 'app/templates/admin'
for filename in os.listdir(template_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(template_dir, filename)
        fix_template(filepath)

print('\nDone!')