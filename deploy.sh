#!/bin/bash
# deploy.sh - Deploy Eschaton RSS to Vercel

set -e

echo "🚀 Deploying Eschaton RSS to Vercel..."

# Check for Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    
    # Try npm
    if command -v npm &> /dev/null; then
        echo "Installing via npm..."
        npm install -g vercel || {
            echo "❌ npm install failed. Trying pnpm..."
            if command -v pnpm &> /dev/null; then
                pnpm add -g vercel
            fi
        }
    fi
    
    # Check again
    if ! command -v vercel &> /dev/null; then
        echo "❌ Could not install Vercel CLI automatically."
        echo ""
        echo "Please install manually:"
        echo "  npm i -g vercel"
        echo "  # or"
        echo "  pnpm add -g vercel"
        echo "  # or"
        echo "  yarn global add vercel"
        echo ""
        echo "Then run: vercel login"
        exit 1
    fi
fi

# Ensure we're logged in
echo "🔐 Checking Vercel login..."
vercel whoami || {
    echo "❌ Not logged in. Please run: vercel login"
    exit 1
}

# Copy latest reports
echo "📄 Syncing latest reports..."
mkdir -p reports
cp ~/.openclaw/workspace-agents/research-agent/daily-report-*.md reports/ 2>/dev/null || true

# Commit changes
git add -A
git commit -m "Update reports - $(date '+%Y-%m-%d %H:%M')" || true

# Deploy
echo "🌍 Deploying to Vercel..."
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Your RSS feed is available at:"
echo "  https://eschaton-rss.vercel.app/api/feed"
echo ""
echo "Landing page:"
echo "  https://eschaton-rss.vercel.app"
echo ""
