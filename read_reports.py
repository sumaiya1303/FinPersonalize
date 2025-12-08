import pdfplumber
import os

reports_dir = r"c:\Users\sshaikh10\Desktop\newProjectNew\Reports"
files = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]

for f in files:
    print(f"--- START OF {f} ---")
    path = os.path.join(reports_dir, f)
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                print(page.extract_text())
    except Exception as e:
        print(f"Error reading {f}: {e}")
    print(f"--- END OF {f} ---")
