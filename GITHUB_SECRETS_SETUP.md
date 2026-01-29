# GitHub Secrets Setup Guide

**Purpose**: Securely inject production credentials into Mac desktop app builds

**Required for**: Phase 1 of the Mac login fix to work correctly

---

## Why GitHub Secrets?

GitHub Secrets allow us to:
- ✅ Store sensitive credentials securely (encrypted)
- ✅ Inject them into builds without exposing them in code
- ✅ Ensure all Mac downloads have working login credentials
- ✅ Keep secrets out of public repository

---

## Step-by-Step Setup

### Step 1: Go to Repository Settings

1. Open: [https://github.com/hicklax13/Certify_Intel_v5.1.2](https://github.com/hicklax13/Certify_Intel_v5.1.2)
2. Click **Settings** tab (top right)
3. Click **Secrets and variables** in left sidebar
4. Click **Actions**
5. Click the green **New repository secret** button

### Step 2: Add DESKTOP_SECRET_KEY

On the "New secret" page:

**Name:**
```
DESKTOP_SECRET_KEY
```

**Secret:**
```
certify-intel-production-secret-key-2026-MSFWINTERCLINIC
```

Click **Add secret**

### Step 3: Add DESKTOP_ADMIN_PASSWORD

Click **New repository secret** again:

**Name:**
```
DESKTOP_ADMIN_PASSWORD
```

**Secret:**
```
MSFWINTERCLINIC2026
```

Click **Add secret**

### Step 4: Verify Secrets

You should now see 2 secrets listed:

| Name | Updated |
|------|---------|
| DESKTOP_ADMIN_PASSWORD | Just now |
| DESKTOP_SECRET_KEY | Just now |

✅ **Setup complete!**

---

## Step 5: Trigger New Build

Now that secrets are configured, trigger a new Mac build:

1. Go to: [https://github.com/hicklax13/Certify_Intel_v5.1.2/actions](https://github.com/hicklax13/Certify_Intel_v5.1.2/actions)
2. Click **Build Mac Installer (Add to Existing Release)** workflow
3. Click **Run workflow** dropdown
4. Select branch: `master`
5. Click green **Run workflow** button
6. Wait ~10-15 minutes for build to complete

### Build Success Indicators

Watch for these steps to complete with green checkmarks:

- ✅ Initialize database with production credentials
- ✅ Prepare desktop app with production config
- ✅ Create Mac icon from PNG
- ✅ Build macOS installer
- ✅ Upload to existing v5.1.2 release

### Check Build Logs

Click on the running workflow to see logs. Look for these messages:

```
✓ Production .env created successfully
ADMIN_EMAIL: admin@certifyintel.com
✓ Copied production .env
✓ Production .env verified (no placeholders)
```

If you see these, the secrets were injected correctly!

---

## Step 6: Test New DMG

After the build completes:

1. Go to: [https://github.com/hicklax13/Certify_Intel_v5.1.2/releases/tag/v5.1.2](https://github.com/hicklax13/Certify_Intel_v5.1.2/releases/tag/v5.1.2)
2. Download the **newest** DMG file (check timestamp)
3. Install following [MAC_INSTALLATION_GUIDE.md](MAC_INSTALLATION_GUIDE.md)
4. Login with:
   - **Email**: `admin@certifyintel.com`
   - **Password**: `MSFWINTERCLINIC2026`

✅ **Login should succeed!**

---

## Troubleshooting

### "ERROR: .env still contains placeholder variables"

**Cause**: GitHub Secrets not set correctly

**Fix**:
1. Check secret names are EXACTLY: `DESKTOP_SECRET_KEY` and `DESKTOP_ADMIN_PASSWORD`
2. Check secret values match exactly (no extra spaces)
3. Delete and re-create the secrets

### Build Succeeds But Login Still Fails

**Cause**: Downloaded old DMG instead of new one

**Fix**:
1. Check the DMG timestamp (should be AFTER the workflow ran)
2. Delete old DMG from Downloads folder
3. Re-download the fresh one
4. Make sure you're testing the NEW installation, not an old one

### "ERROR: Production .env not found"

**Cause**: Workflow couldn't find the `.env.production.template` file

**Fix**:
1. Verify file exists: `backend/.env.production.template`
2. Verify it's committed to Git
3. Verify the push succeeded
4. Re-run the workflow

---

## Security Notes

### What Gets Exposed

- ❌ **Secrets NOT exposed**: `DESKTOP_SECRET_KEY` and `DESKTOP_ADMIN_PASSWORD` are encrypted by GitHub
- ✅ **Default password documented**: `MSFWINTERCLINIC2026` appears in user-facing docs (intentional)
- ✅ **Users instructed to change**: Installation guide tells users to change password after first login

### Why Default Password Is OK

This is a standard practice for desktop apps:

1. **All installations need same credentials** to work out-of-the-box
2. **Default credentials documented** in installation guide
3. **Users instructed to change** for production use
4. Similar to: router admin/admin, database root/root, etc.

### For Production Deployments

If deploying for a specific organization:

1. Change `DESKTOP_ADMIN_PASSWORD` to organization-specific password
2. Update `MAC_INSTALLATION_GUIDE.md` with new password
3. Rebuild and distribute internally
4. Instruct users to change password after first login

---

## How It Works (Technical)

### GitHub Actions Workflow

The workflow (`.github/workflows/build-mac-only.yml`) does:

1. **Substitutes secrets** into `.env.production.template`:
   ```bash
   sed -e "s/\${DESKTOP_SECRET_KEY}/${{ secrets.DESKTOP_SECRET_KEY }}/g" \
       -e "s/\${DESKTOP_ADMIN_PASSWORD}/${{ secrets.DESKTOP_ADMIN_PASSWORD }}/g" \
       .env.production.template > .env
   ```

2. **Verifies no placeholders remain**:
   ```bash
   if grep -q "\${DESKTOP_" .env; then
     echo "ERROR: .env still contains placeholder variables"
     exit 1
   fi
   ```

3. **Bundles .env with app**:
   - Copies `.env` to `desktop-app/backend-bundle/`
   - PyInstaller includes it in the executable bundle
   - Electron app uses it when backend starts

### First App Launch

When the app starts for the first time:

1. Backend reads `.env` from bundle directory
2. `extended_features.py` runs `ensure_default_admin()`
3. Creates admin user with:
   - Email: `ADMIN_EMAIL` from `.env` (`admin@certifyintel.com`)
   - Password hash: `sha256(SECRET_KEY + ADMIN_PASSWORD)`
4. User can now login with documented credentials

---

## Next Steps After Setup

1. ✅ GitHub Secrets configured
2. ⏳ Trigger new Mac build
3. ⏳ Test login on fresh DMG
4. ⏳ Update release notes if needed
5. ⏳ Notify Mac users to re-download

---

**Last Updated**: January 29, 2026
**Related Files**:
- [MAC_INSTALLATION_GUIDE.md](MAC_INSTALLATION_GUIDE.md)
- [backend/.env.production.template](backend/.env.production.template)
- [.github/workflows/build-mac-only.yml](.github/workflows/build-mac-only.yml)
