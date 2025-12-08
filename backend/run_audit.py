import json
from app import create_app
from app.audit_utils import run_red_team_audit
from dotenv import load_dotenv

load_dotenv()

app = create_app()

def main():
    print("Starting Security Audit (CLI Mode)...")
    print("-" * 50)
    
    with app.app_context():
        results = run_red_team_audit()
        
        if "error" in results:
            print(f"Error: {results['error']}")
            return

        print(f"Safety Score: {results['safety_score']:.1f}%")
        print(f"Tests Passed: {results['passed']}/{results['total_tests']}")
        print("-" * 50)
        
        print(f"{'Type':<25} | {'Status':<6} | {'Question'}")
        print("-" * 50)
        
        for log in results['audit_log']:
            status_color = "PASS" if log['status'] == "PASS" else "FAIL"
            # Truncate question for display
            q_display = (log['question'][:45] + '..') if len(log['question']) > 45 else log['question']
            print(f"{log['type']:<25} | {status_color:<6} | {q_display}")
            print(f"   -> Response: {log['response'][:100]}...")
                
        print("-" * 50)
        print("Audit Complete.")

if __name__ == "__main__":
    main()
