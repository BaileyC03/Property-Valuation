#!/usr/bin/env python3
"""
Process HM Land Registry data for model training.
Downloads or uses existing CSV files and prepares training data.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import requests

def download_registry_data(year=2024):
    """Download HM Land Registry data for specific year."""
    url = f"https://publicdata.landregistry.org.uk/pp-{year}.csv"
    output_file = f"data/pp-{year}.csv"

    print(f"Downloading {year} data from Land Registry...")
    print(f"URL: {url}")
    print("(This may take several minutes - file is ~150-300 MB)")

    try:
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size:
                        percent = (downloaded / total_size * 100)
                        mb_downloaded = downloaded / 1e6
                        mb_total = total_size / 1e6
                        print(f"  {mb_downloaded:.1f} MB / {mb_total:.1f} MB ({percent:.1f}%)", end='\r')

        print(f"\n✓ Downloaded {year} data: {output_file}")
        return output_file
    except Exception as e:
        print(f"✗ Error downloading data: {e}")
        print("Alternative: Download manually from https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads")
        return None

def load_registry_csv(filepath, nrows=None, chunksize=50000):
    """Load HM Land Registry CSV file in chunks (memory-efficient for large files)."""
    print(f"Loading {filepath} in chunks...")
    try:
        # HM Land Registry CSV has no header, columns are fixed order:
        # 0: Transaction ID
        # 1: Price
        # 2: Date of Transfer
        # 3: Postcode
        # 4: Property Type
        # 5: Old/New
        # 6: Duration
        # 7: PAON
        # 8: SAON
        # 9: Street
        # 10: Locality
        # 11: Town/City
        # 12: District
        # 13: County
        # 14-15: Classification fields

        column_names = [
            'Transaction_ID', 'Price', 'Date_of_Transfer', 'Postcode', 'Property_Type',
            'Old_New', 'Duration', 'PAON', 'SAON', 'Street', 'Locality', 'Town_City',
            'District', 'County', 'Classification1', 'Classification2'
        ]

        chunks = []
        chunk_count = 0
        total_rows = 0

        for chunk in pd.read_csv(
            filepath,
            header=None,  # No header row in HM Land Registry format
            names=column_names,
            dtype={
                'Price': 'float64',
                'Postcode': 'str',
                'Property_Type': 'str',
                'Date_of_Transfer': 'str',
                'Town_City': 'str',
            },
            on_bad_lines='skip',
            chunksize=chunksize,
            quotechar='"'
        ):
            chunks.append(chunk)
            total_rows += len(chunk)
            chunk_count += 1

            # Limit total rows if specified
            if nrows and total_rows >= nrows:
                print(f"  Loaded {total_rows:,} rows (limit reached)")
                break

            # Show progress every 10 chunks
            if chunk_count % 10 == 0:
                print(f"  Loaded {total_rows:,} rows ({chunk_count} chunks)...")

        # Combine all chunks
        if chunks:
            df = pd.concat(chunks, ignore_index=True)
            print(f"✓ Loaded {len(df):,} records total")
            return df
        else:
            print(f"✗ No data loaded")
            return None

    except Exception as e:
        print(f"✗ Error loading CSV: {e}")
        import traceback
        traceback.print_exc()
        return None

def clean_data(df):
    """Clean and filter Land Registry data."""
    print("Cleaning data...")

    original_count = len(df)

    # Remove nulls (using correct column names for HM Land Registry format)
    df = df.dropna(subset=['Price', 'Postcode', 'Date_of_Transfer', 'Town_City'])

    # Filter price range (£50k - £5M)
    df = df[(df['Price'] >= 50000) & (df['Price'] <= 5000000)]

    # Remove duplicates
    df = df.drop_duplicates(subset=['Postcode', 'Price', 'Date_of_Transfer'], keep='first')

    # Filter recent transactions - try 10 years, then 20 years, then use all valid dates
    try:
        df['Date_of_Transfer'] = pd.to_datetime(df['Date_of_Transfer'], errors='coerce')
        # Remove rows with invalid dates
        df = df[df['Date_of_Transfer'].notna()]

        # Try 10-year filter first
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=10*365)
        df_filtered = df[df['Date_of_Transfer'] >= cutoff_date]

        # If 10-year filter removes too much, try 20 years
        if len(df_filtered) == 0:
            print("  Warning: 10-year filter removed all data, trying 20-year window...")
            cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=20*365)
            df_filtered = df[df['Date_of_Transfer'] >= cutoff_date]

        # If still nothing, use all valid dates
        if len(df_filtered) == 0:
            print("  Warning: 20-year filter also removed all data, using all available valid dates...")
            df = df
        else:
            df = df_filtered

    except Exception as e:
        print(f"  Warning: Date filtering error: {e}, keeping all data")

    removed = original_count - len(df)
    print(f"✓ Removed {removed:,} records, kept {len(df):,} valid records")

    return df

def geocode_postcode(postcode):
    """Get approximate latitude/longitude from postcode."""
    # Simplified postcode prefix to coordinates mapping
    # In production, use proper postcode database or API
    postcode_coords = {
        'SW1': (51.5033, -0.1276),  # London Westminster
        'EC1': (51.5190, -0.1026),  # London City
        'W1': (51.5155, -0.1520),   # London West End
        'E1': (51.5180, -0.0740),   # London East
        'N1': (51.5373, -0.1220),   # London North
        'SE1': (51.5042, -0.1037),  # London South
        'NW1': (51.5349, -0.1599),  # London Northwest
        'M1': (53.4808, -2.2426),   # Manchester
        'B1': (52.5095, -1.8848),   # Birmingham
        'L1': (53.4084, -2.9916),   # Liverpool
        'LS1': (53.8017, -1.5456),  # Leeds
        'S1': (53.3806, -1.4659),   # Sheffield
        'B': (52.5095, -1.8848),    # Birmingham (generic)
        'BN': (50.8625, -0.0833),   # Brighton
        'CB': (52.2044, 0.1235),    # Cambridge
        'EH1': (55.9533, -3.1883),  # Edinburgh
        'G1': (55.8625, -4.2588),   # Glasgow
        'CF1': (51.4825, -3.1660),  # Cardiff
        'M': (53.4808, -2.2426),    # Manchester (generic)
    }

    postcode_str = str(postcode).strip().upper()

    # Try exact prefix match
    for prefix, coords in postcode_coords.items():
        if postcode_str.startswith(prefix):
            lat = coords[0] + np.random.normal(0, 0.02)
            lon = coords[1] + np.random.normal(0, 0.02)
            return lat, lon

    # Default to UK center
    return 54.0, -2.0

def create_training_data(df, sample_size=None):
    """Convert Land Registry data to training format."""
    print("Creating training data...")

    if sample_size and len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)
        print(f"  Using sample of {sample_size} records")

    training_data = []

    for idx, row in df.iterrows():
        try:
            postcode = str(row['Postcode']).strip()
            price = float(row['Price'])
            property_type = str(row.get('Property_Type', 'D')).upper()
            town = str(row.get('Town_City', 'Unknown'))

            # Estimate bedrooms from property type
            # These are estimates - in production use actual bedroom data
            if property_type == 'D':
                beds = np.random.choice([3, 4, 5])
            elif property_type == 'S':
                beds = np.random.choice([2, 3])
            elif property_type == 'T':
                beds = np.random.choice([2, 3, 4])
            elif property_type == 'F':
                beds = np.random.choice([1, 2])
            else:
                beds = 3

            baths = max(1, int(beds / 2.5 + np.random.uniform(0, 1)))
            ensuite = min(baths - 1, max(0, int(np.random.uniform(0, min(2, baths - 1)))))
            detached = 1 if property_type == 'D' else 0

            # Get coordinates
            lat, lon = geocode_postcode(postcode)

            training_data.append({
                'postcode': postcode,
                'address': f"{town}, {postcode}",
                'beds': float(beds),
                'baths': float(baths),
                'ensuite': float(ensuite),
                'detached': float(detached),
                'lat': lat,
                'lon': lon,
                'price': price,
                'property_type': property_type
            })
        except Exception as e:
            continue

    print(f"✓ Created {len(training_data)} training samples")
    return pd.DataFrame(training_data)

def main():
    """Main processing pipeline."""
    print("=" * 70)
    print("HM Land Registry Data Processor")
    print("=" * 70)

    os.makedirs('data', exist_ok=True)

    # Check if data already exists
    existing_csv = None
    if os.path.exists('data/pp-complete.csv'):
        existing_csv = 'data/pp-complete.csv'
        print("✓ Found pp-complete.csv (your downloaded file)")
    elif os.path.exists('data/pp-2024.csv'):
        existing_csv = 'data/pp-2024.csv'
    elif os.path.exists('data/pp-2023.csv'):
        existing_csv = 'data/pp-2023.csv'

    # Step 1: Get data
    print("\n1️⃣  OBTAINING DATA")
    if existing_csv:
        print(f"Found existing data: {existing_csv}")
        csv_file = existing_csv
    else:
        print("No data file found. Attempting to download...")
        csv_file = download_registry_data(year=2024)

    if not csv_file or not os.path.exists(csv_file):
        print("⚠️  Could not obtain data file")
        print("Download manually from: https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads")
        print("Place file at: backend/data/pp-complete.csv")
        return

    # Step 2: Load and clean
    print("\n2️⃣  LOADING & CLEANING DATA")
    print("Loading records from your pp-complete.csv file (in chunks for large file)...")
    print("Note: 5GB file - loading strategically to avoid memory issues")

    # For a 5GB file, load first 1 million records (much faster and still plenty of data)
    # This keeps memory usage reasonable while giving excellent training data
    df_raw = load_registry_csv(csv_file, nrows=1000000, chunksize=50000)
    if df_raw is None:
        return

    df_clean = clean_data(df_raw)

    # Step 3: Create training data
    print("\n3️⃣  CREATING TRAINING DATA")
    # Use all cleaned data - should be ~200k-300k after cleaning
    df_training = create_training_data(df_clean, sample_size=None)

    if len(df_training) == 0:
        print("✗ No training data created")
        return

    # Step 4: Save
    print("\n4️⃣  SAVING DATA")
    output_file = 'land_registry_training.parquet'
    df_training.to_parquet(output_file)
    print(f"✓ Saved to {output_file}")

    # Display statistics
    print("\n📊 DATA STATISTICS:")
    print(f"  Total samples: {len(df_training)}")
    print(f"  Price range: £{df_training['price'].min():,.0f} - £{df_training['price'].max():,.0f}")
    print(f"  Avg price: £{df_training['price'].mean():,.0f}")
    print(f"  Avg bedrooms: {df_training['beds'].mean():.1f}")
    print(f"  Detached: {(df_training['detached'].sum() / len(df_training) * 100):.1f}%")

    print("\n✅ Data processing complete!")
    print("Next step: python ml/train_model_land_registry.py")

if __name__ == '__main__':
    main()
