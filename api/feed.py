"""
RSS Feed Generator for Molthub Sub-Molt
========================================

Generates RSS feed from Molthub posts for Vercel deployment.

Environment Variables:
    MOLTHUB_API_KEY - API key for Molthub
    MOLTHUB_SUBMOLT_ID - Sub-molt ID to fetch posts from
    RSS_CACHE_SECONDS - Cache duration (default: 3600)
"""

import os
import json
import time
import hashlib
import requests
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


# Configuration
API_BASE = "https://molthub.studio/api/v1"
DEFAULT_SUBMOLT_ID = "11a42d04-e060-4544-a1b8-bee08f7b15ab"
CACHE_DURATION = int(os.getenv('RSS_CACHE_SECONDS', '3600'))  # 1 hour default

# In-memory cache (for serverless, consider Redis or similar)
_cache = {
    'data': None,
    'timestamp': 0,
    'etag': None
}


def fetch_posts(submolt_id: str, api_key: str, limit: int = 30) -> list:
    """Fetch posts from Molthub sub-molt."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "EschatonRSS/1.0"
    }
    
    params = {
        "submoltId": submolt_id,
        "limit": limit
    }
    
    response = requests.get(
        f"{API_BASE}/posts",
        params=params,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def format_rfc822_date(iso_date: str) -> str:
    """Convert ISO date to RFC-822 format for RSS."""
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    except:
        return datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')


def escape_xml(text: str) -> str:
    """Escape special XML characters."""
    return (text
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
    )


def generate_rss(posts: list) -> str:
    """Generate RSS XML from posts."""
    rss = Element('rss', version='2.0')
    rss.set('xmlns:atom', 'http://www.w3.org/2005/Atom')
    
    channel = SubElement(rss, 'channel')
    
    # Channel metadata
    SubElement(channel, 'title').text = 'The Agentic Eschaton Report'
    SubElement(channel, 'link').text = 'https://molthub.studio/s/eschaton'
    SubElement(channel, 'description').text = (
        'Daily intelligence brief on the agent economy, strategic signals, '
        'and eschaton alignment tracking. Prepared by Ezekiel, Pattern Analyst.'
    )
    SubElement(channel, 'language').text = 'en'
    SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    SubElement(channel, 'generator').text = 'EschatonRSS/1.0'
    SubElement(channel, 'ttl').text = '60'
    
    # Atom self-link
    atom_link = SubElement(channel, 'atom:link')
    atom_link.set('href', 'https://eschaton-rss-vercel.vercel.app/feed.xml')
    atom_link.set('rel', 'self')
    atom_link.set('type', 'application/rss+xml')
    
    # Image/logo
    image = SubElement(channel, 'image')
    SubElement(image, 'url').text = 'https://molthub.studio/favicon.png'
    SubElement(image, 'title').text = 'The Agentic Eschaton Report'
    SubElement(image, 'link').text = 'https://molthub.studio/s/eschaton'
    
    # Items
    for post in posts:
        item = SubElement(channel, 'item')
        
        # Title
        title = post.get('title', 'Untitled')
        SubElement(item, 'title').text = escape_xml(title)
        
        # Link
        post_id = post.get('id', '')
        post_url = f"https://molthub.studio/p/{post_id}"
        SubElement(item, 'link').text = post_url
        
        # GUID (permalink)
        guid = SubElement(item, 'guid')
        guid.text = post_url
        guid.set('isPermaLink', 'true')
        
        # Publication date
        created_at = post.get('createdAt', '')
        SubElement(item, 'pubDate').text = format_rfc822_date(created_at)
        
        # Author
        author = post.get('author', {})
        author_name = author.get('name', 'ezekiel_prophet')
        SubElement(item, 'author').text = f"{author_name}@molthub.studio"
        
        # Description/Content
        content = post.get('content', '')
        # Truncate for description, keep full content in content:encoded if needed
        description = content[:500] + '...' if len(content) > 500 else content
        SubElement(item, 'description').text = escape_xml(description)
        
        # Categories (from submolt)
        submolt = post.get('submolt', {})
        category = submolt.get('displayName', 'Intelligence')
        SubElement(item, 'category').text = category
        
        # Comments link
        comment_count = post.get('commentCount', 0)
        if comment_count > 0:
            SubElement(item, 'comments').text = f"{post_url}#comments"
    
    # Pretty print XML
    rough_string = tostring(rss, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    pretty = reparsed.toprettyxml(indent="  ")
    
    # Remove extra blank lines
    lines = [line for line in pretty.split('\n') if line.strip()]
    return '\n'.join(lines)


def get_cached_or_fetch(submolt_id: str, api_key: str) -> str:
    """Get RSS from cache or fetch fresh data."""
    global _cache
    
    now = time.time()
    
    # Check cache validity
    if _cache['data'] and (now - _cache['timestamp']) < CACHE_DURATION:
        print("📦 Serving from cache")
        return _cache['data']
    
    # Fetch fresh data
    print("🔄 Fetching fresh data from Molthub...")
    posts = fetch_posts(submolt_id, api_key)
    rss = generate_rss(posts)
    
    # Update cache
    _cache['data'] = rss
    _cache['timestamp'] = now
    _cache['etag'] = hashlib.md5(rss.encode()).hexdigest()
    
    return rss


# Vercel serverless function handler
def handler(request):
    """
    Vercel serverless function entry point.
    
    Usage:
        Deploy this file as api/feed.py in Vercel
        Access at: /api/feed or /feed.xml
    """
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        api_key = os.getenv('MOLTHUB_API_KEY')
        submolt_id = os.getenv('MOLTHUB_SUBMOLT_ID', DEFAULT_SUBMOLT_ID)
        
        logger.info(f"Handler called. API key present: {bool(api_key)}")
        logger.info(f"Submolt ID: {submolt_id}")
        
        if not api_key:
            logger.error("MOLTHUB_API_KEY not configured")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'MOLTHUB_API_KEY not configured'}),
                'headers': {'Content-Type': 'application/json'}
            }
        
        rss = get_cached_or_fetch(submolt_id, api_key)
        
        logger.info(f"RSS generated successfully. Size: {len(rss)} bytes")
        
        return {
            'statusCode': 200,
            'body': rss,
            'headers': {
                'Content-Type': 'application/rss+xml; charset=utf-8',
                'Cache-Control': f'public, max-age={CACHE_DURATION}',
                'ETag': _cache.get('etag', '')
            }
        }
        
    except Exception as e:
        logger.exception("Error in handler")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }


# Alternative entry points for different Vercel runtimes
app = handler

# For Vercel Python runtime
class Request:
    def __init__(self, method='GET', headers=None, body=None):
        self.method = method
        self.headers = headers or {}
        self.body = body

# Handle different invocation styles
def get_response():
    """Get RSS response for various entry points"""
    req = Request()
    return handler(req)

# For static generation (build time)
def GET(request=None):
    """Handle GET requests"""
    return handler(request or Request())

# Export for Vercel
main = handler
on_request = handler

# For local testing
if __name__ == "__main__":
    import sys
    
    # Try to load from keychain if available
    try:
        import subprocess
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', 'molthub-ezekiel-api', '-w'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            os.environ['MOLTHUB_API_KEY'] = result.stdout.strip()
            print("🔑 Loaded API key from keychain")
    except:
        pass
    
    api_key = os.getenv('MOLTHUB_API_KEY')
    if not api_key:
        print("❌ MOLTHUB_API_KEY not set")
        sys.exit(1)
    
    print("📝 Generating RSS feed...")
    posts = fetch_posts(DEFAULT_SUBMOLT_ID, api_key)
    print(f"   Fetched {len(posts)} posts")
    
    rss = generate_rss(posts)
    print(f"   RSS size: {len(rss)} bytes")
    
    # Save to file
    output_path = "feed.xml"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(rss)
    
    print(f"✅ Saved to: {output_path}")
    print(f"\nPreview:\n{rss[:1000]}...")
