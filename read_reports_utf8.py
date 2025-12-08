import pdfplumber
import os

reports_dir = r"c:\Users\sshaikh10\Desktop\newProjectNew\Reports"
output_file = r"c:\Users\sshaikh10\Desktop\newProjectNew\reports_clean.txt"
files = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]

with open(output_file, 'w', encoding='utf-8') as out:
    for f in files:
        out.write(f"\n\n--- START OF {f} ---\n")
        path = os.path.join(reports_dir, f)
        try:
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        out.write(text)
                        out.write("\n")
        except Exception as e:
            out.write(f"Error reading {f}: {e}\n")
        out.write(f"--- END OF {f} ---\n")

print("Done.")
