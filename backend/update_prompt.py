"""Update processor.py to use advanced prompt"""
import re

# Read current processor
with open('processor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the get_prompt_for_game method and replace GTA section
new_gta_prompt = '''        if game_type == "gta":
            # Check if advanced prompt should be used
            if config.USE_ADVANCED_PROMPT:
                try:
                    with open('prompts/gta_advanced.txt', 'r', encoding='utf-8') as f:
                        return f.read()
                except FileNotFoundError:
                    logger.warning("Warning Advanced prompt file not found, using default")
            
            # Default prompt (backwards compatible)
            return """Analyze these GTA V gameplay screenshots for KILL NOTIFICATIONS.'''

# Replace the section
pattern = r'(\s+if game_type == "gta":\s+return """Analyze these GTA V)'
replacement = new_gta_prompt
content = re.sub(pattern, replacement, content, count=1)

# Write back
with open('processor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK processor.py updated to support advanced prompt")
print("OK Set USE_ADVANCED_PROMPT=true in .env to enable")
