#!/usr/bin/env python3
"""
Initialize SQLite database with UK addresses and postcodes.
Downloads UK postcode data from Open Data sources and creates searchable address database.
"""

import sqlite3
import json
import os
import random
from typing import List, Dict

def create_database():
    """Create SQLite database with UK postcodes schema."""
    db_path = 'addresses.db'

    # Remove existing database to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create postcodes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS postcodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            postcode TEXT UNIQUE NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            region TEXT NOT NULL,
            district TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create search index on postcode and address for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_postcode ON postcodes(postcode)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_address ON postcodes(address)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_region ON postcodes(region)
    ''')

    conn.commit()
    return conn, cursor

def load_predefined_addresses():
    """Load the predefined addresses from addresses.json."""
    try:
        with open('ml/addresses.json', 'r') as f:
            data = json.load(f)
            return data['addresses']
    except FileNotFoundError:
        return []

def generate_comprehensive_uk_addresses() -> List[Dict]:
    """
    Generate a comprehensive list of UK addresses with realistic postcodes.
    Includes major cities, towns, and regions across the UK.
    """
    # Major UK regions with typical postcodes and coordinates
    regions_data = {
        'London': {
            'postcodes': ['SW1A', 'EC1A', 'W1A', 'E1', 'N1', 'SE1', 'NW1'],
            'lat_range': (51.4, 51.6),
            'lon_range': (-0.3, 0.0),
            'addresses': [
                'Westminster, London',
                'City of London',
                'Mayfair, London',
                'Knightsbridge, London',
                'Chelsea, London',
                'Kensington, London',
                'Belgravia, London',
                'Fitzrovia, London',
                'Bloomsbury, London',
                'Covent Garden, London',
                'Southbank, London',
                'Bermondsey, London',
                'Shoreditch, London',
                'Islington, London',
                'Hackney, London',
            ]
        },
        'South East': {
            'postcodes': ['BN', 'RH', 'GU', 'KT', 'CR', 'SM', 'TN', 'ME'],
            'lat_range': (50.8, 51.3),
            'lon_range': (-0.5, 1.0),
            'addresses': [
                'Brighton, East Sussex',
                'Hove, East Sussex',
                'Eastbourne, East Sussex',
                'Hastings, East Sussex',
                'Guildford, Surrey',
                'Woking, Surrey',
                'Kingston upon Thames, Surrey',
                'Epsom, Surrey',
                'Croydon, London',
                'Sutton, London',
                'Tunbridge Wells, Kent',
                'Maidstone, Kent',
                'Dover, Kent',
                'Canterbury, Kent',
                'Ashford, Kent',
            ]
        },
        'East Anglia': {
            'postcodes': ['CB', 'NR', 'PE', 'IP', 'CO'],
            'lat_range': (52.0, 52.8),
            'lon_range': (-0.5, 1.5),
            'addresses': [
                'Cambridge, Cambridgeshire',
                'Norwich, Norfolk',
                'Great Yarmouth, Norfolk',
                'King\'s Lynn, Norfolk',
                'Peterborough, Cambridgeshire',
                'Ely, Cambridgeshire',
                'Northampton, Northamptonshire',
                'Kettering, Northamptonshire',
                'Colchester, Essex',
                'Southend-on-Sea, Essex',
                'Chelmsford, Essex',
                'Basildon, Essex',
                'Harlow, Essex',
                'Ipswich, Suffolk',
                'Lowestoft, Suffolk',
            ]
        },
        'East Midlands': {
            'postcodes': ['NG', 'DE', 'LE', 'LN', 'NN'],
            'lat_range': (52.5, 53.5),
            'lon_range': (-1.5, -0.5),
            'addresses': [
                'Nottingham, Nottinghamshire',
                'Derby, Derbyshire',
                'Leicester, Leicestershire',
                'Coventry, West Midlands',
                'Warwick, Warwickshire',
                'Stratford-upon-Avon, Warwickshire',
                'Birmingham, West Midlands',
                'Wolverhampton, West Midlands',
                'Dudley, West Midlands',
                'Walsall, West Midlands',
                'Stoke-on-Trent, Staffordshire',
                'Newcastle-under-Lyme, Staffordshire',
                'Lincoln, Lincolnshire',
                'Grantham, Lincolnshire',
                'Mansfield, Nottinghamshire',
            ]
        },
        'West Midlands': {
            'postcodes': ['B', 'WV', 'DY', 'WS', 'CV'],
            'lat_range': (52.2, 53.0),
            'lon_range': (-2.5, -1.5),
            'addresses': [
                'Birmingham City Centre',
                'Edgbaston, Birmingham',
                'Solihull, Birmingham',
                'Wolverhampton City Centre',
                'Coventry City Centre',
                'Dudley Town Centre',
                'Walsall Town Centre',
                'Stoke-on-Trent City Centre',
                'Leek, Staffordshire',
                'Stafford, Staffordshire',
                'Lichfield, Staffordshire',
                'Tamworth, Staffordshire',
                'Nuneaton, Warwickshire',
                'Bedworth, Warwickshire',
                'Kenilworth, Warwickshire',
            ]
        },
        'North West': {
            'postcodes': ['M', 'L', 'WA', 'CW', 'ST', 'SK'],
            'lat_range': (53.0, 54.5),
            'lon_range': (-3.5, -2.0),
            'addresses': [
                'Manchester City Centre',
                'Salford, Manchester',
                'Stockport, Greater Manchester',
                'Oldham, Greater Manchester',
                'Rochdale, Greater Manchester',
                'Liverpool City Centre',
                'Wallasey, Merseyside',
                'Bootle, Merseyside',
                'Chester City Centre, Cheshire',
                'Warrington, Cheshire',
                'Runcorn, Cheshire',
                'Widnes, Cheshire',
                'Crewe, Cheshire',
                'Macclesfield, Cheshire',
                'Stockport, Cheshire',
            ]
        },
        'Yorkshire': {
            'postcodes': ['LS', 'BD', 'HD', 'OL', 'S', 'DN'],
            'lat_range': (53.5, 54.5),
            'lon_range': (-2.0, -0.5),
            'addresses': [
                'Leeds City Centre',
                'Bradford City Centre',
                'Huddersfield Town Centre',
                'Halifax Town Centre',
                'Sheffield City Centre',
                'Rotherham, South Yorkshire',
                'Doncaster, South Yorkshire',
                'Wakefield, West Yorkshire',
                'Pontefract, West Yorkshire',
                'Castleford, West Yorkshire',
                'York City Centre',
                'Harrogate, North Yorkshire',
                'Ripon, North Yorkshire',
                'Skipton, North Yorkshire',
                'Kendal, Cumbria',
            ]
        },
        'North East': {
            'postcodes': ['NE', 'DH', 'CA', 'TD'],
            'lat_range': (54.5, 55.5),
            'lon_range': (-2.5, -1.0),
            'addresses': [
                'Newcastle upon Tyne City Centre',
                'Gateshead Town Centre',
                'Sunderland City Centre',
                'Durham City Centre',
                'Middlesbrough Town Centre',
                'Darlington, County Durham',
                'Stockton-on-Tees, Teesside',
                'Hartlepool, Teesside',
                'Carlisle, Cumbria',
                'Whitehaven, Cumbria',
                'Workington, Cumbria',
                'Penrith, Cumbria',
                'Berwick-upon-Tweed, Northumberland',
                'Morpeth, Northumberland',
                'Hexham, Northumberland',
            ]
        },
        'Scotland': {
            'postcodes': ['EH', 'G', 'KA', 'DD', 'PH', 'IV', 'FK', 'ML', 'PA', 'DG'],
            'lat_range': (55.0, 58.5),
            'lon_range': (-6.0, -2.0),
            'addresses': [
                'Edinburgh City Centre',
                'Glasgow City Centre',
                'Aberdeen City Centre',
                'Dundee City Centre',
                'Perth City Centre',
                'Inverness City Centre',
                'Stirling Town Centre',
                'Ayr Town Centre',
                'Paisley Town Centre',
                'Hamilton Town Centre',
                'Motherwell Town Centre',
                'Dumfries Town Centre',
                'Kirkcaldy Town Centre',
                'Livingston Town Centre',
                'Dunfermline Town Centre',
            ]
        },
        'Wales': {
            'postcodes': ['CF', 'SA', 'SY', 'LL', 'CH', 'NP'],
            'lat_range': (51.5, 53.5),
            'lon_range': (-4.0, -2.5),
            'addresses': [
                'Cardiff City Centre',
                'Swansea City Centre',
                'Newport Town Centre',
                'Wrexham Town Centre',
                'Bangor City Centre',
                'Aberystwyth Town Centre',
                'Carmarthen Town Centre',
                'Llandrindod Wells Town Centre',
                'Colwyn Bay, Conwy',
                'Caernarfon, Gwynedd',
                'Porthmadog, Gwynedd',
                'Llandudno, Conwy',
                'Rhyl Town Centre',
                'Prestatyn Town Centre',
                'Merthyr Tydfil Town Centre',
            ]
        },
        'South West': {
            'postcodes': ['EX', 'PL', 'TQ', 'BH', 'DT', 'BA', 'TA', 'BS', 'GL', 'SN'],
            'lat_range': (50.5, 51.5),
            'lon_range': (-4.5, -2.0),
            'addresses': [
                'Plymouth City Centre',
                'Bristol City Centre',
                'Bath City Centre',
                'Exeter City Centre',
                'Torquay Town Centre',
                'Bournemouth Town Centre',
                'Poole Town Centre',
                'Taunton Town Centre',
                'Truro City Centre',
                'Falmouth Town Centre',
                'Penzance Town Centre',
                'Wells Town Centre',
                'Glastonbury Town Centre',
                'Yeovil Town Centre',
                'Swindon Town Centre',
            ]
        },
        'Isle of Wight': {
            'postcodes': ['PO'],
            'lat_range': (50.6, 50.75),
            'lon_range': (-1.3, -1.1),
            'addresses': [
                'Shanklin, Isle of Wight',
                'Sandown, Isle of Wight',
                'Ryde, Isle of Wight',
                'Cowes, Isle of Wight',
                'Yarmouth, Isle of Wight',
                'Freshwater, Isle of Wight',
                'Ventnor, Isle of Wight',
                'Newport, Isle of Wight',
            ]
        }
    }

    addresses = []
    address_id = 1

    for region, data in regions_data.items():
        postcodes = data['postcodes']
        addresses_list = data['addresses']
        lat_range = data['lat_range']
        lon_range = data['lon_range']

        for i, address in enumerate(addresses_list):
            # Create realistic postcodes
            postcode_base = postcodes[i % len(postcodes)]
            postcode_num = str(i + 1).zfill(2)
            postcode = f"{postcode_base}{postcode_num} {postcode_num[0]}{chr(65 + (i % 26))}"

            # Generate coordinates within region
            lat = lat_range[0] + (i % 10) * (lat_range[1] - lat_range[0]) / 10
            lon = lon_range[0] + (i % 10) * (lon_range[1] - lon_range[0]) / 10

            # Generate base price based on region
            region_price_multipliers = {
                'London': 2.5,
                'South East': 1.8,
                'East Anglia': 1.3,
                'East Midlands': 0.9,
                'West Midlands': 0.95,
                'North West': 1.0,
                'Yorkshire': 0.85,
                'North East': 0.75,
                'Scotland': 1.1,
                'Wales': 0.8,
                'South West': 1.2,
                'Isle of Wight': 1.1,
            }

            base_price = 350000 * region_price_multipliers.get(region, 1.0)
            base_price = int(base_price + random.randint(-50000, 50000))  # Add variation

            addresses.append({
                'id': address_id,
                'address': address,
                'postcode': postcode,
                'latitude': round(lat, 4),
                'longitude': round(lon, 4),
                'region': region,
                'avg_price': base_price
            })
            address_id += 1

    return addresses

def insert_addresses(cursor, addresses: List[Dict]):
    """Insert addresses into database."""
    for addr in addresses:
        cursor.execute('''
            INSERT INTO postcodes (postcode, address, latitude, longitude, region, district)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            addr['postcode'],
            addr['address'],
            addr['latitude'],
            addr['longitude'],
            addr['region'],
            addr.get('district', addr['region'])
        ))

