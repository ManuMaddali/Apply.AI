#!/usr/bin/env python3
"""
Python Version Compatibility Checker for AI Resume Tailoring App
"""

import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print(f"🐍 Python Version Check")
    print(f"   Current version: {version_str}")
    print(f"   Platform: {platform.system()}")
    
    # Check compatibility
    if version.major != 3:
        print("❌ ERROR: Python 3 is required")
        return False
    
    if version.minor < 8:
        print("❌ ERROR: Python 3.8+ is required")
        print("   Please upgrade your Python installation")
        return False
    
    if version.minor >= 13:
        print("⚠️  WARNING: Python 3.13+ detected")
        print("   Most ML/AI libraries don't support Python 3.13 yet")
        print("   Recommended: Python 3.8-3.12")
        print("   You may encounter package installation issues")
        return "warning"
    
    print("✅ Python version is compatible")
    return True

def check_pip():
    """Check if pip is available and working"""
    try:
        import pip
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pip is working: {result.stdout.strip()}")
            return True
        else:
            print("❌ pip is not working properly")
            return False
    except ImportError:
        print("❌ pip is not installed")
        return False

def check_virtual_env():
    """Check if we're in a virtual environment"""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print(f"✅ Running in virtual environment: {sys.prefix}")
    else:
        print("⚠️  Not in a virtual environment")
        print("   Recommended to use virtual environment for the project")
    
    return in_venv

def suggest_fixes():
    """Suggest fixes based on detected issues"""
    version = sys.version_info
    
    print("\n🔧 RECOMMENDED ACTIONS:")
    
    if version.minor >= 13:
        print("\n1. INSTALL COMPATIBLE PYTHON VERSION:")
        if platform.system() == "Darwin":  # macOS
            print("   # Using Homebrew:")
            print("   brew install python@3.11")
            print("   # Or:")
            print("   brew install python@3.12")
            print("\n   # Then use specific version:")
            print("   python3.11 -m venv resume_env")
            print("   source resume_env/bin/activate")
        elif platform.system() == "Linux":
            print("   # Ubuntu/Debian:")
            print("   sudo apt update")
            print("   sudo apt install python3.11 python3.11-venv")
            print("\n   # Then use specific version:")
            print("   python3.11 -m venv resume_env")
            print("   source resume_env/bin/activate")
        else:  # Windows
            print("   # Download Python 3.11 or 3.12 from python.org")
            print("   # Or use pyenv-win:")
            print("   pyenv install 3.11.6")
            print("   pyenv local 3.11.6")
    
    print("\n2. CREATE VIRTUAL ENVIRONMENT:")
    print("   python3 -m venv resume_env")
    if platform.system() == "Windows":
        print("   resume_env\\Scripts\\activate")
    else:
        print("   source resume_env/bin/activate")
    
    print("\n3. UPGRADE PIP AND SETUPTOOLS:")
    print("   pip install --upgrade pip setuptools wheel")
    
    print("\n4. RUN SETUP:")
    print("   ./setup.sh")

def main():
    """Main compatibility check"""
    print("=" * 60)
    print("🚀 AI Resume Tailoring App - Python Compatibility Check")
    print("=" * 60)
    
    # Check Python version
    python_ok = check_python_version()
    print()
    
    # Check pip
    pip_ok = check_pip()
    print()
    
    # Check virtual environment
    venv_ok = check_virtual_env()
    print()
    
    # Overall assessment
    if python_ok is True and pip_ok and venv_ok:
        print("🎉 EVERYTHING LOOKS GOOD!")
        print("   You can proceed with: ./setup.sh")
    elif python_ok == "warning":
        print("⚠️  PROCEED WITH CAUTION")
        print("   Python 3.13 may cause package installation issues")
        print("   Consider using Python 3.11 or 3.12 for best compatibility")
    else:
        print("🔧 ISSUES DETECTED - SEE RECOMMENDATIONS BELOW")
        suggest_fixes()

if __name__ == "__main__":
    main() 