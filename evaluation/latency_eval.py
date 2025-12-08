import argparse
import requests
import time
import numpy as np
import sys

def main():
    parser = argparse.ArgumentParser(description='Latency Evaluation')
    parser.add_argument('--url', type=str, default='http://localhost:5000/api/chat', help='API URL to test')
    parser.add_argument('--requests', type=int, default=20, help='Number of requests to send')
    
    args = parser.parse_args()
    
    payload = {'message': 'Can I afford a new car?', 'user_id': 1}
    latencies = []
    
    print(f"Testing API Latency: {args.url}")
    print(f"Sending {args.requests} requests...")
    
    for i in range(args.requests):
        start_time = time.time()
        try:
            response = requests.post(args.url, json=payload)
            response.raise_for_status()
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to {args.url}. Is the server running?")
            sys.exit(1)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            sys.exit(1)
            
        end_time = time.time()
        latency = end_time - start_time
        latencies.append(latency)
        
        # Optional: Print dot to show progress
        print(".", end="", flush=True)
        
    print("\n\n" + "="*40)
    print("LATENCY REPORT")
    print("="*40)
    
    if latencies:
        mean_latency = np.mean(latencies)
        median_latency = np.median(latencies)
        p95_latency = np.percentile(latencies, 95)
        
        print(f"Total Requests:       {len(latencies)}")
        print(f"Average Response Time: {mean_latency:.4f}s")
        print(f"Median Response Time:  {median_latency:.4f}s")
        print(f"P95 Response Time:     {p95_latency:.4f}s")
    else:
        print("No successful requests recorded.")
        
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