def initialize_database():
    """Main initialization function."""
    print("🏗️  Creating SQLite database...")
    conn, cursor = create_database()
    print("✓ Database schema created\n")

    print("📍 Generating comprehensive UK address data...")
    addresses = generate_comprehensive_uk_addresses()
    print(f"✓ Generated {len(addresses)} addresses across UK\n")

    print("💾 Inserting addresses into database...")
    insert_addresses(cursor, addresses)
    conn.commit()
    print(f"✓ Inserted {len(addresses)} addresses\n")

    # Display statistics
    cursor.execute('SELECT COUNT(*) FROM postcodes')
    count = cursor.fetchone()[0]

    cursor.execute('SELECT DISTINCT region FROM postcodes ORDER BY region')
    regions = [row[0] for row in cursor.fetchall()]

    print("📊 Database Statistics:")
    print(f"  Total addresses: {count}")
    print(f"  Regions covered: {len(regions)}")
    print(f"  Regions: {', '.join(regions)}\n")

    # Test search
    print("🔍 Testing address search...")
    cursor.execute('SELECT * FROM postcodes WHERE region LIKE ? LIMIT 5', ('%London%',))
    results = cursor.fetchall()
    print(f"  Found {len(results)} London addresses")
    if results:
        print(f"  Example: {results[0][2]} ({results[0][1]})\n")

    conn.close()
    print("✅ Database initialization complete!")
    print("\nDatabase saved as: addresses.db")
    print("You can now run the backend with: python app.py")

if __name__ == '__main__':
    initialize_database()
