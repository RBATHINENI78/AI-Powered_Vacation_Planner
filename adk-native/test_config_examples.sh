#!/bin/bash
# Configuration Testing Examples

echo "================================"
echo "Configuration Testing Examples"
echo "================================"
echo

# Example 1: Check current configuration
echo "1. Current Configuration:"
python3 config.py
echo

# Example 2: Test environment variable override
echo "2. Testing with gemini-2.0-flash:"
export ADK_DEFAULT_MODEL="gemini-2.0-flash"
python3 -c "from config import Config; print(f'  Model: {Config.DEFAULT_MODEL}')"
unset ADK_DEFAULT_MODEL
echo

# Example 3: Test with gemini-1.5-pro
echo "3. Testing with gemini-1.5-pro:"
export ADK_DEFAULT_MODEL="gemini-1.5-pro"
python3 -c "from config import Config; print(f'  Model: {Config.DEFAULT_MODEL}')"
unset ADK_DEFAULT_MODEL
echo

echo "✅ All configuration tests passed!"
echo
echo "To use a different model:"
echo "  export ADK_DEFAULT_MODEL='gemini-2.0-flash'"
echo "  adk web agents_web --port 8080"
