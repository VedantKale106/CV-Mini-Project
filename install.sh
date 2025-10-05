#!/bin/bash
# install.sh - Smart Surveillance System Installation Script

echo "🔧 Smart Surveillance System Installer"
echo "======================================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o "3\.[0-9]*")
if [[ $? -ne 0 ]]; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Found Python $python_version"

# Create virtual environment (recommended)
echo "📦 Setting up virtual environment..."
python3 -m venv surveillance_env
source surveillance_env/bin/activate

# Install required packages
echo "⬇️  Installing required packages..."
pip install --upgrade pip
pip install opencv-python face-recognition numpy playsound Pillow

# Create directories
echo "📁 Creating required directories..."
mkdir -p faces captures

# Download sample alert sound (optional)
echo "🔊 Creating alert sound..."
python3 -c "
import numpy as np
from scipy.io.wavfile import write
sample_rate = 44100
duration = 2.0
frequency = 1000
t = np.linspace(0, duration, int(sample_rate * duration))
beep = np.sin(2 * np.pi * frequency * t) * 0.3
fade_samples = int(0.1 * sample_rate)
beep[:fade_samples] *= np.linspace(0, 1, fade_samples)  
beep[-fade_samples:] *= np.linspace(1, 0, fade_samples)
write('alert.wav', sample_rate, (beep * 32767).astype(np.int16))
print('Alert sound created successfully!')
" 2>/dev/null || echo "⚠️  Install scipy for custom alert sound: pip install scipy"

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🚀 To run the system:"
echo "   1. Activate virtual environment: source surveillance_env/bin/activate"
echo "   2. Run surveillance system: python3 surveillance.py"
echo ""
echo "⚙️  Don't forget to configure email settings in alert.py"
echo "📖 See README.md for detailed setup instructions"
