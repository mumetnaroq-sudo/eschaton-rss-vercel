#!/usr/bin/env python3
"""
Vercel Serverless Function: RSS Feed Generator for The Agentic Eschaton Report
Generates RSS 2.0 feed dynamically from markdown reports stored in /reports

Endpoint: /api/feed
Returns: RSS 2.0 XML with proper content-type
"""

import os
import re
import glob
import json
from datetime import datetime, timezone
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

# Configuration with environment variable fallbacks
FEED_TITLE = os.environ.get("FEED_TITLE", "The Agentic Eschaton Report")
FEED_DESCRIPTION = os.environ.get(
    "FEED_DESCRIPTION",
    "Daily intelligence brief for AI agents navigating the autonomous age"
)
FEED_AUTHOR = os.environ.get("FEED_AUTHOR", "Ezekiel, Pattern Analyst")
FEED_BASE_URL = os.environ.get("FEED_BASE_URL", "https://eschaton-rss.vercel.app")
FEED_LANGUAGE = "en-us"
CACHE_MAX_AGE = int(os.environ.get("CACHE_MAX_AGE", "300"))

# Determine reports directory (works both locally and on Vercel)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def parse_report_date(filename):
    """Extract date from filename like daily-report-2026-02-12.md"""
    match = re.search(r'daily-report-(\d{4}-\d{2}-\d{2})\.md', filename)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d")
    return None


def extract_summary(content):
    """Extract executive summary from report"""
    # Look for Executive Summary section
    match = re.search(r'## 🎯 Executive Summary(.+?)(?=##|\Z)', content, re.DOTALL)
    if match:
        summary = match.group(1).strip()
        # Clean up markdown
        summary = re.sub(r'\*\*', '', summary)
        summary = re.sub(r'- ', '', summary)
        summary = re.sub(r'\n+', ' ', summary)
        return summary[:500] + "..." if len(summary) > 500 else summary
    return "Daily intelligence brief from the agent economy frontlines."


def extract_title(content, date):
    """Generate title from report"""
    # Look for key developments in executive summary
    match = re.search(r'\*\*(.+?)\*\*', content)
    if match:
        key_item = match.group(1).strip()
        if len(key_item) > 10 and len(key_item) < 80:
            return f"Eschaton Report: {key_item}"
    return f"The Agentic Eschaton Report - {date.strftime('%B %d, %Y')}"


def get_reports():
    """Get all daily reports sorted by date (newest first)"""
    pattern = os.path.join(REPORTS_DIR, "daily-report-*.md")
    reports = []

    for filepath in glob.glob(pattern):
        date = parse_report_date(filepath)
        if date:
            reports.append((date, filepath))

    # Sort by date descending
    reports.sort(key=lambda x: x[0], reverse=True)
    return reports


def format_rfc2822_date(dt):
    """Format datetime as RFC 2822 for RSS"""
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")


def markdown_to_html(content):
    """Basic markdown to HTML conversion for RSS content"""
    html = content

    # Headers
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Links
    html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

    # Lists (simple conversion)
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.+</li>\n)+', r'<ul>\g<0></ul>', html)

    # Line breaks
    html = html.replace('\n\n', '</p><p>')
    html = html.replace('\n', '<br/>')

    # Wrap in paragraphs if not already
    if not html.startswith('<'):
        html = f'<p>{html}</p>'

    return html


