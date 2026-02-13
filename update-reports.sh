#!/bin/bash
# update-reports.sh - Sync daily reports to Vercel project

REPORTS_SOURCE="${HOME}/.openclaw/workspace-agents/research-agent"
REPORTS_DEST="${HOME}/projects/eschaton-rss-vercel/reports"

echo "🔄 Syncing reports..."

# Create destination if needed
mkdir -p "$REPORTS_DEST"

# Copy all daily reports
cp "$REPORTS_SOURCE"/daily-report-*.md "$REPORTS_DEST/" 2>/dev/null || {
    echo "⚠️  No reports found in source directory"
    exit 1
}

# Count reports
REPORT_COUNT=$(ls -1 "$REPORTS_DEST"/daily-report-*.md 2>/dev/null | wc -l)
echo "✅ Synced $REPORT_COUNT reports"

# Git operations (if in a git repo)
if [ -d "$REPORTS_DEST/../.git" ]; then
    cd "$REPORTS_DEST/.."
    
    # Check for changes
    if ! git diff --quiet reports/ 2>/dev/null || ! git diff --cached --quiet reports/ 2>/dev/null; then
        echo "📦 Committing changes..."
        git add reports/
        git commit -m "Update reports - $(date '+%Y-%m-%d %H:%M')"
        
        # Push if remote exists
        if git remote get-url origin &>/dev/null; then
            echo "🚀 Pushing to remote..."
            git push
        fi
        
        echo "✅ Done! Changes will auto-deploy if GitHub integration is enabled."
    else
        echo "ℹ️  No changes to commit"
    fi
fi
