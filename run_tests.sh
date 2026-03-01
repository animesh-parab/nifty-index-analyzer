#!/bin/bash

echo "=================================="
echo "Nifty AI Predictor - Quick Test"
echo "=================================="
echo ""

# Test 1: Check Python
echo "1. Checking Python..."
python --version
if [ $? -ne 0 ]; then
    echo "   ✗ Python not found. Please install Python 3.8+"
    exit 1
fi
echo "   ✓ Python OK"
echo ""

# Test 2: Check dependencies
echo "2. Checking dependencies..."
pip list | grep -q streamlit
if [ $? -ne 0 ]; then
    echo "   ⚠ Dependencies not installed"
    echo "   Installing now..."
    pip install -r requirements.txt
fi
echo "   ✓ Dependencies OK"
echo ""

# Test 3: Test NSE Fetcher
echo "3. Testing NSE API..."
python nse_fetcher_enhanced.py
echo ""

# Test 4: Check Groq API key
echo "4. Checking Groq API key..."
if [ -f .env ]; then
    if grep -q "GROQ_API_KEY=your_groq_api_key_here" .env; then
        echo "   ⚠ Groq API key not set"
        echo "   Edit .env file and add your key from https://console.groq.com"
    else
        echo "   ✓ Groq API key configured"
    fi
else
    echo "   ⚠ .env file not found"
    echo "   Run: cp env.example .env"
    echo "   Then edit .env and add your Groq API key"
fi
echo ""

echo "=================================="
echo "Setup complete!"
echo "=================================="
echo ""
echo "To start the dashboard:"
echo "  streamlit run app.py"
echo ""
echo "To test with sample data:"
echo "  python create_sample_data.py"
echo "  streamlit run app_dry_run.py"
echo ""
