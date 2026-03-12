# Instagram MCP Setup Guide

**Connect Instagram to your Gold Tier AI Employee**

---

## Prerequisites

Before starting, you need:

1. ✅ **Instagram Business Account** (or Creator account)
2. ✅ **Facebook Page** connected to your Instagram
3. ✅ **Facebook App** (from Facebook Developer)

---

## Step 1: Convert to Business Account

### If you have a personal Instagram account:

1. Open Instagram app on your phone
2. Go to **Settings** → **Account**
3. Tap **Switch to Professional Account**
4. Select **Business** (not Creator)
5. Connect to your Facebook Page
6. Complete the setup

### Verify it's a Business account:
- Go to your Instagram profile
- You should see "Professional Account" or business category
- You should have "Insights" button

---

## Step 2: Get Instagram Business Account ID

### Method 1: Graph API Explorer (Recommended)

1. **Go to:** [Graph API Explorer](https://developers.facebook.com/tools/explorer/)

2. **Select your app** from dropdown

3. **Use your Facebook Page Access Token** (same as Facebook config)

4. **Run this query:**
   ```
   GET /v18.0/{your-facebook-page-id}?fields=instagram_business_account
   ```
   
   Replace `{your-facebook-page-id}` with your Page ID (e.g., `101144749664954`)

5. **Copy the Instagram Business Account ID:**
   ```json
   {
     "instagram_business_account": {
       "id": "17841400000000000"  ← COPY THIS
     }
   }
   ```

### Method 2: Get from Instagram Profile

1. Go to your Instagram profile in browser
2. View page source
3. Search for `"profile_id"`
4. Copy the number

---

## Step 3: Get Access Token

### Use Same Token as Facebook

Your **Facebook Page Access Token** also works for Instagram!

From your `.env` file:
```env
IG_ACCESS_TOKEN=EAAaTw6hPaqIeexyYK59SrYQZCgMK7aotbJoS0MUrv2RkeVfnwnb2wvU50v0O2hFys7pEcXgiTEQnBM44M7RNoI2tEsHVo0bU6iTvGhrKUfGtrjQsIvmJP7otQZBn9OZBHg28QtEiIr7y4yB3jTgYS8sIkVVeEQLGQHFMLhiKLE79nxtN9zTZAeCZCoPdi3RjK4KESpoqAWothk19pjF3AZDZD
```

This is the same as `FB_ACCESS_TOKEN` - they're the same token!

---

## Step 4: Configure .env

Edit your `.env` file:

```env
# ============================================
# Instagram Configuration
# ============================================
IG_APP_ID=144350074030
IG_APP_SECRET=17cd89ab4fea52a387f78fa60a1c
IG_ACCESS_TOKEN=EAAaTwyDePG4XGmR36hPaqIeexyYK59SrYQZCgMK7aotbJoS0MUrv2RkeVfnwnb2wvU50v0O2hFys7pEcXgiTEQnBM44M7RNoI2tEsHVo0bU6iTvGhrKUfGtrjQsIvmJP7otQZBn9OZBHg28QtEiIr7y4yB3jTgYS8sIkVVeEQLGQHFMLhiKLE79nxtN9zTZAeCZCoPdi3RjK4KESpoqAWothk19pjF3AZDZD
IG_BUSINESS_ACCOUNT_ID=178414000000000
IG_VERSION=v18.0
```

**Replace:**
- `IG_APP_ID` - Same as `FB_APP_ID`
- `IG_APP_SECRET` - Same as `FB_APP_SECRET`
- `IG_ACCESS_TOKEN` - Same as `FB_ACCESS_TOKEN`
- `IG_BUSINESS_ACCOUNT_ID` - Your Instagram Business ID from Step 2

---

## Step 5: Install Dependencies

```bash
cd D:\Documents\GitHub\Personal_AI_Employee_Gold_Tier\mcp-servers\instagram-mcp
npm install
```

---

## Step 6: Test Instagram Connection

```bash
cd D:\Documents\GitHub\Personal_AI_Employee_Gold_Tier\mcp-servers\instagram-mcp
node test-instagram.js
```

You should see:
```
✅ Instagram authenticated as your_username
✅ Instagram MCP Server is connected
```

---

## Step 7: Test Posting

### Create Test Image

For testing, create a simple test image or use any image URL.

### Run Test Post

```bash
cd D:\Documents\GitHub\Personal_AI_Employee_Gold_Tier\mcp-servers\instagram-mcp
node test-post-instagram.js
```

---

## How Instagram Posting Works

Instagram posting is **2-step process**:

1. **Create Media Container**
   - Upload image to Instagram
   - Instagram returns creation ID

2. **Publish Media**
   - Use creation ID to publish
   - Post appears on Instagram

This is different from Facebook which posts in one step.

---

## Approval Workflow (Same as Facebook)

1. **AI creates approval request** → `Pending_Approval/INSTAGRAM_POST_*.md`
2. **You review** in Obsidian
3. **Move to Approved/** to publish
4. **Orchestrator executes** via Instagram MCP
5. **Post published** to Instagram
6. **File moved to Done/**

---

## Required Permissions

Your token needs these permissions:
- ✅ `instagram_basic`
- ✅ `instagram_content_publish`
- ✅ `pages_read_engagement`

These are included by default in Page Access Tokens.

---

## Troubleshooting

### "Instagram Business Account not found"

**Solution:**
1. Verify Instagram is Business account (not personal)
2. Verify Instagram is connected to Facebook Page
3. Check Business Account ID is correct

### "Invalid access token"

**Solution:**
1. Token may be expired - get new one from Graph API Explorer
2. Token needs Instagram permissions - re-authorize

### "Media upload failed"

**Solution:**
1. Image URL must be publicly accessible
2. Image must meet Instagram requirements (size, format)
3. Try a different image

---

## Next Steps

After setup:

1. ✅ Test connection
2. ✅ Test posting with approval workflow
3. ✅ Integrate with orchestrator
4. ✅ Monitor Instagram DMs (future enhancement)

---

*Instagram MCP Setup Guide - Gold Tier AI Employee*
