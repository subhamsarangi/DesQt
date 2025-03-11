import os
import subprocess


def build_app():
    """Build the application using PyInstaller as a single standalone executable."""
    # Define the spec file content for a standalone executable
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add offline content to the bundle
offline_content_path = os.path.abspath('offline_content')
if os.path.exists(offline_content_path):
    a.datas += [(f'offline_content/{file}', 
                 os.path.join(offline_content_path, file), 
                 'DATA') 
                for file in os.listdir(offline_content_path)]

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DesQt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico' if os.path.exists('app_icon.ico') else None,
    singlefile=True  # <--- This ensures a single standalone EXE!
)
"""

    # Write the spec file
    with open("app_standalone.spec", "w") as f:
        f.write(spec_content)

    # Run PyInstaller without --onefile (handled in .spec)
    cmd = ["poetry", "run", "pyinstaller", "app_standalone.spec"]
    subprocess.run(cmd, check=True)

    print("Build completed successfully. Standalone executable is in the dist folder.")


if __name__ == "__main__":
    build_app()
