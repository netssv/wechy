#!/bin/bash

# Enhanced Web Audit Tool - Streamlit Setup Script
# Author: netss
# Description: Automated setup for Streamlit version

echo "🔍 Enhanced Web Audit Tool - Streamlit Setup"
echo "============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Create virtual environment (optional but recommended)
read -p "🤔 Do you want to create a virtual environment? (y/n): " create_venv

if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Install requirements
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Check if installation was successful
if [ $? -eq 0 ]; then
    echo "✅ All dependencies installed successfully!"
else
    echo "❌ Error installing dependencies. Please check the output above."
    exit 1
fi

# Test Streamlit installation
echo "🧪 Testing Streamlit installation..."
python3 -c "import streamlit; print('✅ Streamlit:', streamlit.__version__)"

# Create run script
cat > run_audit.sh << 'EOF'
#!/bin/bash
# Enhanced Web Audit Tool - Run Script

echo "🚀 Starting Enhanced Web Audit Tool..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Start Streamlit app
streamlit run streamlit_web_audit.py
EOF

chmod +x run_audit.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Run the application:"
echo "   ./run_audit.sh"
echo ""
echo "2. Or run manually:"
if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "   source venv/bin/activate"
fi
echo "   streamlit run streamlit_web_audit.py"
echo ""
echo "3. Open your browser at: http://localhost:8501"
echo ""
echo "🌐 To deploy on Streamlit Cloud:"
echo "1. Push this code to GitHub"
echo "2. Go to share.streamlit.io"
echo "3. Connect your repository"
echo "4. Deploy streamlit_web_audit.py"
echo ""
echo "📚 Read README_STREAMLIT.md for more information"
