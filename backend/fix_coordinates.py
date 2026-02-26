#!/usr/bin/env python3
"""Fix addresses.db with accurate UK coordinates."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'addresses.db')

# Real coordinates for all 173 addresses (lat, lon)
REAL_COORDS = {
    # London
    'Westminster, London':              (51.4975, -0.1357),
    'City of London':                   (51.5155, -0.0922),
    'Mayfair, London':                  (51.5116, -0.1488),
    'Knightsbridge, London':            (51.4994, -0.1607),
    'Chelsea, London':                  (51.4875, -0.1687),
    'Kensington, London':               (51.4991, -0.1938),
    'Belgravia, London':                (51.4963, -0.1477),
    'Fitzrovia, London':                (51.5183, -0.1362),
    'Bloomsbury, London':               (51.5222, -0.1237),
    'Covent Garden, London':            (51.5117, -0.1240),
    'Southbank, London':                (51.5055, -0.1132),
    'Bermondsey, London':               (51.4993, -0.0799),
    'Shoreditch, London':               (51.5232, -0.0813),
    'Islington, London':                (51.5362, -0.1029),
    'Hackney, London':                  (51.5450, -0.0553),
    # South East
    'Brighton, East Sussex':            (50.8225, -0.1372),
    'Hove, East Sussex':                (50.8370, -0.1749),
    'Eastbourne, East Sussex':          (50.7684,  0.2844),
    'Hastings, East Sussex':            (50.8562,  0.5735),
    'Guildford, Surrey':                (51.2362, -0.5704),
    'Woking, Surrey':                   (51.3192, -0.5578),
    'Kingston upon Thames, Surrey':     (51.4100, -0.3020),
    'Epsom, Surrey':                    (51.3355, -0.2664),
    'Croydon, London':                  (51.3762, -0.0982),
    'Sutton, London':                   (51.3618, -0.1945),
    'Tunbridge Wells, Kent':            (51.1328,  0.2637),
    'Maidstone, Kent':                  (51.2717,  0.5268),
    'Dover, Kent':                      (51.1295,  1.3123),
    'Canterbury, Kent':                 (51.2802,  1.0789),
    'Ashford, Kent':                    (51.1465,  0.8675),
    # East Anglia
    'Cambridge, Cambridgeshire':        (52.2053,  0.1218),
    'Norwich, Norfolk':                 (52.6309,  1.2974),
    'Great Yarmouth, Norfolk':          (52.6066,  1.7295),
    "King's Lynn, Norfolk":             (52.7531,  0.3990),
    'Peterborough, Cambridgeshire':     (52.5736, -0.2408),
    'Ely, Cambridgeshire':              (52.3985,  0.2625),
    'Northampton, Northamptonshire':    (52.2405, -0.9027),
    'Kettering, Northamptonshire':      (52.3984, -0.7280),
    'Colchester, Essex':                (51.8959,  0.8919),
    'Southend-on-Sea, Essex':           (51.5462,  0.7077),
    'Chelmsford, Essex':                (51.7356,  0.4685),
    'Basildon, Essex':                  (51.5800,  0.4891),
    'Harlow, Essex':                    (51.7707,  0.0882),
    'Ipswich, Suffolk':                 (52.0567,  1.1482),
    'Lowestoft, Suffolk':               (52.4797,  1.7508),
    # East Midlands
    'Nottingham, Nottinghamshire':      (52.9548, -1.1581),
    'Derby, Derbyshire':                (52.9225, -1.4746),
    'Leicester, Leicestershire':        (52.6369, -1.1398),
    'Coventry, West Midlands':          (52.4082, -1.5108),
    'Warwick, Warwickshire':            (52.2804, -1.5860),
    'Stratford-upon-Avon, Warwickshire':(52.1917, -1.7077),
    'Birmingham, West Midlands':        (52.4862, -1.8904),
    'Wolverhampton, West Midlands':     (52.5862, -2.1272),
    'Dudley, West Midlands':            (52.5113, -2.0874),
    'Walsall, West Midlands':           (52.5858, -1.9824),
    'Stoke-on-Trent, Staffordshire':    (53.0027, -2.1794),
    'Newcastle-under-Lyme, Staffordshire': (53.0120, -2.2277),
    'Lincoln, Lincolnshire':            (53.2307, -0.5406),
    'Grantham, Lincolnshire':           (52.9117, -0.6418),
    'Mansfield, Nottinghamshire':       (53.1475, -1.1991),
    # West Midlands
    'Birmingham City Centre':           (52.4796, -1.9026),
    'Edgbaston, Birmingham':            (52.4654, -1.9324),
    'Solihull, Birmingham':             (52.4130, -1.7780),
    'Wolverhampton City Centre':        (52.5862, -2.1272),
    'Coventry City Centre':             (52.4082, -1.5108),
    'Dudley Town Centre':               (52.5113, -2.0874),
    'Walsall Town Centre':              (52.5858, -1.9824),
    'Stoke-on-Trent City Centre':       (53.0027, -2.1794),
    'Leek, Staffordshire':              (53.1046, -1.9952),
    'Stafford, Staffordshire':          (52.8069, -2.1169),
    'Lichfield, Staffordshire':         (52.6835, -1.8276),
    'Tamworth, Staffordshire':          (52.6341, -1.6961),
    'Nuneaton, Warwickshire':           (52.5228, -1.4652),
    'Bedworth, Warwickshire':           (52.4775, -1.4755),
    'Kenilworth, Warwickshire':         (52.3413, -1.5783),
    # North West
    'Manchester City Centre':           (53.4808, -2.2426),
    'Salford, Manchester':              (53.4872, -2.2856),
    'Stockport, Greater Manchester':    (53.4083, -2.1494),
    'Oldham, Greater Manchester':       (53.5409, -2.1114),
    'Rochdale, Greater Manchester':     (53.6136, -2.1610),
    'Liverpool City Centre':            (53.4084, -2.9916),
    'Wallasey, Merseyside':             (53.4204, -3.0501),
    'Bootle, Merseyside':               (53.4440, -2.9906),
    'Chester City Centre, Cheshire':    (53.1914, -2.8920),
    'Warrington, Cheshire':             (53.3900, -2.5970),
    'Runcorn, Cheshire':                (53.3430, -2.7294),
    'Widnes, Cheshire':                 (53.3622, -2.7376),
    'Crewe, Cheshire':                  (53.0996, -2.4414),
    'Macclesfield, Cheshire':           (53.2601, -2.1269),
    'Stockport, Cheshire':              (53.4083, -2.1494),
    # Yorkshire
    'Leeds City Centre':                (53.7997, -1.5492),
    'Bradford City Centre':             (53.7959, -1.7594),
    'Huddersfield Town Centre':         (53.6459, -1.7850),
    'Halifax Town Centre':              (53.7215, -1.8633),
    'Sheffield City Centre':            (53.3811, -1.4701),
    'Rotherham, South Yorkshire':       (53.4327, -1.3565),
    'Doncaster, South Yorkshire':       (53.5228, -1.1282),
    'Wakefield, West Yorkshire':        (53.6826, -1.4997),
    'Pontefract, West Yorkshire':       (53.6920, -1.3116),
    'Castleford, West Yorkshire':       (53.7156, -1.3568),
    'York City Centre':                 (53.9600, -1.0873),
    'Harrogate, North Yorkshire':       (53.9939, -1.5377),
    'Ripon, North Yorkshire':           (54.1382, -1.5225),
    'Skipton, North Yorkshire':         (53.9622, -2.0176),
    'Kendal, Cumbria':                  (54.3235, -2.7416),
    # North East
    'Newcastle upon Tyne City Centre':  (54.9783, -1.6178),
    'Gateshead Town Centre':            (54.9581, -1.6030),
    'Sunderland City Centre':           (54.9058, -1.3816),
    'Durham City Centre':               (54.7753, -1.5849),
    'Middlesbrough Town Centre':        (54.5742, -1.2349),
    'Darlington, County Durham':        (54.5271, -1.5526),
    'Stockton-on-Tees, Teesside':       (54.5705, -1.3197),
    'Hartlepool, Teesside':             (54.6881, -1.2130),
    'Carlisle, Cumbria':                (54.8951, -2.9382),
    'Whitehaven, Cumbria':              (54.5484, -3.5890),
    'Workington, Cumbria':              (54.6427, -3.5459),
    'Penrith, Cumbria':                 (54.6640, -2.7536),
    'Berwick-upon-Tweed, Northumberland': (55.7704, -2.0050),
    'Morpeth, Northumberland':          (55.1683, -1.6893),
    'Hexham, Northumberland':           (54.9712, -2.1007),
    # Scotland
    'Edinburgh City Centre':            (55.9533, -3.1883),
    'Glasgow City Centre':              (55.8642, -4.2518),
    'Aberdeen City Centre':             (57.1497, -2.0943),
    'Dundee City Centre':               (56.4620, -2.9707),
    'Perth City Centre':                (56.3950, -3.4313),
    'Inverness City Centre':            (57.4778, -4.2247),
    'Stirling Town Centre':             (56.1165, -3.9369),
    'Ayr Town Centre':                  (55.4628, -4.6288),
    'Paisley Town Centre':              (55.8455, -4.4234),
    'Hamilton Town Centre':             (55.7779, -4.0379),
    'Motherwell Town Centre':           (55.7905, -3.9910),
    'Dumfries Town Centre':             (55.0752, -3.6040),
    'Kirkcaldy Town Centre':            (56.1128, -3.1636),
    'Livingston Town Centre':           (55.8867, -3.5231),
    'Dunfermline Town Centre':          (56.0712, -3.4585),
    # Wales
    'Cardiff City Centre':              (51.4837, -3.1681),
    'Swansea City Centre':              (51.6214, -3.9441),
    'Newport Town Centre':              (51.5841, -2.9977),
    'Wrexham Town Centre':              (53.0455, -2.9927),
    'Bangor City Centre':               (53.2271, -4.1281),
    'Aberystwyth Town Centre':          (52.4153, -4.0829),
    'Carmarthen Town Centre':           (51.8577, -4.3118),
    'Llandrindod Wells Town Centre':    (52.2422, -3.3793),
    'Colwyn Bay, Conwy':                (53.2935, -3.7249),
    'Caernarfon, Gwynedd':              (53.1395, -4.2755),
    'Porthmadog, Gwynedd':              (52.9297, -4.1320),
    'Llandudno, Conwy':                 (53.3254, -3.8247),
    'Rhyl Town Centre':                 (53.3192, -3.4907),
    'Prestatyn Town Centre':            (53.3347, -3.4044),
    'Merthyr Tydfil Town Centre':       (51.7457, -3.3787),
    # South West
    'Plymouth City Centre':             (50.3755, -4.1427),
    'Bristol City Centre':              (51.4545, -2.5879),
    'Bath City Centre':                 (51.3813, -2.3594),
    'Exeter City Centre':               (50.7236, -3.5275),
    'Torquay Town Centre':              (50.4619, -3.5251),
    'Bournemouth Town Centre':          (50.7192, -1.8808),
    'Poole Town Centre':                (50.7154, -1.9870),
    'Taunton Town Centre':              (51.0159, -3.1006),
    'Truro City Centre':                (50.2632, -5.0510),
    'Falmouth Town Centre':             (50.1547, -5.0675),
    'Penzance Town Centre':             (50.1188, -5.5372),
    'Wells Town Centre':                (51.2087, -2.6473),
    'Glastonbury Town Centre':          (51.1462, -2.7164),
    'Yeovil Town Centre':               (50.9426, -2.6370),
    'Swindon Town Centre':              (51.5604, -1.7800),
    # Isle of Wight
    'Shanklin, Isle of Wight':          (50.6298, -1.1773),
    'Sandown, Isle of Wight':           (50.6549, -1.1498),
    'Ryde, Isle of Wight':              (50.7319, -1.1634),
    'Cowes, Isle of Wight':             (50.7630, -1.2994),
    'Yarmouth, Isle of Wight':          (50.7038, -1.4980),
    'Freshwater, Isle of Wight':        (50.6836, -1.5178),
    'Ventnor, Isle of Wight':           (50.5968, -1.2087),
    'Newport, Isle of Wight':           (50.7038, -1.2956),
}

def fix_coordinates():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, address, latitude, longitude FROM postcodes")
    rows = cur.fetchall()

    updated = 0
    not_found = []

    for id_, address, old_lat, old_lon in rows:
        if address in REAL_COORDS:
            new_lat, new_lon = REAL_COORDS[address]
            cur.execute(
                "UPDATE postcodes SET latitude=?, longitude=? WHERE id=?",
                (new_lat, new_lon, id_)
            )
            updated += 1
        else:
            not_found.append(address)

    conn.commit()
    conn.close()

    print(f"✅ Updated {updated} addresses with real coordinates")
    if not_found:
        print(f"⚠  {len(not_found)} addresses not in mapping:")
        for a in not_found:
            print(f"   - {a}")

if __name__ == '__main__':
    fix_coordinates()
