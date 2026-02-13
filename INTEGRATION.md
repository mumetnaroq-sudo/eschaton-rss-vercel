# 🔗 Integration Guide

## Overview

After deploying to Vercel, update these systems to use the new permanent RSS URL:

**New RSS Feed URL:** `https://eschaton-rss.vercel.app/api/feed`

---

## 1. Substack Integration

### Update RSS Import

1. Go to your Substack publication settings
2. Navigate to **Settings → Imports**
3. Replace the old Cloudflare tunnel URL with:
   ```
   https://eschaton-rss.vercel.app/api/feed
   ```
4. Save and verify the feed imports correctly

### Alternative: Manual Import

If automatic import doesn't work:
1. Copy content from individual reports
2. Paste into Substack as new posts
3. Add backdated publication dates

---

## 2. Update Ezekiel's Automation

### Files to Update

#### `~/projects/eschaton-rss/ezekiel_publish.py`

Update the publish target URLs:

```python
# OLD (Cloudflare tunnel - changeable)
# FEED_BASE_URL = "https://farmers-prove-pediatric-alphabetical.trycloudflare.com"

# NEW (Vercel - permanent)
FEED_BASE_URL = "https://eschaton-rss.vercel.app"
```

#### `~/projects/eschaton-rss/generate-rss.py`

Update the feed link generation:

```python
# Around line 22
FEED_LINK = "https://eschaton-rss.vercel.app"
# Or keep reading from env/file but update the default
```

#### `~/projects/eschaton-rss/PIPELINE.md`

Update the pipeline documentation to reflect:
- New permanent URL
- Vercel deployment instead of Cloudflare tunnels
- Git-based sync workflow

---

## 3. Automation Sync Script

Add this to Ezekiel's daily publish script:

```bash
#!/bin/bash
# sync-to-vercel.sh - Run after generating daily report

ESCHATON_DIR="${HOME}/.openclaw/workspace-agents/research-agent"
VERCEL_DIR="${HOME}/projects/eschaton-rss-vercel"

echo "🔄 Syncing to Vercel..."

# Copy latest report
cp "${ESCHATON_DIR}"/daily-report-*.md "${VERCEL_DIR}/reports/"

# Navigate to Vercel project
cd "$VERCEL_DIR"

# Commit and push (triggers auto-deploy if GitHub connected)
git add reports/
git commit -m "Add report for $(date +%Y-%m-%d)"
git push

echo "✅ Synced! New content will be live in ~1 minute."
```

---

## 4. Cron Job Updates

### Current Setup

Your current cron job likely runs the RSS generator:

```bash
# Example current crontab
0 2 * * * /Users/mumetnaroq/projects/eschaton-rss/publish-daily.sh
```

### New Setup

Add the sync step to the daily workflow:

```bash
# Edit crontab
crontab -e

# Updated entry
0 2 * * * /Users/mumetnaroq/projects/eschaton-rss/publish-daily.sh && /Users/mumetnaroq/projects/eschaton-rss-vercel/update-reports.sh
```

Or modify `publish-daily.sh` to include the sync step.

---

## 5. x402 Payment Gateway Updates

If you're using x402 for premium content:

Update the base URL in your payment configuration:

```javascript
// x402 config
const config = {
  baseUrl: "https://eschaton-rss.vercel.app",
  // ... rest of config
};
```

---

## 6. Verification Checklist

After updating all integrations:

- [ ] RSS feed loads at `https://eschaton-rss.vercel.app/api/feed`
- [ ] Feed validates at https://validator.w3.org/feed/
- [ ] Substack imports correctly
- [ ] Daily automation still works
- [ ] x402 payments work (if applicable)
- [ ] Reports appear in feed within 5 minutes of publishing
- [ ] Old Cloudflare tunnel can be safely disabled

---

## 7. Rollback Plan

If issues arise:

1. Keep the Cloudflare tunnel running until Vercel is confirmed working
2. Switch Substack back to old URL temporarily
3. Debug Vercel deployment
4. Re-switch once resolved

---

## 8. Benefits of New Setup

| Feature | Old (Cloudflare) | New (Vercel) |
|---------|-----------------|--------------|
| URL Stability | Changes on restart | Permanent |
| SSL Certificate | Auto-managed | Auto-managed |
| CDN | Cloudflare | Vercel Edge |
| Uptime | Depends on tunnel | 99.99% SLA |
| Auto-deploy | No | Yes (with Git) |
| Cost | Free | Free tier |

---

## Questions?

See `DEPLOY.md` for deployment help or `README.md` for general documentation.
