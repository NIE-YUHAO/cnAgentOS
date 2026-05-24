import os
import re

template_dir = 'app/templates/admin'

for filename in os.listdir(template_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(template_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复 {% for %} 循环中的变量访问
        # 找到 {% for var in list %} ... {% end %} 块
        for_pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*\%\}(.*?)\{%\s*end\s*\%\}'
        
        def fix_for_block(match):
            var_name = match.group(1)
            list_name = match.group(2)
            block_content = match.group(3)
            
            # 修复块内的 var_name.attr 为 var_name['attr']
            # 使用正则匹配 var_name.attr 的模式
            block_content = re.sub(
                rf'{re.escape(var_name)}\.(\w+)',
                rf"{var_name}['\1']",
                block_content
            )
            
            return '{% for ' + var_name + ' in ' + list_name + ' %}' + block_content + '{% end %}'
        
        content = re.sub(for_pattern, fix_for_block, content, flags=re.DOTALL)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Fixed: {filename}')

print('\nDone!')