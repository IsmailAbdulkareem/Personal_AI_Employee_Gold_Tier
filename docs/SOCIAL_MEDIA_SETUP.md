# Social Media Developer Setup Guide

**Gold Tier AI Employee - Social Media Integration**

---

## Overview

This guide walks you through setting up developer accounts and API credentials for Facebook, Instagram, and Twitter/X integration with your Gold Tier AI Employee.

---

## Facebook Integration

### Step 1: Create Facebook Developer Account

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click **Get Started** or **Log In**
3. Complete developer verification:
   - Confirm email address
   - Add phone number
   - Accept terms of service

### Step 2: Create Facebook App

1. Go to [My Apps](https://developers.facebook.com/apps/)
2. Click **Create App**
3. Select use case: **Other** → **Next**
4. Select app type: **Business** → **Next**
5. Fill in app details:
   - **App Name**: Gold Tier AI Employee
   - **App Contact Email**: your-email@example.com
   - **Business Account**: Select or create
6. Click **Create App**

### Step 3: Configure Facebook Login

1. In app dashboard, click **Add Product**
2. Find **Facebook Login** → Click **Set Up**
3. Configure settings:
   - **Valid OAuth Redirect URIs**: `https://localhost:8080/callback`
   - **App Domains**: localhost (for development)
4. Save changes

### Step 4: Get Page Access Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from dropdown
3. Click **Get Token** → **Get Page Access Token**
4. Select your Facebook Page
5. Copy the **Access Token**
6. Click **Add Permission** and add:
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `publish_to_groups`

### Step 5: Configure MCP Server

Create config file:
```bash
nano config/facebook_config.json
```

Add:
```json
{
  "app_id": "your-app-id",
  "app_secret": "your-app-secret",
  "access_token": "your-page-access-token",
  "page_id": "your-page-id",
  "version": "v18.0"
}
```

### Step 6: Test Facebook Integration

```bash
cd mcp-servers/facebook-mcp
npm install
node index.js
```

---

## Instagram Integration

### Prerequisites

- Instagram **Business** or **Creator** account
- Facebook Page connected to Instagram
- Facebook Developer app (from above)

### Step 1: Convert to Business Account

1. Open Instagram app
2. Go to **Settings → Account**
3. Tap **Switch to Professional Account**
4. Select **Business**
5. Connect to Facebook Page

### Step 2: Get Instagram Business Account ID

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Run this query:
```
GET /me/accounts
```
4. Copy your **Page ID**
5. Run this query:
```
GET /<page-id>?fields=instagram_business_account
```
6. Copy the **instagram_business_account.id**

### Step 3: Add Instagram Graph API Permissions

1. Go to [App Review](https://developers.facebook.com/apps/<app-id>/app-review/)
2. Request permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `instagram_manage_comments`
   - `instagram_manage_insights`

### Step 4: Configure MCP Server

Create config file:
```bash
nano config/instagram_config.json
```

Add:
```json
{
  "app_id": "your-app-id",
  "app_secret": "your-app-secret",
  "access_token": "your-page-access-token",
  "instagram_business_account_id": "your-ig-business-account-id",
  "version": "v18.0"
}
```

### Step 5: Test Instagram Integration

```bash
cd mcp-servers/instagram-mcp
npm install
node index.js
```

---

## Twitter/X Integration

### Step 1: Apply for Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Click **Apply for a developer account**
3. Fill in application:
   - **Account name**: Gold Tier AI Employee
   - **Use case description**: "Automating business social media posting and analytics for AI Employee project"
   - **Email**: your-email@example.com
4. Wait for approval (usually 1-3 days)

### Step 2: Create Twitter App

Once approved:

1. Go to [Developer Portal](https://developer.twitter.com/en/portal/projects-and-apps)
2. Click **Create Project**
   - **Project name**: Gold Tier AI Employee
   - **Use case**: Business
3. Click **Create App** within project
   - **App name**: gold-tier-ai-employee
4. Save **API Key** and **API Secret**

### Step 3: Generate Access Token

1. In app settings, go to **Keys and Tokens**
2. Under **Authentication Tokens**, click **Generate**
3. Save:
   - **Access Token**
   - **Access Token Secret**
4. Under **Bearer Token**, click **Generate**
5. Save **Bearer Token**

### Step 4: Configure App Permissions

1. Go to **App Permissions**
2. Set to **Read and Write**
3. Enable **Request email address** (optional)
4. Save changes

### Step 5: Configure MCP Server

Create config file:
```bash
nano config/twitter_config.json
```

Add:
```json
{
  "api_key": "your-api-key",
  "api_secret": "your-api-secret",
  "access_token": "your-access-token",
  "access_secret": "your-access-secret",
  "bearer_token": "your-bearer-token"
}
```

### Step 6: Test Twitter Integration

```bash
cd mcp-servers/twitter-mcp
npm install
node index.js
```

---

## Environment Variables Setup

For security, use environment variables instead of config files:

### Windows (PowerShell)

```powershell
# Facebook
$env:FB_APP_ID="your-app-id"
$env:FB_APP_SECRET="your-app-secret"
$env:FB_ACCESS_TOKEN="your-access-token"
$env:FB_PAGE_ID="your-page-id"

# Instagram
$env:IG_APP_ID="your-app-id"
$env:IG_APP_SECRET="your-app-secret"
$env:IG_ACCESS_TOKEN="your-access-token"
$env:IG_BUSINESS_ACCOUNT_ID="your-ig-account-id"

# Twitter
$env:TWITTER_API_KEY="your-api-key"
$env:TWITTER_API_SECRET="your-api-secret"
$env:TWITTER_ACCESS_TOKEN="your-access-token"
$env:TWITTER_ACCESS_SECRET="your-access-secret"
$env:TWITTER_BEARER_TOKEN="your-bearer-token"
```

### Linux/macOS (Bash)

```bash
# Add to ~/.bashrc or ~/.zshrc
export FB_APP_ID="your-app-id"
export FB_APP_SECRET="your-app-secret"
export FB_ACCESS_TOKEN="your-access-token"
export FB_PAGE_ID="your-page-id"

export IG_APP_ID="your-app-id"
export IG_APP_SECRET="your-app-secret"
export IG_ACCESS_TOKEN="your-access-token"
export IG_BUSINESS_ACCOUNT_ID="your-ig-account-id"

export TWITTER_API_KEY="your-api-key"
export TWITTER_API_SECRET="your-api-secret"
export TWITTER_ACCESS_TOKEN="your-access-token"
export TWITTER_ACCESS_SECRET="your-access-secret"
export TWITTER_BEARER_TOKEN="your-bearer-token"

# Reload
source ~/.bashrc
```

### Using .env File (Recommended for Development)

Create `.env` file in project root:
```bash
nano .env
```

Add:
```env
# Facebook
FB_APP_ID=your-app-id
FB_APP_SECRET=your-app-secret
FB_ACCESS_TOKEN=your-access-token
FB_PAGE_ID=your-page-id

# Instagram
IG_APP_ID=your-app-id
IG_APP_SECRET=your-app-secret
IG_ACCESS_TOKEN=your-access-token
IG_BUSINESS_ACCOUNT_ID=your-ig-account-id

# Twitter
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_SECRET=your-access-secret
TWITTER_BEARER_TOKEN=your-bearer-token
```

Install dotenv:
```bash
npm install dotenv
```

Update MCP servers to load `.env`:
```javascript
require('dotenv').config();
```

---

## Testing All Integrations

### Test Script

Create test script:
```bash
nano scripts/test_social_media.js
```

Add:
```javascript
const fetch = require('node-fetch');

async function testFacebook() {
    console.log('Testing Facebook...');
    const response = await fetch(
        `https://graph.facebook.com/v18.0/${process.env.FB_PAGE_ID}?access_token=${process.env.FB_ACCESS_TOKEN}`
    );
    const result = await response.json();
    console.log('Facebook:', result);
}

async function testInstagram() {
    console.log('Testing Instagram...');
    const response = await fetch(
        `https://graph.facebook.com/v18.0/${process.env.IG_BUSINESS_ACCOUNT_ID}?fields=username,name&access_token=${process.env.IG_ACCESS_TOKEN}`
    );
    const result = await response.json();
    console.log('Instagram:', result);
}

async function testTwitter() {
    console.log('Testing Twitter...');
    const response = await fetch(
        'https://api.twitter.com/2/users/me',
        {
            headers: {
                'Authorization': `Bearer ${process.env.TWITTER_BEARER_TOKEN}`
            }
        }
    );
    const result = await response.json();
    console.log('Twitter:', result);
}

async function main() {
    try {
        await testFacebook();
        await testInstagram();
        await testTwitter();
        console.log('✅ All social media integrations working!');
    } catch (error) {
        console.error('❌ Test failed:', error.message);
    }
}

main();
```

Run test:
```bash
node scripts/test_social_media.js
```

---

## Troubleshooting

### Facebook: "Invalid Access Token"

1. Check token hasn't expired (short-lived tokens expire in 1 hour)
2. Generate long-lived token: [Access Token Tool](https://developers.facebook.com/tools/access_token/)
3. Verify page permissions are granted

### Instagram: "Business Account Not Found"

1. Ensure Instagram is converted to Business account
2. Verify Instagram is connected to Facebook Page
3. Check business account ID is correct

### Twitter: "Authentication Failed"

1. Verify all tokens are copied correctly
2. Check app permissions are set to "Read and Write"
3. Ensure developer account is approved

### Rate Limiting

| Platform | Limit | Solution |
|----------|-------|----------|
| Facebook | 200 calls/hour | Implement caching |
| Instagram | 200 calls/hour | Implement caching |
| Twitter | 300 tweets/day | Queue posts |

---

## Security Best Practices

1. **Never commit credentials** to git
2. **Use environment variables** or `.env` files
3. **Rotate tokens regularly** (every 90 days)
4. **Limit app permissions** to minimum required
5. **Use HTTPS** for all API calls
6. **Monitor API usage** for unusual activity

---

## Next Steps

After credentials are configured:

1. ✅ **Test each MCP server** individually
2. ✅ **Create test posts** on each platform
3. ✅ **Set up approval workflow** for social media posts
4. ✅ **Configure scheduled posting** in orchestrator
5. ✅ **Enable analytics tracking** in audit logger

---

## Resources

- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)
- [Facebook Access Token Tool](https://developers.facebook.com/tools/access_token/)
- [Twitter Developer Portal](https://developer.twitter.com/en/portal)

---

*Social Media Developer Setup Guide - Gold Tier AI Employee*
*For support: Check platform developer documentation*
