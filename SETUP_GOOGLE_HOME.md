# Google Home Integration Setup Guide

To integrate this PMS with Google Home, follow these steps:

## 1. Google Cloud Project Setup
1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Home Graph API**.
3. Create a Service Account and download the JSON key.

## 2. Actions on Google Setup
1. Go to the [Actions on Google Console](https://console.actions.google.com/).
2. Create a new Smart Home project.
3. Under **Develop > Actions**, add your Odoo fulfillment URL:
   `https://your-odoo-domain.com/google_home/fulfillment`
4. Under **Account Linking**, configure OAuth2:
   - Client ID/Secret: (From Odoo OAuth provider)
   - Authorization URL: `https://your-odoo-domain.com/oauth2/authorize`
   - Token URL: `https://your-odoo-domain.com/oauth2/token`

## 3. Odoo Configuration
1. Install the `sc_google_home` module.
2. Go to **Settings > Technical > Parameters > System Parameters**.
3. Add `sc_google_home.bearer_token` with a secure random string.
4. Ensure your Odoo instance is accessible via HTTPS.

## 4. STAPS Synchronization
1. Use the `wuchang_master.py` dashboard to monitor device sync status.
2. Every command execution is logged with STAPS high-precision timing.
