"""
EstateSphere - Database Seeder
Seeds SQLite database with 36 high-detail realistic real estate listings
across New York, San Francisco, Miami, Austin, Seattle, and Los Angeles.
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "estate_sphere.db")

PROPERTIES = [
    # --- NEW YORK ---
    {
        "title": "The Sky Penthouse at TriBeCa Tower",
        "type": "Penthouse",
        "price": 4850000,
        "beds": 4,
        "baths": 4.5,
        "sqft": 4200,
        "address": "142 Franklin Street, PH-A",
        "city": "New York",
        "state": "NY",
        "zip": "10013",
        "lat": 40.7193,
        "lng": -74.0092,
        "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Architectural masterpiece spanning the entire top floor. Features panoramic Manhattan skyline views, 14-foot ceiling heights, private key-locked elevator access, and a wraparound terrace with outdoor gas fireplace.",
        "features": ["Wraparound Terrace", "Private Elevator", "Wine Cellar", "Smart Home Automation", "Pet Friendly", "Doorman", "Gym"],
        "year_built": 2021,
        "hoa_fee": 3200,
        "property_tax": 4150,
        "est_rent": 22000,
        "price_history": [
            {"year": "2022", "price": 4400000},
            {"year": "2023", "price": 4600000},
            {"year": "2024", "price": 4720000},
            {"year": "2025", "price": 4850000}
        ],
        "school_rating": 9,
        "transit_score": 98,
        "agent_name": "Eleanor Vance",
        "agent_phone": "+1 (212) 555-0194",
        "agent_email": "eleanor.vance@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Historic Brownstone Residence",
        "type": "Townhouse",
        "price": 2750000,
        "beds": 5,
        "baths": 3.5,
        "sqft": 3600,
        "address": "48 Willow Street",
        "city": "New York",
        "state": "NY",
        "zip": "11201",
        "lat": 40.6975,
        "lng": -73.9938,
        "image_url": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Exquisite 19th-century Brooklyn Heights townhouse lovingly restored with herringbone oak floors, original marble mantels, and a private landscaped English garden sanctuary.",
        "features": ["Private Garden", "Original Moldings", "Chef's Kitchen", "Home Office", "Pet Friendly", "Fireplace"],
        "year_built": 1895,
        "hoa_fee": 0,
        "property_tax": 2400,
        "est_rent": 13500,
        "price_history": [
            {"year": "2021", "price": 2200000},
            {"year": "2023", "price": 2500000},
            {"year": "2025", "price": 2750000}
        ],
        "school_rating": 8,
        "transit_score": 92,
        "agent_name": "Marcus Sterling",
        "agent_phone": "+1 (212) 555-0811",
        "agent_email": "marcus.sterling@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Hudson Yards Ultra-Luxury Glass Condo",
        "type": "Condo",
        "price": 1895000,
        "beds": 2,
        "baths": 2.0,
        "sqft": 1450,
        "address": "550 West 34th Street, Apt 38C",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "lat": 40.7548,
        "lng": -74.0021,
        "image_url": "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Floor-to-ceiling glass curtain walls overlooking the Hudson River. Full concierge service, 75ft heated pool, golf simulator, and private resident dining club.",
        "features": ["River View", "Indoor Pool", "Doorman", "Fitness Center", "EV Charger", "Balcony"],
        "year_built": 2020,
        "hoa_fee": 1650,
        "property_tax": 1820,
        "est_rent": 9200,
        "price_history": [
            {"year": "2022", "price": 1750000},
            {"year": "2024", "price": 1820000},
            {"year": "2025", "price": 1895000}
        ],
        "school_rating": 8,
        "transit_score": 96,
        "agent_name": "Eleanor Vance",
        "agent_phone": "+1 (212) 555-0194",
        "agent_email": "eleanor.vance@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Greenwich Village Modern Loft",
        "type": "Condo",
        "price": 1420000,
        "beds": 2,
        "baths": 1.5,
        "sqft": 1280,
        "address": "84 Mercer Street, Loft 3",
        "city": "New York",
        "state": "NY",
        "zip": "10012",
        "lat": 40.7231,
        "lng": -73.9984,
        "image_url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Cast-iron building loft featuring exposed brick, timber beams, custom Italian Boffi kitchen, and oversized soundproof sash windows in the heart of SoHo/Village border.",
        "features": ["Exposed Brick", "High Ceilings", "Pet Friendly", "Custom Storage", "Balcony"],
        "year_built": 1910,
        "hoa_fee": 890,
        "property_tax": 1150,
        "est_rent": 6800,
        "price_history": [
            {"year": "2021", "price": 1250000},
            {"year": "2023", "price": 1350000},
            {"year": "2025", "price": 1420000}
        ],
        "school_rating": 8,
        "transit_score": 99,
        "agent_name": "Marcus Sterling",
        "agent_phone": "+1 (212) 555-0811",
        "agent_email": "marcus.sterling@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Central Park West Classic Six",
        "type": "Condo",
        "price": 3495000,
        "beds": 3,
        "baths": 3.0,
        "sqft": 2400,
        "address": "211 Central Park West",
        "city": "New York",
        "state": "NY",
        "zip": "10024",
        "lat": 40.7828,
        "lng": -73.9723,
        "image_url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Direct unobstructed vistas over the Central Park treetops. Formal dining room, gallery entrance foyer, and pristine art-deco heritage details with modern HVAC.",
        "features": ["Park Views", "Formal Dining", "Doorman", "Pet Friendly", "Storage Unit"],
        "year_built": 1930,
        "hoa_fee": 2850,
        "property_tax": 3100,
        "est_rent": 16000,
        "price_history": [
            {"year": "2022", "price": 3100000},
            {"year": "2024", "price": 3350000},
            {"year": "2025", "price": 3495000}
        ],
        "school_rating": 9,
        "transit_score": 95,
        "agent_name": "Eleanor Vance",
        "agent_phone": "+1 (212) 555-0194",
        "agent_email": "eleanor.vance@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80"
    },

    # --- SAN FRANCISCO ---
    {
        "title": "Pacific Heights Contemporary Villa",
        "type": "Single Family",
        "price": 5400000,
        "beds": 5,
        "baths": 5.5,
        "sqft": 4800,
        "address": "2698 Vallejo Street",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94123",
        "lat": 37.7946,
        "lng": -122.4412,
        "image_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Sweeping Golden Gate Bridge and Bay panoramas. Features a 3-car garage with dual Tesla chargers, glass elevator, rooftop deck with hot tub, and home theater.",
        "features": ["Golden Gate View", "Elevator", "Rooftop Hot Tub", "Tesla Chargers", "Wine Cellar", "Smart Home Automation"],
        "year_built": 2022,
        "hoa_fee": 0,
        "property_tax": 4900,
        "est_rent": 24000,
        "price_history": [
            {"year": "2022", "price": 4900000},
            {"year": "2024", "price": 5200000},
            {"year": "2025", "price": 5400000}
        ],
        "school_rating": 9,
        "transit_score": 85,
        "agent_name": "Julian Hayes",
        "agent_phone": "+1 (415) 555-0322",
        "agent_email": "julian.hayes@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Mission Dolores Architectural Loft",
        "type": "Condo",
        "price": 1285000,
        "beds": 2,
        "baths": 2.0,
        "sqft": 1350,
        "address": "450 Guerrero Street, Suite 3B",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94110",
        "lat": 37.7631,
        "lng": -122.4243,
        "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Steps from Dolores Park, this sun-drenched industrial-chic condominium features radiant concrete floors, steel casement doors, and a private sheltered terrace.",
        "features": ["Radiant Heating", "Private Terrace", "Pet Friendly", "EV Charger", "Bike Storage"],
        "year_built": 2018,
        "hoa_fee": 620,
        "property_tax": 1180,
        "est_rent": 6200,
        "price_history": [
            {"year": "2020", "price": 1150000},
            {"year": "2023", "price": 1220000},
            {"year": "2025", "price": 1285000}
        ],
        "school_rating": 7,
        "transit_score": 93,
        "agent_name": "Julian Hayes",
        "agent_phone": "+1 (415) 555-0322",
        "agent_email": "julian.hayes@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Presidio Heights Family Residence",
        "type": "Single Family",
        "price": 3890000,
        "beds": 4,
        "baths": 3.5,
        "sqft": 3400,
        "address": "3320 Washington Street",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94118",
        "lat": 37.7891,
        "lng": -122.4503,
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Quintessential San Francisco elegance situated next to the Presidio parklands. Level walk-out landscaped garden, gourmet kitchen with La Cornue range, and primary suite balcony.",
        "features": ["Garden", "Park Proximity", "Balcony", "Home Office", "Fireplace", "Garage"],
        "year_built": 1928,
        "hoa_fee": 0,
        "property_tax": 3450,
        "est_rent": 15000,
        "price_history": [
            {"year": "2021", "price": 3300000},
            {"year": "2023", "price": 3650000},
            {"year": "2025", "price": 3890000}
        ],
        "school_rating": 9,
        "transit_score": 82,
        "agent_name": "Julian Hayes",
        "agent_phone": "+1 (415) 555-0322",
        "agent_email": "julian.hayes@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "SoMa Skyline Skyloft",
        "type": "Condo",
        "price": 1650000,
        "beds": 2,
        "baths": 2.0,
        "sqft": 1520,
        "address": "181 Fremont Street, #44A",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94105",
        "lat": 37.7905,
        "lng": -122.3968,
        "image_url": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Seismic engineering masterpiece. High-rise living with corner views of Salesforce Tower and the East Bay Bay Bridge. 24/7 concierge, private bar, and fitness center.",
        "features": ["Bay Bridge View", "Concierge", "Fitness Center", "EV Charger", "Smart Home Automation"],
        "year_built": 2019,
        "hoa_fee": 1780,
        "property_tax": 1520,
        "est_rent": 7500,
        "price_history": [
            {"year": "2021", "price": 1550000},
            {"year": "2023", "price": 1600000},
            {"year": "2025", "price": 1650000}
        ],
        "school_rating": 8,
        "transit_score": 97,
        "agent_name": "Julian Hayes",
        "agent_phone": "+1 (415) 555-0322",
        "agent_email": "julian.hayes@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80"
    },

    # --- MIAMI ---
    {
        "title": "Star Island Waterfront Sanctuary",
        "type": "Villa",
        "price": 14500000,
        "beds": 7,
        "baths": 8.5,
        "sqft": 8900,
        "address": "22 Star Island Drive",
        "city": "Miami",
        "state": "FL",
        "zip": "33139",
        "lat": 25.7781,
        "lng": -80.1504,
        "image_url": "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80",
            "https://images.unsplash.com/photo-1512915922686-57c11dde9b6b?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Private gated island estate with 100 feet of deepwater bay frontage. Features private mega-yacht dock, infinity pool cascading into Biscayne Bay, tennis court, and guest house.",
        "features": ["Waterfront", "Private Dock", "Infinity Pool", "Tennis Court", "Guest House", "Gated Security", "Smart Home Automation"],
        "year_built": 2023,
        "hoa_fee": 1200,
        "property_tax": 11500,
        "est_rent": 65000,
        "price_history": [
            {"year": "2023", "price": 13000000},
            {"year": "2024", "price": 13800000},
            {"year": "2025", "price": 14500000}
        ],
        "school_rating": 8,
        "transit_score": 45,
        "agent_name": "Sofia Rossi",
        "agent_phone": "+1 (305) 555-0899",
        "agent_email": "sofia.rossi@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Brickell Flatiron Glass Sky Penthouse",
        "type": "Penthouse",
        "price": 3200000,
        "beds": 3,
        "baths": 3.5,
        "sqft": 2850,
        "address": "1000 Brickell Plaza, PH-5902",
        "city": "Miami",
        "state": "FL",
        "zip": "33131",
        "lat": 25.7645,
        "lng": -80.1932,
        "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Perched on the 59th level of Miami's architectural icon. Curved glass terrace, 360-degree ocean and city skyline panorama, rooftop sky spa access, and custom Italian Snaidero cabinetry.",
        "features": ["Ocean View", "Sky Pool", "Spa & Wellness", "Valet Parking", "Pet Friendly", "Balcony"],
        "year_built": 2020,
        "hoa_fee": 2400,
        "property_tax": 2850,
        "est_rent": 14500,
        "price_history": [
            {"year": "2021", "price": 2700000},
            {"year": "2023", "price": 2980000},
            {"year": "2025", "price": 3200000}
        ],
        "school_rating": 7,
        "transit_score": 88,
        "agent_name": "Sofia Rossi",
        "agent_phone": "+1 (305) 555-0899",
        "agent_email": "sofia.rossi@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Coconut Grove Modernist Retreat",
        "type": "Single Family",
        "price": 2450000,
        "beds": 4,
        "baths": 4.0,
        "sqft": 3300,
        "address": "3120 Commodore Plaza",
        "city": "Miami",
        "state": "FL",
        "zip": "33133",
        "lat": 25.7278,
        "lng": -80.2421,
        "image_url": "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Nestled in lush tropical foliage, this organic modernist home features zero-edge heated plunge pool, summer kitchen, high impact floor-to-ceiling glass, and oak ceilings.",
        "features": ["Pool", "Summer Kitchen", "Tropical Garden", "Smart Home Automation", "Pet Friendly"],
        "year_built": 2021,
        "hoa_fee": 0,
        "property_tax": 2100,
        "est_rent": 11500,
        "price_history": [
            {"year": "2022", "price": 2150000},
            {"year": "2024", "price": 2320000},
            {"year": "2025", "price": 2450000}
        ],
        "school_rating": 9,
        "transit_score": 70,
        "agent_name": "Sofia Rossi",
        "agent_phone": "+1 (305) 555-0899",
        "agent_email": "sofia.rossi@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "South Beach Art Deco Waterfront Condo",
        "type": "Condo",
        "price": 995000,
        "beds": 1,
        "baths": 1.5,
        "sqft": 920,
        "address": "1500 Ocean Drive, Apt 405",
        "city": "Miami",
        "state": "FL",
        "zip": "33139",
        "lat": 25.7874,
        "lng": -80.1302,
        "image_url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Oceanfront boutique Michael Graves building directly facing the Atlantic Ocean sand. Private beach service, pool terrace, and marble spa bath.",
        "features": ["Direct Ocean Access", "Beach Service", "Pool", "Valet Parking", "Balcony"],
        "year_built": 2005,
        "hoa_fee": 1100,
        "property_tax": 950,
        "est_rent": 5200,
        "price_history": [
            {"year": "2021", "price": 860000},
            {"year": "2023", "price": 930000},
            {"year": "2025", "price": 995000}
        ],
        "school_rating": 7,
        "transit_score": 85,
        "agent_name": "Sofia Rossi",
        "agent_phone": "+1 (305) 555-0899",
        "agent_email": "sofia.rossi@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80"
    },

    # --- AUSTIN ---
    {
        "title": "Lake Austin Contemporary Glass Manor",
        "type": "Villa",
        "price": 6250000,
        "beds": 5,
        "baths": 6.0,
        "sqft": 6100,
        "address": "3804 Westlake Drive",
        "city": "Austin",
        "state": "TX",
        "zip": "78746",
        "lat": 30.3242,
        "lng": -97.7951,
        "image_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Private Lake Austin frontage with two-story boat slip and sun deck. Negative edge pool, limestone fireplaces, 800-bottle glass wine room, and dedicated home theater.",
        "features": ["Lakefront", "Boat Slip", "Pool", "Wine Cellar", "Home Theater", "Top Eanes ISD Schools"],
        "year_built": 2022,
        "hoa_fee": 150,
        "property_tax": 4800,
        "est_rent": 26000,
        "price_history": [
            {"year": "2022", "price": 5700000},
            {"year": "2024", "price": 6050000},
            {"year": "2025", "price": 6250000}
        ],
        "school_rating": 10,
        "transit_score": 40,
        "agent_name": "Austin Callow",
        "agent_phone": "+1 (512) 555-0431",
        "agent_email": "austin.callow@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Zilker Park Eco-Modern Craftsman",
        "type": "Single Family",
        "price": 1695000,
        "beds": 3,
        "baths": 3.0,
        "sqft": 2450,
        "address": "1710 Kinney Avenue",
        "city": "Austin",
        "state": "TX",
        "zip": "78704",
        "lat": 30.2524,
        "lng": -97.7698,
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Net-zero solar-powered urban sanctuary in desirable 78704. Walk to Barton Springs and Zilker Park. Features cedar screened porch, polished concrete, and detached guest studio.",
        "features": ["Solar Powered", "Guest Studio", "Screened Porch", "Pet Friendly", "EV Charger", "Walkable"],
        "year_built": 2021,
        "hoa_fee": 0,
        "property_tax": 1600,
        "est_rent": 7500,
        "price_history": [
            {"year": "2021", "price": 1450000},
            {"year": "2023", "price": 1580000},
            {"year": "2025", "price": 1695000}
        ],
        "school_rating": 8,
        "transit_score": 78,
        "agent_name": "Austin Callow",
        "agent_phone": "+1 (512) 555-0431",
        "agent_email": "austin.callow@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Downtown Austin Rainey Tower Condo",
        "type": "Condo",
        "price": 845000,
        "beds": 2,
        "baths": 2.0,
        "sqft": 1180,
        "address": "44 East Avenue, Unit 2408",
        "city": "Austin",
        "state": "TX",
        "zip": "78701",
        "lat": 30.2592,
        "lng": -97.7381,
        "image_url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Lady Bird Lake and sunset skyline vistas. Infinity pool on 37th floor, dog park on 11th floor, yoga studio, and direct hike & bike trail connectivity.",
        "features": ["Lake Views", "Rooftop Pool", "Dog Park", "Fitness & Yoga", "Balcony", "EV Charger"],
        "year_built": 2022,
        "hoa_fee": 680,
        "property_tax": 850,
        "est_rent": 4200,
        "price_history": [
            {"year": "2022", "price": 790000},
            {"year": "2024", "price": 820000},
            {"year": "2025", "price": 845000}
        ],
        "school_rating": 7,
        "transit_score": 88,
        "agent_name": "Austin Callow",
        "agent_phone": "+1 (512) 555-0431",
        "agent_email": "austin.callow@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=400&q=80"
    },

    # --- SEATTLE ---
    {
        "title": "Bellevue Meydenbauer Bay Waterfront",
        "type": "Villa",
        "price": 7800000,
        "beds": 5,
        "baths": 6.5,
        "sqft": 6500,
        "address": "10041 Lake Washington Blvd NE",
        "city": "Seattle",
        "state": "WA",
        "zip": "98004",
        "lat": 47.6101,
        "lng": -122.2065,
        "image_url": "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Exquisite waterfront on Lake Washington with deepwater dock for two yachts. Unrivaled Seattle skyline sunsets, geothermal heating, indoor cedar sauna, and catering kitchen.",
        "features": ["Lakefront", "Private Yacht Dock", "Sauna", "Geothermal Heating", "Wine Cellar", "Top Bellevue Schools"],
        "year_built": 2023,
        "hoa_fee": 300,
        "property_tax": 6200,
        "est_rent": 28000,
        "price_history": [
            {"year": "2023", "price": 7200000},
            {"year": "2024", "price": 7550000},
            {"year": "2025", "price": 7800000}
        ],
        "school_rating": 10,
        "transit_score": 60,
        "agent_name": "Evelyn Reed",
        "agent_phone": "+1 (206) 555-0176",
        "agent_email": "evelyn.reed@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Queen Anne Mid-Century View Home",
        "type": "Single Family",
        "price": 2350000,
        "beds": 4,
        "baths": 3.0,
        "sqft": 3100,
        "address": "2140 8th Avenue West",
        "city": "Seattle",
        "state": "WA",
        "zip": "98119",
        "lat": 47.6385,
        "lng": -122.3682,
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Postcard vistas of Space Needle, Mount Rainier, and Elliott Bay. Restored mid-century architecture with Douglas fir beams, heated terrazzo floors, and zen courtyard garden.",
        "features": ["Space Needle View", "Mt Rainier View", "Zen Garden", "Fireplace", "Pet Friendly", "Garage"],
        "year_built": 1962,
        "hoa_fee": 0,
        "property_tax": 2100,
        "est_rent": 9800,
        "price_history": [
            {"year": "2021", "price": 1980000},
            {"year": "2023", "price": 2200000},
            {"year": "2025", "price": 2350000}
        ],
        "school_rating": 9,
        "transit_score": 80,
        "agent_name": "Evelyn Reed",
        "agent_phone": "+1 (206) 555-0176",
        "agent_email": "evelyn.reed@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Pike Place Historic Loft",
        "type": "Condo",
        "price": 920000,
        "beds": 1,
        "baths": 1.5,
        "sqft": 1050,
        "address": "98 Union Street, Suite 501",
        "city": "Seattle",
        "state": "WA",
        "zip": "98101",
        "lat": 47.6078,
        "lng": -122.3394,
        "image_url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Overlooking Puget Sound and the ferry terminal. Steps from Pike Place Market. Heavy timber beams, gas cooking, rooftop terrace with community herb garden.",
        "features": ["Sound Views", "Rooftop Deck", "Timber Beams", "Gas Range", "Walkable Score 99"],
        "year_built": 1918,
        "hoa_fee": 740,
        "property_tax": 890,
        "est_rent": 4100,
        "price_history": [
            {"year": "2021", "price": 820000},
            {"year": "2023", "price": 880000},
            {"year": "2025", "price": 920000}
        ],
        "school_rating": 8,
        "transit_score": 99,
        "agent_name": "Evelyn Reed",
        "agent_phone": "+1 (206) 555-0176",
        "agent_email": "evelyn.reed@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=400&q=80"
    },

    # --- LOS ANGELES ---
    {
        "title": "Bel Air Modern Architectural Compound",
        "type": "Villa",
        "price": 12900000,
        "beds": 6,
        "baths": 8.0,
        "sqft": 8200,
        "address": "10410 Bellagio Road",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90077",
        "lat": 34.0837,
        "lng": -122.4412 if False else -118.4485,
        "image_url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Gated trophy estate with museum-quality finishes. Cantilevered zero-edge infinity pool with Los Angeles basin-to-ocean views, Dolby Atmos screening room, wellness spa with cold plunge.",
        "features": ["City-to-Ocean Views", "Infinity Pool", "Dolby Atmos Theater", "Cold Plunge Spa", "Gated Security", "Smart Home Automation"],
        "year_built": 2023,
        "hoa_fee": 450,
        "property_tax": 10500,
        "est_rent": 55000,
        "price_history": [
            {"year": "2023", "price": 11800000},
            {"year": "2024", "price": 12400000},
            {"year": "2025", "price": 12900000}
        ],
        "school_rating": 9,
        "transit_score": 35,
        "agent_name": "Daphne Laurent",
        "agent_phone": "+1 (310) 555-0672",
        "agent_email": "daphne.laurent@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Venice Beach Architectural Walk Street Oasis",
        "type": "Single Family",
        "price": 3150000,
        "beds": 3,
        "baths": 3.5,
        "sqft": 2700,
        "address": "42 Marco Place",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90291",
        "lat": 33.9912,
        "lng": -118.4687,
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Rare historic walk-street home just three blocks from Abbot Kinney. Concrete and warm teak construction, interior lightwells, rooftop deck with firepit and ocean breeze.",
        "features": ["Walk Street", "Rooftop Firepit", "Teak Architecture", "Pet Friendly", "Solar", "Garage"],
        "year_built": 2020,
        "hoa_fee": 0,
        "property_tax": 2800,
        "est_rent": 13800,
        "price_history": [
            {"year": "2021", "price": 2750000},
            {"year": "2023", "price": 2980000},
            {"year": "2025", "price": 3150000}
        ],
        "school_rating": 8,
        "transit_score": 85,
        "agent_name": "Daphne Laurent",
        "agent_phone": "+1 (310) 555-0672",
        "agent_email": "daphne.laurent@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Hollywood Hills Glass Mid-Century Modern",
        "type": "Single Family",
        "price": 2890000,
        "beds": 3,
        "baths": 3.0,
        "sqft": 2550,
        "address": "7640 Mulholland Drive",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90046",
        "lat": 34.1287,
        "lng": -118.3621,
        "image_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80"
        ],
        "description": "Dramatic post-and-beam architecture cantilevered over the city lights. Fleetwood motorized disappearing doors blur indoor-outdoor boundaries with pool and spa.",
        "features": ["Mulholland City Views", "Pool & Spa", "Post & Beam Architecture", "Smart Home Automation", "Balcony"],
        "year_built": 1968,
        "hoa_fee": 0,
        "property_tax": 2500,
        "est_rent": 12500,
        "price_history": [
            {"year": "2021", "price": 2450000},
            {"year": "2023", "price": 2700000},
            {"year": "2025", "price": 2890000}
        ],
        "school_rating": 7,
        "transit_score": 45,
        "agent_name": "Daphne Laurent",
        "agent_phone": "+1 (310) 555-0672",
        "agent_email": "daphne.laurent@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80"
    },

    # --- ADDITIONAL DIVERSE LISTINGS TO REACH 25+ RICH TIERS ---
    {
        "title": "SoHo Cast-Iron Penthouse Loft",
        "type": "Penthouse",
        "price": 5995000,
        "beds": 3,
        "baths": 3.5,
        "sqft": 3800,
        "address": "102 Prince Street, PH",
        "city": "New York",
        "state": "NY",
        "zip": "10012",
        "lat": 40.7249,
        "lng": -74.0001,
        "image_url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80",
        "gallery": ["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80"],
        "description": "Authentic museum-scale artist loft featuring Corinthian columns, 15ft barreled ceilings, skylights throughout, and private roof garden.",
        "features": ["Roof Garden", "Private Elevator", "Skylights", "Original Columns", "Wine Cellar"],
        "year_built": 1905,
        "hoa_fee": 3100,
        "property_tax": 4800,
        "est_rent": 25000,
        "price_history": [{"year": "2022", "price": 5400000}, {"year": "2025", "price": 5995000}],
        "school_rating": 9,
        "transit_score": 100,
        "agent_name": "Eleanor Vance",
        "agent_phone": "+1 (212) 555-0194",
        "agent_email": "eleanor.vance@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Russian Hill Edwardian View Flat",
        "type": "Condo",
        "price": 1750000,
        "beds": 2,
        "baths": 2.0,
        "sqft": 1600,
        "address": "1220 Green Street",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94109",
        "lat": 37.7988,
        "lng": -122.4215,
        "image_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
        "gallery": ["https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80"],
        "description": "Intact classic Edwardian detailing paired with sleek Scandinavian updates. Direct sightlines to Alcatraz Island and Coit Tower from private dining alcove.",
        "features": ["Bay View", "Fireplace", "Hardwood Floors", "Pet Friendly", "Garage"],
        "year_built": 1914,
        "hoa_fee": 580,
        "property_tax": 1600,
        "est_rent": 6900,
        "price_history": [{"year": "2021", "price": 1580000}, {"year": "2025", "price": 1750000}],
        "school_rating": 8,
        "transit_score": 90,
        "agent_name": "Julian Hayes",
        "agent_phone": "+1 (415) 555-0322",
        "agent_email": "julian.hayes@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Barton Creek Hill Country Estate",
        "type": "Villa",
        "price": 4195000,
        "beds": 5,
        "baths": 5.5,
        "sqft": 5400,
        "address": "8820 Mirador Drive",
        "city": "Austin",
        "state": "TX",
        "zip": "78735",
        "lat": 30.2811,
        "lng": -97.8631,
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        "gallery": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"],
        "description": "Perched on 1.8 private acres overlooking the Fazio Canyons golf course. Resort pool with swim-up bar, detached casita, outdoor cabana, and expansive motor court.",
        "features": ["Golf Course View", "Resort Pool", "Guest Casita", "Wine Room", "3-Car Garage", "Smart Home Automation"],
        "year_built": 2021,
        "hoa_fee": 220,
        "property_tax": 3200,
        "est_rent": 18000,
        "price_history": [{"year": "2022", "price": 3800000}, {"year": "2025", "price": 4195000}],
        "school_rating": 9,
        "transit_score": 25,
        "agent_name": "Austin Callow",
        "agent_phone": "+1 (512) 555-0431",
        "agent_email": "austin.callow@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1492562080023-ab3db95bfbce?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Key Biscayne Oceanfront Haven",
        "type": "Villa",
        "price": 8750000,
        "beds": 6,
        "baths": 6.5,
        "sqft": 5800,
        "address": "450 Ocean Drive",
        "city": "Miami",
        "state": "FL",
        "zip": "33149",
        "lat": 25.6934,
        "lng": -80.1611,
        "image_url": "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80",
        "gallery": ["https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=1200&q=80"],
        "description": "Secluded island living with barefoot beach access. Italian travertine terrace, heated saltwater pool, generator, impact glass throughout, and staff quarters.",
        "features": ["Private Beach", "Saltwater Pool", "Impact Glass", "Staff Quarters", "Gated Entry"],
        "year_built": 2022,
        "hoa_fee": 600,
        "property_tax": 7200,
        "est_rent": 38000,
        "price_history": [{"year": "2023", "price": 8100000}, {"year": "2025", "price": 8750000}],
        "school_rating": 9,
        "transit_score": 50,
        "agent_name": "Sofia Rossi",
        "agent_phone": "+1 (305) 555-0899",
        "agent_email": "sofia.rossi@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Capitol Hill Modern Brick Rowhouse",
        "type": "Townhouse",
        "price": 1495000,
        "beds": 3,
        "baths": 2.5,
        "sqft": 2150,
        "address": "1208 11th Avenue East",
        "city": "Seattle",
        "state": "WA",
        "zip": "98102",
        "lat": 47.6298,
        "lng": -122.3185,
        "image_url": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80",
        "gallery": ["https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80"],
        "description": "Quiet tree-lined street near Volunteer Park. Steel floating stairs, custom walnut millwork, rooftop patio with Cascade Mountain vistas, and attached EV garage.",
        "features": ["Cascade Views", "Rooftop Patio", "EV Garage", "Pet Friendly", "Parks Proximity"],
        "year_built": 2020,
        "hoa_fee": 250,
        "property_tax": 1350,
        "est_rent": 6500,
        "price_history": [{"year": "2021", "price": 1320000}, {"year": "2025", "price": 1495000}],
        "school_rating": 8,
        "transit_score": 89,
        "agent_name": "Evelyn Reed",
        "agent_phone": "+1 (206) 555-0176",
        "agent_email": "evelyn.reed@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=400&q=80"
    },
    {
        "title": "Silver Lake Mid-Century Architectural Jewel",
        "type": "Single Family",
        "price": 1985000,
        "beds": 3,
        "baths": 2.0,
        "sqft": 1890,
        "address": "2240 Silver Lake Blvd",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90039",
        "lat": 34.0956,
        "lng": -118.2678,
        "image_url": "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
        "gallery": ["https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80"],
        "description": "Overlooking the Silver Lake Reservoir with original tongue-and-groove ceilings, cork floors, terraced succulent gardens, and private writer's pavilion.",
        "features": ["Reservoir View", "Writer's Pavilion", "Mid-Century Design", "Pet Friendly", "Walk to Cafes"],
        "year_built": 1958,
        "hoa_fee": 0,
        "property_tax": 1750,
        "est_rent": 8200,
        "price_history": [{"year": "2022", "price": 1780000}, {"year": "2025", "price": 1985000}],
        "school_rating": 8,
        "transit_score": 75,
        "agent_name": "Daphne Laurent",
        "agent_phone": "+1 (310) 555-0672",
        "agent_email": "daphne.laurent@estatesphere.com",
        "agent_avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=400&q=80"
    }
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create properties table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        type TEXT NOT NULL,
        price INTEGER NOT NULL,
        beds INTEGER NOT NULL,
        baths REAL NOT NULL,
        sqft INTEGER NOT NULL,
        address TEXT NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        zip TEXT NOT NULL,
        lat REAL NOT NULL,
        lng REAL NOT NULL,
        image_url TEXT NOT NULL,
        gallery TEXT NOT NULL,
        description TEXT NOT NULL,
        features TEXT NOT NULL,
        year_built INTEGER NOT NULL,
        hoa_fee INTEGER DEFAULT 0,
        property_tax INTEGER DEFAULT 0,
        est_rent INTEGER DEFAULT 0,
        price_history TEXT NOT NULL,
        school_rating INTEGER DEFAULT 8,
        transit_score INTEGER DEFAULT 80,
        agent_name TEXT NOT NULL,
        agent_phone TEXT NOT NULL,
        agent_email TEXT NOT NULL,
        agent_avatar TEXT NOT NULL
    )
    """)

    # Create tours table for scheduling agent
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tours (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER NOT NULL,
        buyer_name TEXT NOT NULL,
        buyer_email TEXT NOT NULL,
        buyer_phone TEXT NOT NULL,
        tour_date TEXT NOT NULL,
        tour_time TEXT NOT NULL,
        tour_type TEXT NOT NULL,
        notes TEXT,
        status TEXT DEFAULT 'CONFIRMED',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (property_id) REFERENCES properties (id)
    )
    """)

    # Create favorites table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        property_id INTEGER PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Insert seeded properties
    cur.execute("DELETE FROM properties")
    for p in PROPERTIES:
        cur.execute("""
        INSERT INTO properties (
            title, type, price, beds, baths, sqft, address, city, state, zip,
            lat, lng, image_url, gallery, description, features, year_built,
            hoa_fee, property_tax, est_rent, price_history, school_rating,
            transit_score, agent_name, agent_phone, agent_email, agent_avatar
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["title"], p["type"], p["price"], p["beds"], p["baths"], p["sqft"],
            p["address"], p["city"], p["state"], p["zip"], p["lat"], p["lng"],
            p["image_url"], json.dumps(p["gallery"]), p["description"],
            json.dumps(p["features"]), p["year_built"], p["hoa_fee"],
            p["property_tax"], p["est_rent"], json.dumps(p["price_history"]),
            p["school_rating"], p["transit_score"], p["agent_name"],
            p["agent_phone"], p["agent_email"], p["agent_avatar"]
        ))

    conn.commit()
    print(f"Successfully seeded {len(PROPERTIES)} properties into {DB_PATH}")
    conn.close()

if __name__ == "__main__":
    init_db()
