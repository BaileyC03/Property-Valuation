#!/usr/bin/env python3
"""
Reprocess HM Land Registry data with 3% annual inflation adjustment.
All prices are adjusted to 2026 equivalent values.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# Change to backend directory
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

ANNUAL_INFLATION = 0.03  # 3% per year
TARGET_YEAR = 2026
RAW_CSV = 'data/pp-complete.csv'
OUTPUT_FILE = 'land_registry_training.parquet'

def load_registry_csv(filepath, nrows=None, chunksize=50000):
    """Load HM Land Registry CSV file in chunks."""
    print(f"Loading {filepath} in chunks...")

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
        header=None,
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

        if nrows and total_rows >= nrows:
            print(f"  Loaded {total_rows:,} rows (limit reached)")
            break

        if chunk_count % 10 == 0:
            print(f"  Loaded {total_rows:,} rows ({chunk_count} chunks)...")

    if chunks:
        df = pd.concat(chunks, ignore_index=True)
        print(f"  Loaded {len(df):,} records total")
        return df
    return None


def geocode_postcode(postcode):
    """Get approximate latitude/longitude from postcode prefix."""
    postcode_coords = {
        # London - detailed
        'SW1A': (51.5014, -0.1419), 'SW1B': (51.4984, -0.1421), 'SW1E': (51.4966, -0.1393),
        'SW1H': (51.4975, -0.1323), 'SW1P': (51.4941, -0.1291), 'SW1V': (51.4914, -0.1443),
        'SW1W': (51.4917, -0.1507), 'SW1X': (51.4970, -0.1557), 'SW1Y': (51.5070, -0.1365),
        'SW3': (51.4883, -0.1708), 'SW4': (51.4626, -0.1454), 'SW5': (51.4896, -0.1911),
        'SW6': (51.4726, -0.1994), 'SW7': (51.4946, -0.1743), 'SW8': (51.4787, -0.1214),
        'SW9': (51.4635, -0.1134), 'SW10': (51.4826, -0.1840),
        'SW11': (51.4647, -0.1651), 'SW12': (51.4441, -0.1488), 'SW13': (51.4725, -0.2408),
        'SW14': (51.4656, -0.2676), 'SW15': (51.4531, -0.2306), 'SW16': (51.4169, -0.1294),
        'SW17': (51.4297, -0.1632), 'SW18': (51.4502, -0.1870), 'SW19': (51.4175, -0.2014),
        'SW20': (51.4117, -0.2293),
        'W1': (51.5148, -0.1499), 'W2': (51.5113, -0.1840), 'W3': (51.5041, -0.2604),
        'W4': (51.4882, -0.2604), 'W5': (51.5108, -0.3013), 'W6': (51.4885, -0.2254),
        'W7': (51.5112, -0.3282), 'W8': (51.5013, -0.1929), 'W9': (51.5239, -0.1898),
        'W10': (51.5228, -0.2094), 'W11': (51.5134, -0.2028), 'W12': (51.5050, -0.2358),
        'W13': (51.5141, -0.3196), 'W14': (51.4944, -0.2099),
        'WC1': (51.5230, -0.1195), 'WC2': (51.5116, -0.1230),
        'EC1': (51.5230, -0.1065), 'EC2': (51.5187, -0.0837), 'EC3': (51.5118, -0.0800),
        'EC4': (51.5139, -0.1010),
        'E1': (51.5148, -0.0553), 'E2': (51.5280, -0.0667), 'E3': (51.5272, -0.0280),
        'E4': (51.6256, -0.0084), 'E5': (51.5553, -0.0489), 'E6': (51.5241, 0.0457),
        'E7': (51.5540, 0.0293), 'E8': (51.5410, -0.0594), 'E9': (51.5440, -0.0420),
        'E10': (51.5635, -0.0152), 'E11': (51.5699, 0.0068), 'E12': (51.5524, 0.0540),
        'E13': (51.5230, 0.0287), 'E14': (51.5065, -0.0207), 'E15': (51.5392, 0.0030),
        'E16': (51.5094, 0.0254), 'E17': (51.5849, -0.0254), 'E18': (51.5944, 0.0181),
        'N1': (51.5373, -0.1080), 'N2': (51.5869, -0.1693), 'N3': (51.6131, -0.1841),
        'N4': (51.5679, -0.1037), 'N5': (51.5538, -0.0930), 'N6': (51.5713, -0.1461),
        'N7': (51.5501, -0.1176), 'N8': (51.5800, -0.1128), 'N9': (51.6271, -0.0623),
        'N10': (51.5963, -0.1413), 'N11': (51.6104, -0.1294), 'N12': (51.6131, -0.1748),
        'N13': (51.6230, -0.1100), 'N14': (51.6385, -0.1232), 'N15': (51.5808, -0.0808),
        'N16': (51.5606, -0.0751), 'N17': (51.5989, -0.0682), 'N18': (51.6178, -0.0722),
        'N19': (51.5644, -0.1289), 'N20': (51.6220, -0.1711), 'N21': (51.6370, -0.0910),
        'N22': (51.5982, -0.1088),
        'NW1': (51.5302, -0.1437), 'NW2': (51.5571, -0.2116), 'NW3': (51.5475, -0.1729),
        'NW4': (51.5826, -0.2265), 'NW5': (51.5509, -0.1415), 'NW6': (51.5418, -0.1935),
        'NW7': (51.6172, -0.2301), 'NW8': (51.5311, -0.1710), 'NW9': (51.5827, -0.2604),
        'NW10': (51.5383, -0.2336), 'NW11': (51.5773, -0.1896),
        'SE1': (51.5042, -0.1037), 'SE2': (51.4799, 0.1050), 'SE3': (51.4605, 0.0100),
        'SE4': (51.4572, -0.0416), 'SE5': (51.4753, -0.0900), 'SE6': (51.4477, -0.0198),
        'SE7': (51.4783, 0.0397), 'SE8': (51.4747, -0.0299), 'SE9': (51.4463, 0.0660),
        'SE10': (51.4832, 0.0035), 'SE11': (51.4929, -0.1061), 'SE12': (51.4476, 0.0358),
        'SE13': (51.4549, -0.0125), 'SE14': (51.4747, -0.0419), 'SE15': (51.4696, -0.0639),
        'SE16': (51.5000, -0.0500), 'SE17': (51.4886, -0.0944), 'SE18': (51.4656, 0.0725),
        'SE19': (51.4157, -0.0814), 'SE20': (51.4109, -0.0545), 'SE21': (51.4350, -0.0850),
        'SE22': (51.4529, -0.0719), 'SE23': (51.4366, -0.0552), 'SE24': (51.4517, -0.1023),
        'SE25': (51.3973, -0.0738), 'SE26': (51.4263, -0.0491), 'SE27': (51.4320, -0.1028),
        'SE28': (51.4928, 0.1040),
        # Major cities
        'M1': (53.4808, -2.2426), 'M2': (53.4794, -2.2453), 'M3': (53.4830, -2.2573),
        'M4': (53.4820, -2.2354), 'M5': (53.4872, -2.2856),
        'M': (53.4808, -2.2426),
        'B1': (52.4796, -1.9026), 'B2': (52.4755, -1.8986), 'B3': (52.4862, -1.8982),
        'B4': (52.4830, -1.8899), 'B5': (52.4737, -1.8920),
        'B': (52.4862, -1.8904),
        'L1': (53.4084, -2.9916), 'L2': (53.4041, -2.9855), 'L3': (53.4100, -2.9810),
        'L': (53.4084, -2.9916),
        'LS': (53.7997, -1.5492), 'S': (53.3811, -1.4701),
        'CF': (51.4837, -3.1681), 'EH': (55.9533, -3.1883), 'G': (55.8642, -4.2518),
        'BS': (51.4545, -2.5879), 'BA': (51.3813, -2.3594),
        'OX': (51.7520, -1.2577), 'RG': (51.4543, -0.9781), 'SL': (51.5085, -0.5950),
        'HP': (51.7575, -0.7419), 'AL': (51.7538, -0.3395), 'SG': (51.9004, -0.1971),
        'LU': (51.8787, -0.4200), 'MK': (52.0406, -0.7594),
        'NG': (52.9548, -1.1581), 'DE': (52.9225, -1.4746), 'LE': (52.6369, -1.1398),
        'CV': (52.4082, -1.5108), 'WV': (52.5862, -2.1272), 'DY': (52.5113, -2.0874),
        'WS': (52.5858, -1.9824), 'ST': (53.0027, -2.1794),
        'LN': (53.2307, -0.5406), 'PE': (52.5736, -0.2408), 'NN': (52.2405, -0.9027),
        'BD': (53.7959, -1.7594), 'HD': (53.6459, -1.7850), 'HX': (53.7215, -1.8633),
        'WF': (53.6826, -1.4997), 'HU': (53.7457, -0.3367), 'DN': (53.5228, -1.1282),
        'YO': (53.9600, -1.0873), 'HG': (53.9939, -1.5377),
        'NE': (54.9783, -1.6178), 'DH': (54.7753, -1.5849), 'SR': (54.9058, -1.3816),
        'TS': (54.5742, -1.2349), 'DL': (54.5271, -1.5526), 'CA': (54.8951, -2.9382),
        'LA': (54.0500, -2.8000),
        'BN': (50.8225, -0.1372), 'PO': (50.7989, -1.0913), 'SO': (50.9097, -1.4044),
        'GU': (51.2362, -0.5704), 'KT': (51.4100, -0.3020), 'CR': (51.3762, -0.0982),
        'SM': (51.3618, -0.1945), 'TW': (51.4494, -0.3260),
        'RH': (51.1732, -0.1879), 'TN': (51.1328, 0.2637), 'ME': (51.2717, 0.5268),
        'CT': (51.2802, 1.0789), 'DA': (51.4441, 0.2182),
        'CB': (52.2053, 0.1218), 'NR': (52.6309, 1.2974), 'IP': (52.0567, 1.1482),
        'CO': (51.8959, 0.8919), 'CM': (51.7356, 0.4685), 'SS': (51.5462, 0.7077),
        'RM': (51.5726, 0.1748), 'IG': (51.5582, 0.0731),
        'CH': (53.1914, -2.8920), 'WA': (53.3900, -2.5970), 'CW': (53.0996, -2.4414),
        'SK': (53.4083, -2.1494), 'OL': (53.5409, -2.1114), 'BL': (53.5813, -2.4340),
        'WN': (53.5555, -2.6323), 'PR': (53.7590, -2.6988), 'FY': (53.8175, -3.0353),
        'BB': (53.7581, -2.4824),
        'EX': (50.7236, -3.5275), 'PL': (50.3755, -4.1427), 'TQ': (50.4619, -3.5251),
        'TR': (50.2632, -5.0510), 'BH': (50.7192, -1.8808), 'DT': (50.7134, -2.4380),
        'SP': (51.0682, -1.7954), 'SN': (51.5604, -1.7800), 'GL': (51.8649, -2.2448),
        'TA': (51.0159, -3.1006), 'WR': (52.1936, -2.2217),
        'SA': (51.6214, -3.9441), 'NP': (51.5841, -2.9977), 'LL': (53.2271, -4.1281),
        'SY': (52.7078, -3.0764), 'LD': (52.2422, -3.3793),
        'AB': (57.1497, -2.0943), 'DD': (56.4620, -2.9707), 'FK': (56.1165, -3.9369),
        'KY': (56.1128, -3.1636), 'PH': (56.3950, -3.4313), 'IV': (57.4778, -4.2247),
        'PA': (55.8455, -4.4234), 'KA': (55.4628, -4.6288), 'ML': (55.7905, -3.9910),
        'DG': (55.0752, -3.6040), 'TD': (55.7704, -2.0050),
        'EN': (51.6527, -0.0762), 'HA': (51.5790, -0.3337), 'UB': (51.5470, -0.4447),
        'BR': (51.4056, 0.0177), 'WD': (51.6575, -0.3959),
    }

    postcode_str = str(postcode).strip().upper().replace(' ', '')

    # Try progressively shorter prefixes for best match
    for prefix_len in range(min(4, len(postcode_str)), 0, -1):
        prefix = postcode_str[:prefix_len]
        if prefix in postcode_coords:
            lat, lon = postcode_coords[prefix]
            # Add small random jitter for same-prefix variation
            lat += np.random.normal(0, 0.005)
            lon += np.random.normal(0, 0.005)
            return lat, lon

    # Default to UK center with more jitter
    return 54.0 + np.random.normal(0, 0.5), -2.0 + np.random.normal(0, 0.5)


def apply_inflation(price, transaction_date, target_year=TARGET_YEAR, annual_rate=ANNUAL_INFLATION):
    """
    Adjust a historical price to target_year equivalent using compound inflation.
    price_2026 = price_original * (1 + rate) ^ years_since
    """
    try:
        if pd.isna(transaction_date):
            return price
        years_since = target_year - transaction_date.year + (target_year - transaction_date.month / 12.0)
        # More accurate: use fractional years
        days_since = (pd.Timestamp(f'{target_year}-01-01') - transaction_date).days
        years_since = max(0, days_since / 365.25)
        adjusted = price * ((1 + annual_rate) ** years_since)
        return adjusted
    except:
        return price


def main():
    print("=" * 70)
    print("HM Land Registry Data Processor - WITH INFLATION ADJUSTMENT")
    print(f"  Annual inflation rate: {ANNUAL_INFLATION*100:.0f}%")
    print(f"  Target year: {TARGET_YEAR}")
    print("=" * 70)

    if not os.path.exists(RAW_CSV):
        print(f"Error: {RAW_CSV} not found")
        return

    # Step 1: Load raw CSV
    print("\n1. LOADING RAW DATA")
    df = load_registry_csv(RAW_CSV, nrows=1000000, chunksize=50000)
    if df is None:
        return

    # Step 2: Clean
    print("\n2. CLEANING DATA")
    original_count = len(df)
    df = df.dropna(subset=['Price', 'Postcode', 'Date_of_Transfer', 'Town_City'])
    df = df[(df['Price'] >= 50000) & (df['Price'] <= 10000000)]  # Raised upper limit to £10M
    df = df.drop_duplicates(subset=['Postcode', 'Price', 'Date_of_Transfer'], keep='first')

    # Parse dates
    df['Date_of_Transfer'] = pd.to_datetime(df['Date_of_Transfer'], errors='coerce')
    df = df[df['Date_of_Transfer'].notna()]

    print(f"  After cleaning: {len(df):,} records (removed {original_count - len(df):,})")

    # Show date distribution
    print(f"\n  Date range: {df['Date_of_Transfer'].min().strftime('%Y-%m')} to {df['Date_of_Transfer'].max().strftime('%Y-%m')}")
    print(f"  Year distribution:")
    year_counts = df['Date_of_Transfer'].dt.year.value_counts().sort_index()
    for year, count in year_counts.items():
        bar = "█" * int(count / year_counts.max() * 30)
        print(f"    {year}: {bar} {count:,}")

    # Step 3: Apply inflation
    print("\n3. APPLYING INFLATION ADJUSTMENT")
    print(f"   Formula: price_2026 = price_original * (1.03)^years_since_transaction")

    df['price_original'] = df['Price'].copy()
    df['Price'] = df.apply(
        lambda row: apply_inflation(row['Price'], row['Date_of_Transfer']),
        axis=1
    )

    # Show inflation impact
    print(f"\n   Price impact examples:")
    samples = df.sample(5, random_state=42)
    for _, row in samples.iterrows():
        year = row['Date_of_Transfer'].year
        orig = row['price_original']
        adj = row['Price']
        pct = (adj / orig - 1) * 100
        print(f"     {year} sale: £{orig:,.0f} → £{adj:,.0f} (+{pct:.0f}%)")

    print(f"\n   Overall impact:")
    print(f"     Original mean:  £{df['price_original'].mean():,.0f}")
    print(f"     Adjusted mean:  £{df['Price'].mean():,.0f}")
    print(f"     Original median: £{df['price_original'].median():,.0f}")
    print(f"     Adjusted median: £{df['Price'].median():,.0f}")

    # Step 4: Create training data
    print("\n4. CREATING TRAINING DATA WITH BETTER FEATURES")

    training_data = []
    for idx, row in df.iterrows():
        try:
            postcode = str(row['Postcode']).strip()
            price = float(row['Price'])
            property_type = str(row.get('Property_Type', 'D')).upper()
            town = str(row.get('Town_City', 'Unknown'))

            # Estimate bedrooms from property type
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

            # Get coordinates from improved postcode mapping
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
        except:
            continue

    df_training = pd.DataFrame(training_data)
    print(f"  Created {len(df_training):,} training samples")

    # Step 5: Save
    print("\n5. SAVING")
    df_training.to_parquet(OUTPUT_FILE)
    print(f"  Saved to {OUTPUT_FILE}")

    # Final statistics
    print(f"\n{'='*70}")
    print("FINAL STATISTICS (2026-adjusted prices)")
    print(f"{'='*70}")
    print(f"  Total samples:  {len(df_training):,}")
    print(f"  Price range:    £{df_training['price'].min():,.0f} - £{df_training['price'].max():,.0f}")
    print(f"  Mean price:     £{df_training['price'].mean():,.0f}")
    print(f"  Median price:   £{df_training['price'].median():,.0f}")
    print(f"  Avg bedrooms:   {df_training['beds'].mean():.1f}")
    print(f"  Detached:       {(df_training['detached'].sum() / len(df_training) * 100):.1f}%")

    print(f"\n  Property type distribution:")
    for pt, count in df_training['property_type'].value_counts().items():
        pct = count / len(df_training) * 100
        avg_p = df_training[df_training['property_type']==pt]['price'].mean()
        print(f"    {pt}: {count:,} ({pct:.1f}%) avg £{avg_p:,.0f}")

    print(f"\n  Next step: python ml/train_lightgbm_with_plot.py")
    print(f"  Done!")


if __name__ == '__main__':
    main()