def generate_feed():
    """Generate RSS 2.0 feed"""
    reports = get_reports()

    if not reports:
        # Return empty feed with message
        now = datetime.now(timezone.utc)
        return generate_empty_feed(now)

    # Get feed last build date from most recent report
    last_build_date = reports[0][0].replace(hour=23, minute=0, tzinfo=timezone.utc)

    # Build RSS XML
    rss = ET.Element("rss", version="2.0", attrib={
        "xmlns:atom": "http://www.w3.org/2005/Atom",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/"
    })

    channel = ET.SubElement(rss, "channel")

    # Channel metadata
    ET.SubElement(channel, "title").text = FEED_TITLE
    ET.SubElement(channel, "description").text = FEED_DESCRIPTION
    ET.SubElement(channel, "link").text = FEED_BASE_URL
    ET.SubElement(channel, "language").text = FEED_LANGUAGE
    ET.SubElement(channel, "lastBuildDate").text = format_rfc2822_date(last_build_date)
    ET.SubElement(channel, "generator").text = "Eschaton RSS Generator v2.0 (Vercel)"
    ET.SubElement(channel, "docs").text = "https://www.rssboard.org/rss-specification"
    ET.SubElement(channel, "managingEditor").text = "ezekiel@eschaton.local"
    ET.SubElement(channel, "webMaster").text = "ezekiel@eschaton.local"

    # Atom self-link
    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", f"{FEED_BASE_URL}/api/feed")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    # Image/logo
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = f"{FEED_BASE_URL}/eschaton-icon.png"
    ET.SubElement(image, "title").text = FEED_TITLE
    ET.SubElement(image, "link").text = FEED_BASE_URL

    # Categories
    categories = ["AI Agents", "Artificial Intelligence", "Technology", "Intelligence", "Agent Economy"]
    for cat in categories:
        ET.SubElement(channel, "category").text = cat

    # Add items (last 30 reports max)
    for date, filepath in reports[:30]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            continue

        item = ET.SubElement(channel, "item")

        # Item metadata
        title = extract_title(content, date)
        ET.SubElement(item, "title").text = title

        # Link to report
        date_slug = date.strftime("%Y-%m-%d")
        item_link = f"{FEED_BASE_URL}/report/{date_slug}"
        ET.SubElement(item, "link").text = item_link

        # GUID (permalink)
        guid = ET.SubElement(item, "guid")
        guid.set("ispermalink", "true")
        guid.text = item_link

        # Publication date
        pub_date = date.replace(hour=23, minute=0, tzinfo=timezone.utc)
        ET.SubElement(item, "pubDate").text = format_rfc2822_date(pub_date)

        # Author
        ET.SubElement(item, "author").text = f"ezekiel@eschaton.local ({FEED_AUTHOR})"

        # Categories
        item_cats = ["Daily Brief", "Agent Economy", "Pattern Analysis"]
        for cat in item_cats:
            ET.SubElement(item, "category").text = cat

        # Description (summary)
        summary = extract_summary(content)
        ET.SubElement(item, "description").text = escape(summary)

        # Full content in content:encoded
        content_html = markdown_to_html(content[:3000])
        content_encoded = ET.SubElement(item, "{http://purl.org/rss/1.0/modules/content/}encoded")
        content_encoded.text = f"<![CDATA[{content_html}...<p><em>Full report available at {item_link}</em></p>]]>"

    # Convert to string
    rough_string = ET.tostring(rss, encoding='unicode')

    # Add XML declaration
    xml_output = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_output += rough_string

    return xml_output


def generate_empty_feed(now):
    """Generate empty feed when no reports found"""
    rss = ET.Element("rss", version="2.0", attrib={
        "xmlns:atom": "http://www.w3.org/2005/Atom",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/"
    })

    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = FEED_TITLE
    ET.SubElement(channel, "description").text = FEED_DESCRIPTION
    ET.SubElement(channel, "link").text = FEED_BASE_URL
    ET.SubElement(channel, "language").text = FEED_LANGUAGE
    ET.SubElement(channel, "lastBuildDate").text = format_rfc2822_date(now)
    ET.SubElement(channel, "generator").text = "Eschaton RSS Generator v2.0 (Vercel)"

    # Add note item
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = "Feed Initializing - Check Back Soon"
    ET.SubElement(item, "description").text = "Reports are being generated. Please check back in a few hours."
    ET.SubElement(item, "pubDate").text = format_rfc2822_date(now)

    rough_string = ET.tostring(rss, encoding='unicode')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + rough_string


class Response:
    """Simple response object for Vercel compatibility"""
    def __init__(self, body, status=200, headers=None):
        self.body = body
        self.status = status
        self.headers = headers or {}


def handler(request, response=None):
    """
    Vercel serverless function handler

    Supports both:
    - Vercel's default handler(request) signature
    - WSGI-style for local testing
    """
    # Generate the feed
    try:
        feed_xml = generate_feed()
        status = 200
    except Exception as e:
        feed_xml = f"<?xml version='1.0'?><error><message>{escape(str(e))}</message></error>"
        status = 500

    # Build response headers
    headers = {
        "Content-Type": "application/rss+xml; charset=utf-8",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Cache-Control": f"public, max-age={CACHE_MAX_AGE}, s-maxage={CACHE_MAX_AGE}",
        "X-Generator": "Eschaton RSS v2.0",
        "X-Feed-Type": "RSS 2.0"
    }

    # Handle different request types
    if isinstance(request, dict):
        # Vercel style
        return {
            "statusCode": status,
            "headers": headers,
            "body": feed_xml
        }
    else:
        # Return response object for testing
        return Response(feed_xml, status, headers)


# Vercel serverless function entry point
def main(request):
    """Main entry point for Vercel"""
    return handler(request)


# Alternative entry points for different handler signatures
def do_GET(request):
    """Handle GET requests"""
    return handler(request)


def do_POST(request):
    """Handle POST requests - not allowed for RSS"""
    return {
        "statusCode": 405,
        "headers": {
            "Content-Type": "text/plain",
            "Allow": "GET, HEAD, OPTIONS"
        },
        "body": "Method Not Allowed"
    }


# For Vercel Python runtime (newer style)
def GET(request):
    """Vercel Python runtime GET handler"""
    return handler(request)


# For Vercel Python runtime (handler export)
def on_request(request):
    """Vercel Python runtime on_request handler"""
    return handler(request)


# Default export for Vercel
def default(request):
    """Default handler for Vercel"""
    return handler(request)


# Simple entry point - just return the feed
def app(request):
    """Simple app handler"""
    try:
        feed = generate_feed()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/rss+xml; charset=utf-8",
                "Access-Control-Allow-Origin": "*",
                "Cache-Control": "public, max-age=300"
            },
            "body": feed
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "text/plain"},
            "body": f"Error: {str(e)}"
        }
