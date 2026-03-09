"""
daily_backup_monitor.py
Monitors prediction_log.csv and creates clean daily backup
Run alongside standalone_logger.py
"""

import csv
import os
import time
from datetime import datetime

MAIN_CSV = 'prediction_log.csv'
DAILY_CSV = 'prediction_log_2026_03_09.csv'

print("="*60)
print("DAILY BACKUP MONITOR")
print("="*60)
print(f"Reading from: {MAIN_CSV}")
print(f"Writing to: {DAILY_CSV}")
print("Press Ctrl+C to stop")
print("="*60)

# Track last processed line
last_line_count = 0

# Create daily CSV with header if doesn't exist
if not os.path.exists(DAILY_CSV):
    with open(MAIN_CSV, 'r') as f:
        header = f.readline()
    with open(DAILY_CSV, 'w') as f:
        f.write(header)
    print(f"✓ Created {DAILY_CSV} with header")

try:
    while True:
        # Read all lines from main CSV
        with open(MAIN_CSV, 'r') as f:
            lines = f.readlines()
        
        current_line_count = len(lines)
        
        # If new lines added
        if current_line_count > last_line_count:
            new_lines = lines[last_line_count:]
            
            # Filter for today's date (2026-03-09)
            today_lines = [line for line in new_lines if '2026-03-09' in line]
            
            if today_lines:
                # Append to daily CSV
                with open(DAILY_CSV, 'a') as f:
                    f.writelines(today_lines)
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Copied {len(today_lines)} new rows to daily backup")
            
            last_line_count = current_line_count
        
        # Check every 10 seconds
        time.sleep(10)

except KeyboardInterrupt:
    print("\n\nStopping monitor...")
    print(f"Final backup saved to: {DAILY_CSV}")
