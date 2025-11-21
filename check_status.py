#!/usr/bin/env python3
"""Quick status check for Microsoft Login Counter."""
import os
import sqlite3
from datetime import datetime, timezone, timedelta

# Database path
db_path = os.path.expanduser('~/.microsoft-login-counter/events.db')

if not os.path.exists(db_path):
    print("❌ Database not found. Has the proxy been started?")
    exit(1)

# Connect and query
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Total count
cursor.execute("SELECT COUNT(*) FROM login_events")
total = cursor.fetchone()[0]

print("=" * 60)
print("Microsoft Login Counter - Status")
print("=" * 60)
print(f"Total logins detected: {total}")

if total > 0:
    # Get latest event
    cursor.execute("""
        SELECT timestamp, detected_via
        FROM login_events
        ORDER BY unix_timestamp DESC
        LIMIT 1
    """)
    latest = cursor.fetchone()
    print(f"Latest login: {latest[0]} (detected via: {latest[1]})")

    # Get today's count
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_ts = int(today_start.timestamp())

    cursor.execute("""
        SELECT COUNT(*) FROM login_events
        WHERE unix_timestamp >= ?
    """, (today_ts,))
    today_count = cursor.fetchone()[0]
    print(f"Logins today: {today_count}")

    print("\nRecent logins:")
    cursor.execute("""
        SELECT id, timestamp, detected_via
        FROM login_events
        ORDER BY unix_timestamp DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  [{row[0]}] {row[1]} - {row[2]}")
else:
    print("\n⚠️  No logins detected yet.")
    print("\nTroubleshooting:")
    print("1. Is the proxy running? (python main.py)")
    print("2. Is your browser configured to use the proxy (localhost:8080)?")
    print("3. Have you tried logging into a Microsoft service?")
    print("   - Try: https://outlook.office.com")
    print("   - Try: https://portal.azure.com")
    print("   - Try: https://www.office.com")

print("=" * 60)

conn.close()
