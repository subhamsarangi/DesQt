## DESKTOP APPLICATION USING PyQt

### Install Dependencies:
`poetry install`
or 
`poetry add PyQt6 PyQt6-WebEngine pyinstaller`

### Test the app:
`poetry run python -m desqt.main`

### Build the standalone executable:
`poetry run python build.py`

### Find your executable:
The standalone executable will be in the dist folder, named DesQt.exe.

NOTE:
Some antivirus programs, especially Windows Defender, have a habit of freaking out over PyInstaller-built executables. Why? Because they see a single-file EXE with everything packed inside and assume it must be something evil. It’s not. It’s just how PyInstaller works. But hey, if Windows wants to panic over a perfectly normal program, that’s its problem, not ours.