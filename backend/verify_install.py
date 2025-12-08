import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print("sys.path:")
for p in sys.path:
    print(f"  - {p}")

try:
    import langchain_google_genai
    print(f"SUCCESS: langchain_google_genai imported from {langchain_google_genai.__file__}")
except ImportError as e:
    print(f"ERROR: {e}")
