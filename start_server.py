import subprocess
import sys

result = subprocess.run([sys.executable, 'app.py'], capture_output=True, text=True, encoding='utf-8', cwd='c:\\Users\\L\\Desktop\\ShiXun\\day4\\cnAgentOS')
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)