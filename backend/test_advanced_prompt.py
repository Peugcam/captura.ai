"""
Test Advanced Prompt vs Old Prompt
Compare detection capabilities with real frames
"""
import sys
import os
import base64
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from src.multi_api_client import MultiAPIClient

# Load prompts
def load_old_prompt():
    """Old GTA prompt (inline in processor)"""
    return """Analyze these GTA V gameplay screenshots for KILL NOTIFICATIONS.

🎯 PRIMARY FOCUS: KILL FEED in TOP-RIGHT CORNER

WHAT TO LOOK FOR:
1. **SKULL ICON** - The most important indicator of a kill!
2. **WEAPON ICONS** - Gun/knife/explosion icons between names
3. **KILL TEXT** - Common verbs: "killed", "shot", "sniped"
4. **PLAYER NAMES** - Text on both sides of the icon/text

RETURN JSON FORMAT:
{
  "description": "what you see in the kill feed",
  "has_combat": true/false,
  "kills": [
    {
      "killer": "exact killer name",
      "killer_team": "Unknown",
      "victim": "exact victim name",
      "victim_team": "Unknown",
      "distance": "weapon/method"
    }
  ]
}"""

def load_advanced_prompt():
    """Advanced GTA prompt from file"""
    try:
        with open('prompts/gta_advanced.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("ERROR: prompts/gta_advanced.txt not found!")
        sys.exit(1)

def load_image_as_base64(image_path):
    """Load image and convert to base64"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def test_prompt(client, prompt_name, prompt_text, image_base64):
    """Test a prompt with an image"""
    print(f"\n{'='*80}")
    print(f"TESTING: {prompt_name}")
    print(f"{'='*80}\n")
    
    print(f"Prompt length: {len(prompt_text)} characters")
    print(f"Sending request to GPT-4o Vision...")
    
    try:
        response = client.vision_chat_multiple(
            model=config.VISION_MODEL,
            prompt=prompt_text,
            images_base64=[image_base64],
            temperature=0,
            max_tokens=2000
        )
        
        if not response['success']:
            print(f"ERROR: {response.get('error')}")
            return None
        
        content = response['content']
        
        # Extract JSON
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end > start:
            json_str = content[start:end]
            data = json.loads(json_str)
            
            print("\nRESULT:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Summary
            print(f"\nSUMMARY:")
            print(f"  Has Combat: {data.get('has_combat', False)}")
            
            if 'events' in data:
                print(f"  Events Detected: {len(data.get('events', []))}")
                for i, event in enumerate(data.get('events', []), 1):
                    print(f"    {i}. {event.get('event_type', 'unknown')}: {event.get('actor', '?')} -> {event.get('target', '?')}")
                    if 'actor_team' in event and event['actor_team'] != 'Unknown':
                        print(f"       Teams: {event.get('actor_team')} vs {event.get('target_team')}")
            elif 'kills' in data:
                print(f"  Kills Detected: {len(data.get('kills', []))}")
                for i, kill in enumerate(data.get('kills', []), 1):
                    print(f"    {i}. {kill.get('killer', '?')} -> {kill.get('victim', '?')} ({kill.get('distance', '?')})")
            
            if 'teams_detected' in data:
                print(f"  Teams Found: {len(data.get('teams_detected', []))}")
                for team in data.get('teams_detected', []):
                    print(f"    - {team.get('team_identifier')}: {', '.join(team.get('players', []))}")
            
            if 'kill_feed_location' in data:
                print(f"  Kill Feed Location: {data.get('kill_feed_location')}")
            
            return data
        else:
            print("ERROR: No JSON found in response")
            print(f"Raw response: {content[:500]}")
            return None
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_advanced_prompt.py <image_path>")
        print("\nExample:")
        print("  python test_advanced_prompt.py test_frames/frame_0001.jpg")
        print("  python test_advanced_prompt.py test_frames/mock_kill_feed.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"ERROR: Image not found: {image_path}")
        sys.exit(1)
    
    print(f"\nLoading image: {image_path}")
    image_base64 = load_image_as_base64(image_path)
    print(f"Image loaded: {len(image_base64)} bytes (base64)")
    
    # Initialize API client
    print(f"\nInitializing API client...")
    client = MultiAPIClient(config.API_KEYS)
    
    # Load prompts
    old_prompt = load_old_prompt()
    advanced_prompt = load_advanced_prompt()
    
    # Test old prompt
    old_result = test_prompt(client, "OLD PROMPT (Top-Right Focus)", old_prompt, image_base64)
    
    # Test advanced prompt
    advanced_result = test_prompt(client, "ADVANCED PROMPT (Full-Screen Pattern Recognition)", advanced_prompt, image_base64)
    
    # Comparison
    print(f"\n{'='*80}")
    print("COMPARISON")
    print(f"{'='*80}\n")
    
    if old_result and advanced_result:
        old_events = len(old_result.get('kills', [])) + len(old_result.get('events', []))
        adv_events = len(advanced_result.get('kills', [])) + len(advanced_result.get('events', []))
        
        print(f"Events Detected:")
        print(f"  Old Prompt: {old_events}")
        print(f"  Advanced Prompt: {adv_events}")
        
        if 'teams_detected' in advanced_result:
            print(f"\nTeam Detection:")
            print(f"  Old Prompt: Not supported")
            print(f"  Advanced Prompt: {len(advanced_result['teams_detected'])} teams found")
        
        if 'kill_feed_location' in advanced_result:
            print(f"\nKill Feed Location:")
            print(f"  Old Prompt: Assumes top-right")
            print(f"  Advanced Prompt: Detected at {advanced_result['kill_feed_location']}")
        
        print(f"\nRECOMMENDATION:")
        if adv_events > old_events:
            print(f"  -> Advanced prompt detected MORE events ({adv_events} vs {old_events})")
        elif adv_events == old_events:
            print(f"  -> Both prompts detected same number of events")
            if 'teams_detected' in advanced_result and advanced_result['teams_detected']:
                print(f"  -> But advanced prompt also detected teams!")
        else:
            print(f"  -> Old prompt detected more (might be hallucinating)")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
