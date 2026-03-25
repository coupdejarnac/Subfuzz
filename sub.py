import requests
import sys
import concurrent.futures
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)

# Configuration
MAX_THREADS = 5  # Optimal for speed without getting banned
TIMEOUT = 10
OUTPUT_FILE = "results.txt"
INPUT_FILE = "targets.txt"

all_subdomains = set()

def fetch_subdomains(domain):
    """Worker function to hit the API for a single domain."""
    print(f"{Fore.BLUE}[*] Scanning: {Fore.WHITE}{domain}")
    api_url = f"https://api.subdomainfinder.in/?domain={domain}"
    local_subs = []
    
    try:
        response = requests.get(api_url, timeout=TIMEOUT)
        
        if response.status_code == 200:
            json_data = response.json()
            if json_data.get("status") == "success":
                data_list = json_data.get("data", [])
                for item in data_list:
                    sub = item.get("subdomain")
                    if sub:
                        local_subs.append(sub)
                print(f"{Fore.GREEN}[+] {domain}: Found {len(local_subs)} subdomains.")
                return local_subs
            else:
                print(f"{Fore.RED}[-] {domain}: API Message -> {json_data.get('message')}")
        else:
            print(f"{Fore.RED}[-] {domain}: HTTP {response.status_code}")
            
    except Exception as e:
        # Silently catch connection errors to keep the terminal clean
        print(f"{Fore.RED}[!] {domain}: Connection Error.")
    
    return []

def main():
    print(f"{Fore.CYAN}{Style.BRIGHT}=== Multi-Threaded Subdomain Finder ==={Style.RESET_ALL}\n")
    
    # 1. Load Targets
    try:
        with open(INPUT_FILE, 'r') as f:
            domains = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}[!] Error: '{INPUT_FILE}' not found.")
        return

    if not domains:
        print(f"{Fore.YELLOW}[!] No domains found in '{INPUT_FILE}'.")
        return

    # 2. Multi-threaded Execution
    print(f"{Fore.YELLOW}[*] Using {MAX_THREADS} threads. Please wait...\n")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        # Map the function to the list of domains
        results = list(executor.map(fetch_subdomains, domains))

    # 3. Consolidate Results
    for sub_list in results:
        for s in sub_list:
            all_subdomains.add(s)

    # 4. Final Save
    if all_subdomains:
        sorted_subs = sorted(list(all_subdomains))
        with open(OUTPUT_FILE, 'w') as out:
            for sub in sorted_subs:
                out.write(f"{sub}\n")
        
        print(f"\n{Fore.MAGENTA}" + "="*40)
        print(f"{Fore.GREEN}[DONE] Total Unique Subdomains: {len(sorted_subs)}")
        print(f"{Fore.GREEN}[DONE] Saved to: {OUTPUT_FILE}")
        print(f"{Fore.MAGENTA}" + "="*40)
    else:
        print(f"\n{Fore.RED}[!] No results found.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Forced stop by user. Exiting...")
        sys.exit(0)
