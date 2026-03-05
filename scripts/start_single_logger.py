"""
Start standalone logger - ensures only one instance runs
"""

import os
import sys
import psutil
from datetime import datetime

def check_existing_logger():
    """Check if standalone_logger.py is already running"""
    current_pid = os.getpid()
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = proc.info['cmdline']
                if cmdline and 'standalone_logger.py' in ' '.join(cmdline):
                    if proc.info['pid'] != current_pid:
                        return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    return None

def main():
    print("="*70)
    print("STARTING STANDALONE LOGGER")
    print("="*70)
    
    # Check for existing instance
    existing_pid = check_existing_logger()
    
    if existing_pid:
        print(f"\n⚠️  Logger already running (PID: {existing_pid})")
        print("\nOptions:")
        print("1. Stop existing logger and start new one")
        print("2. Keep existing logger running")
        print("3. Exit")
        
        choice = input("\nEnter choice (1/2/3): ").strip()
        
        if choice == '1':
            try:
                proc = psutil.Process(existing_pid)
                proc.terminate()
                proc.wait(timeout=5)
                print(f"✅ Stopped existing logger (PID: {existing_pid})")
            except Exception as e:
                print(f"❌ Could not stop existing logger: {e}")
                return
        elif choice == '2':
            print("✅ Keeping existing logger running")
            return
        else:
            print("Exiting...")
            return
    
    # Start logger
    print("\n✅ Starting logger...")
    print("   Press Ctrl+C to stop\n")
    
    # Import and run
    from standalone_logger import main as logger_main
    logger_main()

if __name__ == "__main__":
    main()
