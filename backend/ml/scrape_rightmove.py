#!/usr/bin/env python3
"""
Scrape Rightmove house prices for Widley area.
Pages 1-40, with detail pages for beds/baths/coords/transaction history.
"""

import os
import json
import time
import re
import csv
import requests

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-GB,en;q=0.9',
}

BASE_URL = "https://www.rightmove.co.uk/house-prices/widley.html?pageNumber={}"
DETAIL_URL = "https://www.rightmove.co.uk/house-prices/details/{}"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'rightmove_widley.csv')


def scrape_detail_page(uuid, session):
    """Scrape detail page for property info + all transactions."""
    url = DETAIL_URL.format(uuid)
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None

        html = resp.text
        result = {'uuid': uuid, 'transactions': []}

        # Address from h1 tag
        h1 = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        if h1:
            result['address'] = h1.group(1).strip()

        # React stream data uses single-backslash escaped quotes: \"key\",\"value\"
        # Property type (mixed case like "Semi-detached", "Detached", "Terraced")
        pt = re.search(r'propertyType\\",\\"([^"\\]+)\\"', html)
        if pt:
            result['property_type'] = pt.group(1)

        # Bedrooms & bathrooms
        bed = re.search(r'bedrooms\\",(\\d+)', html)
        if not bed:
            bed = re.search(r'bedrooms\\",(\d+)', html)
        if bed:
            result['bedrooms'] = int(bed.group(1))

        bath = re.search(r'bathrooms\\",(\d+)', html)
        if bath:
            result['bathrooms'] = int(bath.group(1))

        # Lat/lon from map URL parameter
        lat = re.search(r'latitude=([\d.\-]+)', html)
        lon = re.search(r'longitude=([\d.\-]+)', html)
        if lat and lon:
            result['lat'] = float(lat.group(1))
            result['lon'] = float(lon.group(1))

        # Postcode from address
        if 'address' in result:
            pc = re.search(r'([A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2})', result['address'])
            if pc:
                result['postcode'] = pc.group(1)

        # Transactions: two patterns
        # 1) First/main transaction: \"price\",NNNNN,\"deedDate\",\"YYYY-MM-DD\"
        first = re.search(r'"price\\",(\d+),\\"deedDate\\",\\"(\d{4}-\d{2}-\d{2})\\"', html)
        if first:
            result['transactions'].append({
                'price': int(first.group(1)),
                'date': first.group(2),
            })

        # 2) Subsequent transactions: \"£XXX,XXX\",NNNNN,\"YYYY-MM-DD\"
        for m in re.finditer(r'\\"£[\d,]+\\",([\d]+),\\"(\d{4}-\d{2}-\d{2})\\"', html):
            price = int(m.group(1))
            date = m.group(2)
            if not any(t['price'] == price and t['date'] == date for t in result['transactions']):
                result['transactions'].append({'price': price, 'date': date})

        return result

    except Exception as e:
        print(f"  Error scraping {uuid}: {e}")
        return None


def scrape_listing_page(page_num, session):
    """Get property UUIDs from a listing page."""
    url = BASE_URL.format(page_num)
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"  Page {page_num}: HTTP {resp.status_code}")
            return []
        return list(set(re.findall(r'/house-prices/details/([0-9a-f\-]{36})', resp.text)))
    except Exception as e:
        print(f"  Page {page_num} error: {e}")
        return []


def main():
    print("=" * 60)
    print("Rightmove Widley Property Scraper")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    session = requests.Session()

    # Step 1: Collect UUIDs
    print("\n1. Collecting property links from pages 1-40...")
    all_uuids = []

    for page in range(1, 41):
        uuids = scrape_listing_page(page, session)
        new = [u for u in uuids if u not in all_uuids]
        all_uuids.extend(new)
        print(f"  Page {page:2d}: {len(uuids)} links ({len(new)} new) | Total: {len(all_uuids)}")
        time.sleep(1.0)

    print(f"\nTotal unique properties: {len(all_uuids)}")
    if not all_uuids:
        print("No properties found!")
        return

    # Step 2: Scrape detail pages
    print(f"\n2. Scraping {len(all_uuids)} detail pages...")
    all_properties = []
    failed = 0

    for i, uuid in enumerate(all_uuids):
        if (i + 1) % 25 == 0 or i == 0:
            print(f"  Progress: {i + 1}/{len(all_uuids)} ({len(all_properties)} ok, {failed} fail)")

        prop = scrape_detail_page(uuid, session)
        if prop and prop.get('transactions') and prop.get('bedrooms') is not None:
            all_properties.append(prop)
        else:
            failed += 1
            if prop:
                missing = []
                if not prop.get('transactions'): missing.append('transactions')
                if prop.get('bedrooms') is None: missing.append('bedrooms')
                # Don't print every failure, just track count

        time.sleep(0.8)

    print(f"\nScraped: {len(all_properties)} properties ({failed} failed)")

    # Step 3: Save CSV (one row per transaction)
    print(f"\n3. Saving to {OUTPUT_FILE}...")

    rows = []
    for prop in all_properties:
        for tx in prop['transactions']:
            rows.append({
                'address': prop.get('address', ''),
                'postcode': prop.get('postcode', ''),
                'property_type': prop.get('property_type', ''),
                'bedrooms': prop.get('bedrooms', 0),
                'bathrooms': prop.get('bathrooms', 0),
                'lat': prop.get('lat', 0),
                'lon': prop.get('lon', 0),
                'price': tx['price'],
                'date_sold': tx['date'],
            })

    if not rows:
        print("No data to save!")
        return

    fieldnames = ['address', 'postcode', 'property_type', 'bedrooms',
                  'bathrooms', 'lat', 'lon', 'price', 'date_sold']

    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    prices = [r['price'] for r in rows]
    beds = [r['bedrooms'] for r in rows if r['bedrooms'] > 0]
    print(f"Saved {len(rows)} transactions from {len(all_properties)} properties")
    print(f"\nStats:")
    print(f"  Price range: £{min(prices):,} - £{max(prices):,}")
    print(f"  Average: £{sum(prices) // len(prices):,}")
    print(f"  Bedroom range: {min(beds)}-{max(beds)}")

    json_file = os.path.join(OUTPUT_DIR, 'rightmove_widley.json')
    with open(json_file, 'w') as f:
        json.dump(all_properties, f, indent=2)
    print(f"  JSON: {json_file}")
    print("\nDone! Next: python ml/train_widley.py")


if __name__ == '__main__':
    main()
