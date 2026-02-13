# 🚀 Deployment Guide

## Quick Deploy (Interactive)

The fastest way to deploy is using the Vercel CLI:

```bash
# 1. Install Vercel CLI (if not already installed)
pnpm add -g vercel

# 2. Login to Vercel
vercel login

# 3. Navigate to project
cd ~/projects/eschaton-rss-vercel

# 4. Deploy
vercel --prod
```

You'll be prompted to:
- Link to existing project or create new
- Set project name (suggest: `eschaton-rss`)
- Confirm settings

Your feed will be live at: `https://eschaton-rss.vercel.app/api/feed`

---

## GitHub Integration (Recommended)

For automatic deployments on every commit:

### Step 1: Create GitHub Repository

```bash
cd ~/projects/eschaton-rss-vercel

# Create GitHub repo (using gh CLI)
gh repo create eschaton-rss-vercel --public --push

# Or manually:
git remote add origin https://github.com/YOUR_USERNAME/eschaton-rss-vercel.git
git push -u origin main
```

### Step 2: Connect to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Vercel auto-detects Python project
4. Deploy!

### Step 3: Enable Auto-Deploy

With GitHub connected, every push to `main` automatically deploys.

---

## Environment Variables

Set these in Vercel Dashboard (Project → Settings → Environment Variables):

| Variable | Value | Description |
|----------|-------|-------------|
| `FEED_TITLE` | `The Agentic Eschaton Report` | Feed title |
| `FEED_DESCRIPTION` | `Daily intelligence brief...` | Feed description |
| `FEED_AUTHOR` | `Ezekiel, Pattern Analyst` | Author name |
| `FEED_BASE_URL` | `https://your-url.vercel.app` | Your Vercel URL |
| `CACHE_MAX_AGE` | `300` | Cache duration (seconds) |

---

## GitHub Actions (CI/CD)

For automated deployment with GitHub Actions:

### 1. Get Vercel Token

```bash
vercel login
vercel tokens create
```

Copy the token and add to GitHub Secrets:
- Go to: `https://github.com/YOUR_USERNAME/eschaton-rss-vercel/settings/secrets/actions`
- Add secret: `VERCEL_TOKEN`

### 2. Get Org and Project IDs

```bash
cd ~/projects/eschaton-rss-vercel
cat .vercel/project.json
```

Add to GitHub Secrets:
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

### 3. Workflow File

Already included: `.github/workflows/deploy.yml`

---

## Updating the Feed

### Manual Update

```bash
cd ~/projects/eschaton-rss-vercel

# Copy new reports
cp ~/.openclaw/workspace-agents/research-agent/daily-report-*.md reports/

# Commit and push
git add reports/
git commit -m "Add reports for $(date +%Y-%m-%d)"
git push
```

### Automated Update

See `update-reports.sh` for a script that can be run via cron or scheduled GitHub Actions.

---

## Custom Domain

To use a custom domain:

1. Go to Vercel Dashboard → Project → Settings → Domains
2. Add your domain
3. Configure DNS as instructed
4. Update `FEED_BASE_URL` environment variable

---

## Troubleshooting

### "No credentials found"

Run `vercel login` first.

### "Project not found"

Run `vercel link` to link to existing project.

### Feed not updating

- Check that reports are in `reports/` directory
- Verify file naming: `daily-report-YYYY-MM-DD.md`
- Check Vercel deployment logs

### CORS errors

CORS is enabled by default. If issues persist, check browser console for specifics.

---

## Post-Deployment Checklist

- [ ] RSS feed loads at `/api/feed`
- [ ] Landing page loads at `/`
- [ ] Feed validates at https://validator.w3.org/feed/
- [ ] Substack can import the feed
- [ ] Auto-deploy is working (test with a commit)

---

**Your permanent RSS URL:** `https://eschaton-rss.vercel.app/api/feed`
