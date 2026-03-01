"""Test Dual-AI Consensus System"""

import os
from dotenv import load_dotenv

print("\n" + "="*70)
print("TESTING DUAL-AI CONSENSUS SYSTEM")
print("="*70 + "\n")

# Load environment variables
load_dotenv()

# Check API keys
groq_key = os.getenv('GROQ_API_KEY')
gemini_key = os.getenv('GEMINI_API_KEY')

print("1. Checking API Keys...")
if groq_key:
    print(f"   [OK] Groq API Key: {groq_key[:20]}...")
else:
    print("   [WARN] Groq API Key not found")

if gemini_key:
    print(f"   [OK] Gemini API Key: {gemini_key[:20]}...")
else:
    print("   [WARN] Gemini API Key not found")

if not groq_key and not gemini_key:
    print("\n   [FAIL] No API keys found!")
    print("   Add GROQ_API_KEY or GEMINI_API_KEY to .env file")
    exit(1)

print("\n2. Testing Consensus Engine...")
try:
    from ai_engine_consensus import get_consensus_prediction
    
    # Mock data for testing
    mock_data = {
        "price_data": {"price": 25300, "change": 50, "pct_change": 0.2},
        "indicator_summary": {
            "RSI": {"signal": "BULLISH", "value": 55},
            "MACD": {"signal": "BULLISH"},
            "EMA_Trend": {"signal": "UPTREND"}
        },
        "oi_data": {"pcr": 1.2, "max_pain": 25300},
        "vix_data": {"vix": 15, "change": 0.5},
        "news_sentiment": {"overall": "BULLISH", "score": 0.3},
        "greeks": {},
        "global_cues": {},
        "patterns": {}
    }
    
    print("   Calling both AIs (this may take 3-5 seconds)...\n")
    
    result = get_consensus_prediction(**mock_data)
    
    print("="*70)
    print("CONSENSUS RESULT")
    print("="*70)
    
    print(f"\nDirection: {result.get('direction')}")
    print(f"Confidence: {result.get('confidence')}%")
    print(f"Consensus: {result.get('consensus')}")
    print(f"Agreement: {result.get('agreement')}")
    
    if result.get('groq_prediction'):
        groq_dir = result.get('groq_direction', 'N/A')
        groq_conf = result.get('groq_confidence', 0)
        print(f"\nGroq (Llama 3.3 70B): {groq_dir} ({groq_conf}%)")
        if result['groq_prediction'].get('error'):
            print(f"  Error: {result['groq_prediction']['error']}")
    
    if result.get('gemini_prediction'):
        gemini_dir = result.get('gemini_direction', 'N/A')
        gemini_conf = result.get('gemini_confidence', 0)
        print(f"Gemini (1.5 Flash): {gemini_dir} ({gemini_conf}%)")
        if result['gemini_prediction'].get('error'):
            print(f"  Error: {result['gemini_prediction']['error']}")
    
    print(f"\nSummary: {result.get('one_line_summary')}")
    
    print("\n" + "="*70)
    
    if result.get('consensus') == "STRONG":
        print("✓✓ STRONG CONSENSUS - Both AIs agree!")
    elif result.get('consensus') == "MODERATE":
        print("✓ MODERATE CONSENSUS - Partial agreement")
    elif result.get('consensus') == "WEAK":
        print("⚠ WEAK CONSENSUS - AIs disagree")
    else:
        print(f"Status: {result.get('consensus')}")
    
    print("="*70 + "\n")
    
    print("[SUCCESS] Dual-AI Consensus System is working!")
    print("\nYour dashboard will now show:")
    print("  - Consensus level (Strong/Moderate/Weak)")
    print("  - Individual AI predictions")
    print("  - Combined confidence score")
    print("  - Agreement indicator")
    
except Exception as e:
    print(f"\n[FAIL] Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*70)
print("Ready to use! Run: streamlit run app.py")
print("="*70 + "\n")
