"""Test if there are any errors in the logging process"""
import sys
import io
from contextlib import redirect_stderr, redirect_stdout

print("Testing logger components...")
print("="*60)

# Test 1: Import modules
try:
    from standalone_logger import generate_and_log_prediction, is_market_open
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test 2: Check market status
try:
    market_open = is_market_open()
    print(f"✅ Market check: {'OPEN' if market_open else 'CLOSED'}")
except Exception as e:
    print(f"❌ Market check error: {e}")

# Test 3: Try to generate one prediction
print("\nTesting prediction generation...")
try:
    # Capture any warnings/errors
    f = io.StringIO()
    with redirect_stderr(f):
        generate_and_log_prediction()
    
    errors = f.getvalue()
    if errors:
        print("⚠️  Warnings/Errors during generation:")
        print(errors)
    else:
        print("✅ Prediction generated successfully")
        
except Exception as e:
    print(f"❌ Generation error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("If you see errors above, they might be appearing in PowerShell")
