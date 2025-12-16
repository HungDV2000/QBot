#!/usr/bin/env python3
"""
Test script để build một module duy nhất (nhanh hơn khi test)
"""

import sys
import subprocess
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python test_build_single.py <module_name>")
    print("Example: python test_build_single.py hd_order.py")
    sys.exit(1)

module_name = sys.argv[1]

if not Path(module_name).exists():
    print(f"❌ File not found: {module_name}")
    sys.exit(1)

print(f"🔨 Building {module_name}...")

cmd = [
    'pyinstaller',
    '--onefile',
    '--console',
    '--name', module_name.replace('.py', ''),
    '--hidden-import', 'cst',
    '--hidden-import', 'gg_sheet_factory',
    '--hidden-import', 'telegram_factory',
    '--hidden-import', 'binance_utils',
    '--hidden-import', 'utils',
    '--hidden-import', 'google.auth.transport.requests',
    '--hidden-import', 'google.oauth2.credentials',
    '--hidden-import', 'google_auth_oauthlib.flow',
    '--hidden-import', 'googleapiclient.discovery',
    '--hidden-import', 'telegram',
    '--hidden-import', 'ccxt',
    '--hidden-import', 'pandas',
    '--hidden-import', 'numpy',
    module_name
]

try:
    subprocess.run(cmd, check=True)
    print(f"✅ {module_name} built successfully!")
    print(f"📍 Output: dist/{module_name.replace('.py', '')}.exe")
except subprocess.CalledProcessError as e:
    print(f"❌ Build failed!")
    sys.exit(1)
