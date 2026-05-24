import os

template_dir = 'app/templates/admin'

for filename in os.listdir(template_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 直接替换所有 Layui 模板语法 {{# 和 # }}
        content = content.replace('{{#', '{{ "{{#" }}')
        content = content.replace('# }}', '# "}}" }}')
        content = content.replace('#}}', '#"}}"}}')
        
        # 转义普通的 {{ ... }} 变量（不在 <script> 标签外的）
        # 使用正则来处理
        import re
        # 匹配 {{ 后面不是 { 和不是 # 的内容
        content = re.sub(r'\{\{(\s*[^#][^{}]*)?\}\}', r'{{ "{{\1}}" }}', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed: {filename}')

print('Done!')