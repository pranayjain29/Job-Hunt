#!/usr/bin/env python3
"""
Job Hunt 2 - Setup Script
Run: python setup.py
"""

import os
import sys
import subprocess
import shutil

def check_command(cmd, name):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            return True
    except:
        pass
    return False

def main():
    print("\n" + "="*50)
    print("  JOB HUNT 2 - SETUP")
    print("="*50)
    
    has_uv = shutil.which("uv") is not None
    
    if not has_uv:
        print("uv not found! Installing uv for you...")
        if sys.platform == "win32":
            try:
                subprocess.run(["powershell", "-Command", "irm https://astral.sh/uv/get.ps1 | iex"], check=True)
                has_uv = True
                print("uv installed!")
            except:
                print("Failed. Please install uv manually:")
                print("  Windows: powershell -Command \"irm https://astral.sh/uv/get.ps1 | iex\"")
                print("  Mac/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
                return
        else:
            print("Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
            return
    
    print("  uv found!")
    
    # Install dependencies
    print("\n[1/2] Installing dependencies...")
    result = subprocess.run(["uv", "sync"], shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return
    print("  Dependencies installed!")
    
    # Install playwright
    print("\n[2/2] Installing Playwright...")
    result = subprocess.run(["uv", "run", "playwright", "install", "chromium"], shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("  Chromium installed!")
    else:
        print("  Playwright warning (continuing...)")
    
    # Setup .env
    print("\n" + "-"*50)
    if not os.path.exists(".env"):
        shutil.copy(".env.example", ".env")
        print("Created .env from template")
        print("\n" + "="*50)
        print("  NEXT STEPS:")
        print("="*50)
        print("1. Edit .env and add your OPENROUTER_API_KEY")
        print("   Get free key at https://openrouter.ai")
        print("")
        print("2. Run: uv run main.py")
    else:
        print(".env already exists")
        print("\nRun: uv run main.py")
    
    print("\nDone!")

if __name__ == "__main__":
    main()