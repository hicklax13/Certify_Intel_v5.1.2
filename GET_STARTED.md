# Get Started with Certify Intel

**The easiest way to track and analyze 82+ healthcare competitors**

---

## Choose Your Installation Method

### 🖥️ Desktop App (Recommended - Easiest)

**Download and run immediately - no setup required**

#### For macOS

**Step 1: Which Mac do you have?**

Click  (Apple menu) → About This Mac

- See "Apple M1" or "Apple M2" or "Apple M3" or "Apple M4"? → You have **Apple Silicon**
- See "Intel"? → You have an **Intel Mac**

**Step 2: Download**

Go to: [https://github.com/hicklax13/Certify_Intel_v5.1.2/releases](https://github.com/hicklax13/Certify_Intel_v5.1.2/releases)

- **Apple Silicon (M1/M2/M3/M4)**: Download `arm64.dmg` ← **Most common**
- **Intel Macs**: Download `x64.dmg`

**Step 3: Install**

1. Open the downloaded `.dmg` file
2. Drag "Certify Intel" to "Applications" folder
3. **Important**: Right-click "Certify Intel" in Applications → select "Open" (not double-click!)
4. Click "Open" again when security warning appears
5. Wait 10 seconds for app to start
6. Login with:
   - **Email**: `admin@certifyintel.com`
   - **Password**: `MSFWINTERCLINIC2026`

✅ **You're in!** See [What's Next](#whats-next) below.

> **Need help?** See [Mac Installation Guide →](MAC_INSTALLATION_GUIDE.md)

#### For Windows

1. Download: [Windows Installer (EXE)](https://github.com/hicklax13/Certify_Intel_v5.1.2/releases)
2. Run installer, click through wizard
3. Launch Certify Intel
4. Login with:
   - **Email**: `admin@certifyintel.com`
   - **Password**: `MSFWINTERCLINIC2026`

---

### 🌐 Web App (For Developers)

**Run from Python source code - requires Python 3.9+**

```bash
# 1. Clone the repository
git clone https://github.com/hicklax13/Certify_Intel_v5.1.2.git
cd Certify_Intel_v5.1.2

# 2. Set up backend
cd backend
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env and set SECRET_KEY (required)

# 4. Start the server
python main.py
```

Then open: [http://localhost:8000](http://localhost:8000)

Login with:
- **Email**: `admin@certifyintel.com`
- **Password**: `MSFWINTERCLINIC2026`

> **Need help?** See [Setup Guide →](SETUP_GUIDE.md)

---

## What's Next?

After logging in:

### 1. **Browse Competitors**
Click "Competitors" → See all 82 pre-loaded healthcare technology companies

### 2. **View Latest News**
Click "News Feed" → Real-time competitor news from 13+ sources

### 3. **Generate Battlecards**
Click "Sales & Marketing" → Create sales battlecards for any competitor

### 4. **Run Reports**
Click "Reports" → Export PDF/Excel reports for your team

### 5. **Compare Competitors**
Click "Comparison" → Side-by-side analysis of 2-4 competitors

### 6. **Track Win/Loss**
Click "Analytics" → Log deals won or lost against competitors

---

## Important: Change Your Password

The default credentials are **shared by all installations**. For production use:

1. Login with default credentials
2. Click your email in top-right → "Settings"
3. Go to "User Management"
4. Create a new admin user with **your own password**
5. Delete or disable the default admin account

---

## Features Overview

| Feature | Description | Coverage |
|---------|-------------|----------|
| **Competitors** | Pre-loaded database | 82 companies |
| **Products** | Product/service catalog | 789 products (100%) |
| **News Feed** | Real-time news monitoring | 1,634 articles |
| **Sales Battlecards** | Competitive sales materials | AI-powered |
| **Data Quality** | Source verification | 86% verified |
| **AI Analysis** | GPT-4 + Gemini hybrid | Optional (requires API key) |

---

## Optional: Add AI Features

The app works out-of-the-box without AI, but you can enable:

### OpenAI (GPT-4)
1. Get API key: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Click "Settings" → "AI Configuration"
3. Paste your OpenAI API key
4. Click "Save"

### Google Gemini (Cheaper alternative)
1. Get API key: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Click "Settings" → "AI Configuration"
3. Paste your Google AI API key
4. Click "Save"

**Cost**: Gemini is ~90% cheaper than OpenAI for bulk tasks ($0.075 vs $5-15 per 1M tokens)

---

## Need Help?

| Question | Answer |
|----------|--------|
| App won't start | Wait 30 seconds and try again. Check if port 8000 is free. |
| Login fails | Check caps lock. Password is case-sensitive. |
| macOS security warning | Right-click app → "Open" (don't double-click first time) |
| Blank screen | Close app completely (Cmd+Q on Mac, Alt+F4 on Windows), relaunch. |
| Missing data | Data is pre-loaded. If missing, click "Competitors" → "Refresh All" |

**Still stuck?** Open an issue on GitHub: [https://github.com/hicklax13/Certify_Intel_v5.1.2/issues](https://github.com/hicklax13/Certify_Intel_v5.1.2/issues)

---

## Documentation

| Document | Purpose |
|----------|---------|
| [GET_STARTED.md](GET_STARTED.md) | **You are here** - Quick start guide |
| [MAC_INSTALLATION_GUIDE.md](MAC_INSTALLATION_GUIDE.md) | Detailed Mac installation with troubleshooting |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Developer setup for web app |
| [CLAUDE.md](CLAUDE.md) | Technical documentation |

---

**Version**: 5.1.2
**Last Updated**: January 29, 2026
**Repository**: [https://github.com/hicklax13/Certify_Intel_v5.1.2](https://github.com/hicklax13/Certify_Intel_v5.1.2)
