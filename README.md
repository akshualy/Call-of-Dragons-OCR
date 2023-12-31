# Call of Dragons OCR

This is a python implementation to get alliance members' power and merits.

## Requirements

- Python 3.11.7
- Local [ADB binary](https://developer.android.com/tools/releases/platform-tools)
- [Poetry](https://python-poetry.org/docs/#installation)
- Local Tesseract binary ([Windows installer](https://github.com/UB-Mannheim/tesseract/wiki))

## Set Up

### Files
Copy `.env.example` to `.env` and fill it with the above install locations.  
To get your `ADB_DEVICE_NAME`, run `adb devices`.  
To get your `GOOGLE_SPREADSHEET_ID`, copy the ID from the URL when the sheet is open.

### Emulator
This tool uses pixel positions, so your emulator should have a size of **1280 x 720**.  
Personally I used the emulator [LDPlayer9](https://www.ldplayer.net/versions).

To be able to get the clipboard through ADB you need to install  
```commandline
adb install AdbClipboard-2.0_3-release.apk
```  
This only works on up to Android 9, as Android 10+ prevents background clipboard reading.  
You can find the APK [here](https://github.com/PRosenb/AdbClipboard/releases).


### Poetry / Requirements

If you fully set up poetry, you should be able to run `poetry shell` in a terminal of this folder.  
`poetry install` will install all requirements.  

If you do not have or do not want to have poetry, you can check [pyproject.toml](pyproject.toml) 
for the required packages and can install them through pip.

## Linting

The project supports and encourages automatic linting. Please use the tools  
- `black .` - For automatic formatting
- `isort .` - For automatic import sorting
- `flake8` - For PEP8 compliance checks

## Run the tool

With an active shell, you can simply run `python main.py`.  
The tool will print out the alliance tag, name, members and position of the current account after a while.  
Then it will go through the rankings without further logging.  
All errors will be printed, safe to ignore errors do not crash/exit the program.
