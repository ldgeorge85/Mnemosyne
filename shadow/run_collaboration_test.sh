#!/bin/bash

# Shadow AI Collaboration Test Runner
# This script runs the collaboration tests with real OpenAI LLM and embedding endpoints

echo "Shadow AI - Multi-Agent Collaboration Test"
echo "=========================================="
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ Found .env file"
    # Check if it has OPENAI_API_KEY
    if grep -q "OPENAI_API_KEY=" .env && ! grep -q "OPENAI_API_KEY=your-openai-api-key-here" .env; then
        echo "✅ OpenAI API key appears to be configured in .env file"
        echo "🚀 Starting collaboration tests with real LLM and embedding endpoints..."
        echo ""
        
        # Run the collaboration test
        python3 test_collaboration.py
        
        # Check the exit code
        if [ $? -eq 0 ]; then
            echo ""
            echo "🎉 All collaboration tests passed!"
            echo "   Multi-agent collaboration with real endpoints is working correctly."
        else
            echo ""
            echo "❌ Some tests failed. Check the output above for details."
        fi
    else
        echo "❌ OPENAI_API_KEY not configured in .env file"
        echo ""
        echo "Please edit your .env file and set your OpenAI API key:"
        echo "   OPENAI_API_KEY=your-actual-openai-api-key-here"
        echo ""
        exit 1
    fi
else
    echo "❌ No .env file found"
    echo ""
    echo "To run the collaboration tests with real endpoints, you need to:"
    echo "1. Create a .env file:"
    echo "   cp .env.example .env"
    echo ""
    echo "2. Edit .env and set your OpenAI API key:"
    echo "   OPENAI_API_KEY=your-actual-openai-api-key-here"
    echo ""
    echo "3. Then run this script again:"
    echo "   ./run_collaboration_test.sh"
    echo ""
    echo "Alternatively, you can set the environment variable manually:"
    echo "   OPENAI_API_KEY='your-key' python3 test_collaboration.py"
    echo ""
    exit 1
fi
