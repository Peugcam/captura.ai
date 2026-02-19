import re

with open('dashboard-strategist.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix WebSocket URL
old_pattern = r"const wsUrl = `\$\{protocol\}//\$\{window\.location\.hostname\}:3000/events`;"
new_code = """const hostname = window.location.hostname || 'localhost';
            const wsUrl = `${protocol}//${hostname}:3000/events`;
            
            console.log('🔌 Conectando ao WebSocket:', wsUrl);"""

content = re.sub(old_pattern, new_code, content)

with open('dashboard-strategist.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ WebSocket URL corrigido!")
