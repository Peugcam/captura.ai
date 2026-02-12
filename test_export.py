"""Test Excel export endpoint"""
import requests
import json

BACKEND_URL = "http://localhost:3000"

try:
    print("Testing Excel export endpoint...")
    response = requests.post(f"{BACKEND_URL}/export", json={}, timeout=10)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data.get('success')}")
        print(f"Filename: {data.get('filename')}")
        print(f"Filepath: {data.get('filepath')}")
        print(f"\nExcel file created successfully!")
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
