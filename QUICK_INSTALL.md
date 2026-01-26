# Certify Intel - Quick Installation Guide

> **Estimated Time**: 5-10 minutes

---

## Prerequisites

Before starting, ensure you have:

| Software | Required Version | Download Link |
|----------|-----------------|---------------|
| Python | 3.9 or higher | https://www.python.org/downloads/ |
| Google Chrome | Any recent version | https://www.google.com/chrome/ |

**Windows Users**: When installing Python, **check "Add Python to PATH"** during installation.

---

## Option 1: Automated Setup (Recommended)

### Windows

1. Download the ZIP from GitHub → Click **"<> Code"** → **"Download ZIP"**
2. Extract the ZIP to your Desktop
3. **IMPORTANT**: Rename the extracted folder from `Project_Intel_v5.0.1-master` to `certify_intel`
4. Open the `certify_intel` folder
5. Double-click **`setup.bat`**
6. Follow the prompts

### Mac / Linux

1. Download the ZIP from GitHub → Click **"<> Code"** → **"Download ZIP"**
2. Extract the ZIP to your Desktop
3. Rename the extracted folder to `certify_intel`
4. Open Terminal and run:
   ```bash
   cd ~/Desktop/certify_intel
   chmod +x setup.sh
   ./setup.sh
   ```
5. Follow the prompts

---

## Option 2: Manual Setup

### Step 1: Download & Extract

1. Go to: https://github.com/hicklax13/Project_Intel_v5.0.1
2. Click the green **"<> Code"** button
3. Click **"Download ZIP"**
4. Extract to your Desktop

### Step 2: Rename the Folder (IMPORTANT!)

> **Why?** GitHub creates long folder names that can cause installation failures on Windows.

Rename the extracted folder:
- **From**: `Project_Intel_v5.0.1-master` (or similar long name)
- **To**: `certify_intel`

### Step 3: Open Terminal/Command Prompt

**Windows**:
1. Open the `certify_intel` folder
2. Open the `backend` folder
3. Click the address bar, type `cmd`, press Enter

**Mac/Linux**:
```bash
cd ~/Desktop/certify_intel/backend
```

### Step 4: Create Virtual Environment

```bash
python -m venv venv
```

### Step 5: Activate Virtual Environment

**Windows (Command Prompt)**:
```bash
venv\Scripts\activate
```

**Windows (PowerShell)**:
```powershell
venv\Scripts\Activate.ps1
```

**Mac/Linux**:
```bash
source venv/bin/activate
```

Your prompt should now show `(venv)` at the beginning.

### Step 6: Install Dependencies

```bash
pip install -r requirements.txt
```

This takes 2-5 minutes.

### Step 7: Create Configuration File

**Windows**:
```bash
copy .env.example .env
```

**Mac/Linux**:
```bash
cp .env.example .env
```

### Step 8: Start the Server

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 9: Open in Browser

1. Open Google Chrome
2. Go to: **http://localhost:8000**
3. Login with:
   - **Email**: `admin@certifyhealth.com`
   - **Password**: `certifyintel2024`

---

## Troubleshooting

### "Python is not recognized"

**Cause**: Python not in system PATH.

**Fix (Windows)**:
1. Reinstall Python from https://www.python.org/downloads/
2. During installation, check **"Add Python to PATH"**
3. Restart Command Prompt

**Fix (Mac)**:
```bash
brew install python3
```

**Fix (Linux)**:
```bash
sudo apt install python3 python3-venv python3-pip
```

---

### "pip install" fails with path error (Windows)

**Cause**: Windows has a 260 character path limit.

**Fix Option 1** - Move to shorter path:
1. Move the `certify_intel` folder to `C:\certify_intel`
2. Delete the `venv` folder if it exists
3. Run setup again

**Fix Option 2** - Enable Long Paths (requires admin):
1. Press `Win + R`, type `regedit`, press Enter
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Double-click `LongPathsEnabled`
4. Set value to `1`
5. Restart your computer
6. Run setup again

---

### "Port 8000 already in use"

**Cause**: Another application is using port 8000.

**Fix**: Use a different port:
```bash
uvicorn main:app --host 0.0.0.0 --port 8001
```
Then open: http://localhost:8001

---

### Login doesn't work

**Cause**: Password hash mismatch with SECRET_KEY.

**Fix**: Reset the admin password:
```bash
python -c "
import os, hashlib
from dotenv import load_dotenv
from database import SessionLocal, User
load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY', '')
new_hash = hashlib.sha256(f'{SECRET_KEY}certifyintel2024'.encode()).hexdigest()
db = SessionLocal()
user = db.query(User).filter(User.email == 'admin@certifyhealth.com').first()
if user: user.hashed_password = new_hash; db.commit(); print('Password reset!')
db.close()
"
```

---

### PowerShell "execution policy" error

**Cause**: PowerShell blocks script execution by default.

**Fix**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Starting the Server Later

After initial setup, to start the server again:

**Windows**:
```bash
cd C:\Users\YourName\Desktop\certify_intel\backend
venv\Scripts\activate
python main.py
```

**Mac/Linux**:
```bash
cd ~/Desktop/certify_intel/backend
source venv/bin/activate
python main.py
```

Then open: http://localhost:8000

---

## Enabling AI Features (Optional)

To enable AI-powered summaries, chat, and research:

1. Open `backend/.env` in a text editor
2. Add your API keys:
   ```env
   OPENAI_API_KEY=sk-your-openai-key-here
   GOOGLE_AI_API_KEY=your-gemini-key-here
   ```
3. Restart the server

Get API keys from:
- OpenAI: https://platform.openai.com/api-keys
- Google Gemini: https://makersuite.google.com/app/apikey

---

## Quick Reference Commands

| Action | Windows | Mac/Linux |
|--------|---------|-----------|
| Activate venv | `venv\Scripts\activate` | `source venv/bin/activate` |
| Start server | `python main.py` | `python main.py` |
| Stop server | `Ctrl + C` | `Ctrl + C` |
| Deactivate venv | `deactivate` | `deactivate` |

---

## Need Help?

- Check the full documentation: [CLAUDE.md](CLAUDE.md)
- Report issues: https://github.com/hicklax13/Project_Intel_v5.0.1/issues
