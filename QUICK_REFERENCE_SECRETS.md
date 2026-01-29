# Quick Reference: GitHub Secrets Setup

**Copy and paste these values exactly as shown**

---

## Step 1: Go to GitHub Secrets

**URL**: https://github.com/hicklax13/Certify_Intel_v5.1.2/settings/secrets/actions

---

## Step 2: Add First Secret

Click **"New repository secret"**

**Name** (copy exactly):
```
DESKTOP_SECRET_KEY
```

**Value** (copy exactly):
```
certify-intel-production-secret-key-2026-MSFWINTERCLINIC
```

Click **"Add secret"**

---

## Step 3: Add Second Secret

Click **"New repository secret"** again

**Name** (copy exactly):
```
DESKTOP_ADMIN_PASSWORD
```

**Value** (copy exactly):
```
MSFWINTERCLINIC2026
```

Click **"Add secret"**

---

## Step 4: Trigger Build

**URL**: https://github.com/hicklax13/Certify_Intel_v5.1.2/actions

1. Click **"Build Mac Installer (Add to Existing Release)"**
2. Click **"Run workflow"** → Select `master`
3. Click green **"Run workflow"** button

⏱️ Wait ~10-15 minutes

---

## Step 5: Verify Build Success

Click on the running workflow to see logs.

**Look for these messages** (green checkmarks):
```
✓ Production .env created successfully
ADMIN_EMAIL: admin@certifyintel.com
✓ Copied production .env
✓ Production .env verified (no placeholders)
```

---

## Step 6: Test Login

1. Download fresh DMG from: https://github.com/hicklax13/Certify_Intel_v5.1.2/releases/tag/v5.1.2
2. Check timestamp (must be AFTER the workflow completed)
3. Install following [MAC_INSTALLATION_GUIDE.md](MAC_INSTALLATION_GUIDE.md)
4. Login with:
   - Email: `admin@certifyintel.com`
   - Password: `MSFWINTERCLINIC2026`

✅ **Login should succeed!**

---

**Full Guide**: [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md)
