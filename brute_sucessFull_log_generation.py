import paramiko
import time

TARGET_IP = '127.0.0.6'
USERNAME = 'ij_baig'
PASSWORD = '00@123qwery'

# Loop Configuration
NUM_LOGINS = 25       # How many successful logins to generate
DELAY_SECONDS = 1     # How long to wait between each login attempt

def trigger_successful_login(attempt_number):
    try:
        # Initialize the SSH client
        client = paramiko.SSHClient()
        # Automatically add the host key
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print(f"[{attempt_number}/{NUM_LOGINS}] Attempting login for {USERNAME}...")
        
        # Connect to the server (This triggers the 'Accepted password' log)
        client.connect(TARGET_IP, username=USERNAME, password=PASSWORD)
        print("    [+] Login successful! Log generated.")
        
        # Close the connection immediately (This triggers the 'session closed' log)
        client.close()
        print("    [*] Connection closed. No shell spawned.")
        
    except paramiko.AuthenticationException:
        print("    [-] Authentication failed. Check your password.")
    except Exception as e:
        print(f"    [-] Error: {e}")

if __name__ == "__main__":
    print(f"[*] Starting SSH login simulation loop against {TARGET_IP}")
    print(f"[*] Press Ctrl+C at any time to stop.\n")
    
    for i in range(1, NUM_LOGINS + 1):
        trigger_successful_login(i)
        
        # Wait before the next attempt, unless it's the very last iteration
        if i < NUM_LOGINS:
            print(f"    [*] Waiting {DELAY_SECONDS} seconds before next attempt...\n")
            time.sleep(DELAY_SECONDS)
            
    print("\n[+] Simulation loop complete!")
