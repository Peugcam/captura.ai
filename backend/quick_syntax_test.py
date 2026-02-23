#!/usr/bin/env python3
"""Quick syntax check - just try to compile the files"""
import py_compile
import sys

files_to_check = [
    'src/pixel_filter.py',
    'config.py',
    'processor.py'
]

print("Checking Python syntax...")
errors = []

for file in files_to_check:
    try:
        py_compile.compile(file, doraise=True)
        print(f"✅ {file}")
    except py_compile.PyCompileError as e:
        print(f"❌ {file}")
        print(f"   Error: {e}")
        errors.append(file)

if errors:
    print(f"\n❌ {len(errors)} file(s) have syntax errors")
    sys.exit(1)
else:
    print(f"\n✅ All files have valid Python syntax")
    sys.exit(0)
