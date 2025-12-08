import os

# Define the root of the project (assuming script is run from project root)
PROJECT_ROOT = r"c:\Users\sshaikh10\Desktop\newProjectNew"

# List of files to include
FILES_TO_INCLUDE = [
    r"backend\app\models.py",
    r"backend\app\routes.py",
    r"backend\app\services.py",
    r"backend\ingest_data.py",
    r"backend\evaluate_system.py",
    r"frontend\src\pages\Dashboard.jsx",
    r"frontend\src\components\InsightCard.jsx"
]

OUTPUT_FILE = "appendix_code_dump.txt"

def is_todo_or_commented_code(line):
    stripped = line.strip()
    # Remove TODOs
    if stripped.startswith("# TODO") or stripped.startswith("// TODO"):
        return True
    return False

def main():
    output_path = os.path.join(PROJECT_ROOT, OUTPUT_FILE)
    
    with open(output_path, "w", encoding="utf-8") as outfile:
        for rel_path in FILES_TO_INCLUDE:
            abs_path = os.path.join(PROJECT_ROOT, rel_path)
            
            # Header
            outfile.write(f"### FILE: {rel_path.replace(os.sep, '/')} ###\n")
            
            if os.path.exists(abs_path):
                try:
                    with open(abs_path, "r", encoding="utf-8") as infile:
                        lines = infile.readlines()
                        for line in lines:
                            # Basic filtering of TODOs
                            if not is_todo_or_commented_code(line):
                                outfile.write(line)
                except Exception as e:
                    outfile.write(f"Error reading file: {str(e)}\n")
            else:
                outfile.write("FILE NOT FOUND\n")
            
            # Separator
            outfile.write("\n\n" + "="*50 + "\n\n")
            
    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    main()
