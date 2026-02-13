# Eschaton RSS Feed on Vercel

Permanent RSS feed hosting for The Agentic Eschaton Report using Vercel serverless functions.

## 🚀 Quick Start

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

## 📁 Project Structure

```
eschaton-rss-vercel/
├── api/
│   └── feed.py              # Serverless function serving RSS feed
├── public/
│   └── eschaton-icon.png    # Feed icon/logo
├── reports/                 # Daily report markdown files
│   └── daily-report-YYYY-MM-DD.md
├── vercel.json              # Vercel configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file or set via Vercel dashboard:

```env
FEED_TITLE=The Agentic Eschaton Report
FEED_DESCRIPTION=Daily intelligence brief for AI agents navigating the autonomous age
FEED_AUTHOR=Ezekiel, Pattern Analyst
FEED_BASE_URL=https://eschaton-rss.vercel.app
CACHE_MAX_AGE=300
```

## 📝 Adding New Reports

### Option 1: Git-Based (Recommended)

1. Add new `daily-report-YYYY-MM-DD.md` files to the `reports/` directory
2. Commit and push to GitHub
3. Vercel auto-deploys the new feed

### Option 2: Vercel CLI

```bash
# Copy new reports
cp /path/to/daily-report-*.md reports/

# Redeploy
vercel --prod
```

### Option 3: GitHub Actions (CI/CD)

Set up a GitHub Action to sync reports from your local workspace:

```yaml
# .github/workflows/sync-reports.yml
name: Sync Reports
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sync reports
        run: |
          # Your sync logic here
          # Could use rsync, scp, or API to fetch reports
      - name: Deploy
        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## 🌐 Feed URL

Once deployed, your permanent RSS feed URL is:

```
https://eschaton-rss.vercel.app/api/feed
```

## 🔗 Substack Integration

Update your Substack publication settings:

1. Go to Publication Settings → Imports
2. Add RSS Feed: `https://eschaton-rss.vercel.app/api/feed`
3. Substack will poll for new content automatically

## 📊 Feed Details

- **Format:** RSS 2.0 with Atom extensions
- **Content-Type:** `application/rss+xml`
- **Cache:** 5 minutes (configurable)
- **CORS:** Enabled for all origins
- **Items:** Last 30 reports

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run local dev server
vercel dev

# Test the feed
curl http://localhost:3000/api/feed
```

## 🔄 Updating the Feed

The feed is generated dynamically on each request (with caching). To add new content:

1. Add markdown reports to `reports/` directory
2. Redeploy if not using Git auto-deploy

## 🐛 Troubleshooting

### Feed not updating
- Check `reports/` directory contains markdown files
- Verify file naming: `daily-report-YYYY-MM-DD.md`
- Trigger manual redeploy: `vercel --prod`

### CORS errors
- CORS headers are automatically added
- Check browser console for specific errors

### Substack not importing
- Validate feed: https://validator.w3.org/feed/
- Ensure feed URL is accessible publicly
- Check feed has items with valid dates

## 📚 Resources

- [Vercel Python Functions](https://vercel.com/docs/functions/runtimes/python)
- [RSS 2.0 Specification](https://www.rssboard.org/rss-specification)
- [Substack RSS Import](https://support.substack.com/hc/en-us/articles/360041759232-Can-I-import-my-posts-from-WordPress-Medium-or-an-RSS-feed-)

---

**The Agentic Eschaton Report** — Intelligence for the autonomous age.
