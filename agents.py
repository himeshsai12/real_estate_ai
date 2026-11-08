"""
EstateSphere Multi-Agent Suite
Contains:
1. SearchAgent ("Aria") - Conversational natural language discovery agent.
2. ValuationAgent ("Apex Valuation") - Automated Valuation Model (AVM) & Investment analyst.
3. SchedulingAgent ("Atlas Concierge") - Autonomous tour scheduling with .ics calendar generation.
"""

import sqlite3
import json
import re
import os
import datetime
import math

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "estate_sphere.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# AGENT 1: NATURAL LANGUAGE DISCOVERY AGENT ("ARIA")
# ============================================================================
class SearchAgent:
    """Aria - The Intelligent Natural Language Property Search Agent"""

    CITIES = ["new york", "san francisco", "miami", "austin", "seattle", "los angeles"]
    TYPES = ["penthouse", "villa", "condo", "townhouse", "single family"]
    AMENITIES_MAP = {
        "pool": ["pool", "swim", "swimming", "hot tub", "plunge"],
        "terrace": ["terrace", "balcony", "patio", "screened porch", "deck"],
        "pet": ["pet", "pets", "dog", "dogs", "cat", "cats", "pet friendly"],
        "view": ["view", "views", "skyline", "waterfront", "bay view", "ocean", "river"],
        "waterfront": ["waterfront", "lakefront", "oceanfront", "dock", "boat"],
        "office": ["office", "work from home", "writer's pavilion", "studio"],
        "school": ["school", "schools", "education", "eanes"],
        "elevator": ["elevator"],
        "garden": ["garden", "yard", "backyard", "landscaped"],
        "luxury": ["luxury", "penthouse", "masterpiece", "compound", "wine"]
    }

    @classmethod
    def parse_query(cls, query: str):
        q = query.lower()
        filters = {
            "city": None,
            "property_type": None,
            "max_price": None,
            "min_price": None,
            "min_beds": None,
            "keywords": []
        }

        # Match City
        for city in cls.CITIES:
            if city in q:
                filters["city"] = city.title()
                break
        if "ny" in q or "nyc" in q or "manhattan" in q or "brooklyn" in q:
            filters["city"] = "New York"
        elif "sf" in q or "bay area" in q:
            filters["city"] = "San Francisco"
        elif "la" in q or "hollywood" in q or "beverly" in q:
            filters["city"] = "Los Angeles"

        # Match Type
        for ptype in cls.TYPES:
            if ptype in q:
                filters["property_type"] = ptype.title()
                break
        if "house" in q or "home" in q:
            if not filters["property_type"]:
                filters["property_type"] = "Single Family"

        # Match Price (e.g. "under 2m", "less than $1.5 million", "under 800k", "between 1m and 3m")
        # Under/Max
        under_match = re.search(r"(?:under|below|less than|max|up to)\s*\$?([0-9]+(?:\.[0-9]+)?)\s*(m|million|k|thousand)?", q)
        if under_match:
            num = float(under_match.group(1))
            unit = under_match.group(2) or ""
            if unit.startswith("m"):
                filters["max_price"] = int(num * 1_000_000)
            elif unit.startswith("k"):
                filters["max_price"] = int(num * 1_000)
            elif num < 100:  # e.g., "under 3" implies millions in luxury RE
                filters["max_price"] = int(num * 1_000_000)
            else:
                filters["max_price"] = int(num)

        # Match Beds (e.g. "3 bed", "4 bedroom", "3bhk", "2 beds")
        bed_match = re.search(r"(\d+)\s*(?:bed|bedroom|bhk|br)", q)
        if bed_match:
            filters["min_beds"] = int(bed_match.group(1))

        # Identify keyword intents
        for amenity_key, synonyms in cls.AMENITIES_MAP.items():
            if any(syn in q for syn in synonyms):
                filters["keywords"].append(amenity_key)

        return filters

    @classmethod
    def search(cls, user_message: str):
        filters = cls.parse_query(user_message)
        conn = get_db()
        cur = conn.cursor()

        sql = "SELECT * FROM properties WHERE 1=1"
        params = []

        if filters["city"]:
            sql += " AND city LIKE ?"
            params.append(f"%{filters['city']}%")

        if filters["property_type"]:
            sql += " AND type = ?"
            params.append(filters["property_type"])

        if filters["max_price"]:
            sql += " AND price <= ?"
            params.append(filters["max_price"])

        if filters["min_price"]:
            sql += " AND price >= ?"
            params.append(filters["min_price"])

        if filters["min_beds"]:
            sql += " AND beds >= ?"
            params.append(filters["min_beds"])

        cur.execute(sql, params)
        raw_rows = cur.fetchall()

        # If zero exact results, broaden search gracefully
        if not raw_rows:
            broad_sql = "SELECT * FROM properties WHERE 1=1"
            broad_params = []
            if filters["city"]:
                broad_sql += " AND city LIKE ?"
                broad_params.append(f"%{filters['city']}%")
            if filters["max_price"]:
                broad_sql += " AND price <= ?"
                broad_params.append(int(filters["max_price"] * 1.25))
            cur.execute(broad_sql, broad_params)
            raw_rows = cur.fetchall()

        conn.close()

        # Score and rank properties based on features and query terms
        results = []
        for r in raw_rows:
            item = dict(r)
            item["gallery"] = json.loads(item["gallery"])
            item["features"] = json.loads(item["features"])
            item["price_history"] = json.loads(item["price_history"])

            score = 10.0
            reasons = []

            # Scoring based on extracted keywords
            features_text = " ".join(item["features"]).lower() + " " + item["description"].lower()
            for kw in filters["keywords"]:
                matched = False
                for syn in cls.AMENITIES_MAP.get(kw, []):
                    if syn in features_text:
                        matched = True
                        break
                if matched:
                    score += 5.0
                    reasons.append(f"Features {kw.title()} amenities")

            if filters["city"] and filters["city"].lower() in item["city"].lower():
                reasons.append(f"Located in prime {item['city']}")

            if filters["max_price"] and item["price"] <= filters["max_price"]:
                savings = filters["max_price"] - item["price"]
                if savings > 50000:
                    reasons.append(f"${savings:,.0f} under your maximum budget")

            if item["school_rating"] >= 9:
                reasons.append(f"Top-tier school zone ({item['school_rating']}/10)")

            item["match_score"] = int(min(score * 7, 99))
            item["ai_reason"] = " • ".join(reasons[:3]) if reasons else "Exceptional value and prime architectural build"
            results.append(item)

        # Sort by match score then price
        results.sort(key=lambda x: (x["match_score"], -x["price"]), reverse=True)

        # Formulate Aria's conversational response
        count = len(results)
        summary_intro = f"I found **{count} exceptional properties** that align with your lifestyle criteria."
        if filters['city']:
            summary_intro += f" focused in **{filters['city']}**"
        if filters['max_price']:
            summary_intro += f" under **${filters['max_price']:,.0f}**"
        if filters['min_beds']:
            summary_intro += f" with at least **{filters['min_beds']} bedrooms**"
        summary_intro += "."

        return {
            "agent": "Aria (Discovery Agent)",
            "parsed_criteria": filters,
            "response": summary_intro,
            "matches_count": count,
            "recommendations": results[:8]  # top 8 curated
        }

# ============================================================================
# AGENT 2: VALUATION & INVESTMENT ANALYST ("APEX VALUATION")
# ============================================================================
class ValuationAgent:
    """Apex - Automated Valuation Model (AVM) and Investment Deal Evaluator"""

    @classmethod
    def evaluate(cls, property_id: int = None, custom_inputs: dict = None):
        conn = get_db()
        cur = conn.cursor()

        prop = None
        if property_id:
            cur.execute("SELECT * FROM properties WHERE id = ?", (property_id,))
            row = cur.fetchone()
            if row:
                prop = dict(row)
                prop["features"] = json.loads(prop["features"])
                prop["price_history"] = json.loads(prop["price_history"])

        # Determine target parameters
        if prop:
            city = prop["city"]
            prop_type = prop["type"]
            sqft = prop["sqft"]
            beds = prop["beds"]
            baths = prop["baths"]
            actual_price = prop["price"]
            features = prop["features"]
            est_rent = prop["est_rent"]
            hoa = prop["hoa_fee"]
            taxes = prop["property_tax"]
            title = prop["title"]
        else:
            inputs = custom_inputs or {}
            city = inputs.get("city", "New York")
            prop_type = inputs.get("type", "Condo")
            sqft = int(inputs.get("sqft", 1800))
            beds = int(inputs.get("beds", 3))
            baths = float(inputs.get("baths", 2.0))
            actual_price = int(inputs.get("price", 1500000))
            features = inputs.get("features", ["Balcony", "Smart Home Automation"])
            est_rent = int(inputs.get("est_rent", actual_price * 0.005))
            hoa = int(inputs.get("hoa", 600))
            taxes = int(inputs.get("taxes", actual_price * 0.0008))
            title = f"{beds}B/{baths}B {prop_type} in {city}"

        # Fetch neighborhood comps (same city)
        cur.execute("SELECT id, title, price, sqft, beds, baths, type FROM properties WHERE city = ?", (city,))
        comps = [dict(c) for c in cur.fetchall()]
        conn.close()

        if not comps:
            # Fallback across whole DB if city is unique
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT id, title, price, sqft, beds, baths, type FROM properties")
            comps = [dict(c) for c in cur.fetchall()]
            conn.close()

        # Compute average price per sqft for comparable properties
        type_comps = [c for c in comps if c["type"].lower() == prop_type.lower()]
        target_comps = type_comps if len(type_comps) >= 2 else comps

        avg_price_per_sqft = sum(c["price"] / c["sqft"] for c in target_comps) / max(len(target_comps), 1)

        # Baseline AVM valuation
        baseline_val = sqft * avg_price_per_sqft

        # Feature multipliers
        feat_multiplier = 1.0
        feat_reasons = []
        feat_text = " ".join(features).lower()
        if "view" in feat_text or "waterfront" in feat_text:
            feat_multiplier += 0.08
            feat_reasons.append("+8% Premium for panoramic water/city views")
        if "pool" in feat_text:
            feat_multiplier += 0.04
            feat_reasons.append("+4% Private pool & outdoor amenities")
        if "elevator" in feat_text or "penthouse" in prop_type.lower():
            feat_multiplier += 0.05
            feat_reasons.append("+5% Luxury elevator / top-floor penthouse status")
        if "smart" in feat_text:
            feat_multiplier += 0.02
            feat_reasons.append("+2% Smart home automation")

        estimated_value = int(baseline_val * feat_multiplier)
        # Round to nearest 5,000
        estimated_value = round(estimated_value / 5000) * 5000

        low_val = int(estimated_value * 0.94)
        high_val = int(estimated_value * 1.06)

        # Deal Score (0-100)
        # Ratio of estimated fair value to actual price
        val_ratio = estimated_value / max(actual_price, 1)
        if val_ratio >= 1.10:
            deal_score = 94
            verdict = "🔥 Exceptional Buy: Undervalued relative to market comps."
            advice = f"Property is priced approximately {((val_ratio - 1) * 100):.1f}% below fair market comps. Move quickly with minimal contingency conditions to secure."
        elif val_ratio >= 1.02:
            deal_score = 86
            verdict = "✅ Good Deal: Competitively priced with positive upside."
            advice = "Fairly priced. Consider submitting an initial offer 2-3% under ask or request closing cost concessions."
        elif val_ratio >= 0.96:
            deal_score = 74
            verdict = "⚖️ Fair Market Value: Appropriately priced for current market conditions."
            advice = "List price reflects current appraisals. Focus negotiation on seller inspection repairs or personal property inclusions."
        else:
            deal_score = 58
            verdict = "⚠️ Premium Asking: Priced above automated neighborhood comps."
            advice = f"Asking price is {((1 - val_ratio) * 100):.1f}% higher than baseline comps. Propose an offer closer to ${estimated_value:,.0f} based on comp metrics."

        # Financial Calculations
        gross_annual_rent = est_rent * 12
        gross_yield = (gross_annual_rent / max(actual_price, 1)) * 100
        annual_expenses = (hoa * 12) + (taxes * 12) + (actual_price * 0.01)  # 1% reserve for maintenance
        net_operating_income = max(gross_annual_rent - annual_expenses, 0)
        cap_rate = (net_operating_income / max(actual_price, 1)) * 100

        # 5-Year Appreciation Forecast (compounded at 4.6% avg historical)
        five_year_val = int(estimated_value * math.pow(1.046, 5))
        equity_gain = five_year_val - actual_price

        return {
            "agent": "Apex (Valuation Agent)",
            "property_title": title,
            "actual_price": actual_price,
            "estimated_value": estimated_value,
            "valuation_range": {"low": low_val, "high": high_val},
            "confidence_score": 92,
            "price_per_sqft": int(actual_price / sqft),
            "comp_avg_price_per_sqft": int(avg_price_per_sqft),
            "deal_score": deal_score,
            "verdict": verdict,
            "negotiation_advice": advice,
            "adjustments": feat_reasons,
            "investment_metrics": {
                "gross_rental_yield_pct": round(gross_yield, 2),
                "cap_rate_pct": round(cap_rate, 2),
                "est_monthly_rent": est_rent,
                "net_annual_income": int(net_operating_income),
                "five_year_projected_value": five_year_val,
                "projected_5yr_equity_gain": int(equity_gain)
            },
            "comparables": [
                {
                    "title": c["title"],
                    "price": c["price"],
                    "sqft": c["sqft"],
                    "price_per_sqft": int(c["price"] / c["sqft"])
                }
                for c in target_comps[:3]
            ]
        }

# ============================================================================
# AGENT 3: AUTONOMOUS TOUR SCHEDULING AGENT ("ATLAS CONCIERGE")
# ============================================================================
class SchedulingAgent:
    """Atlas - Autonomous Tour Scheduling & Concierge Agent"""

    @classmethod
    def book_tour(cls, data: dict):
        prop_id = data.get("property_id")
        buyer_name = data.get("buyer_name", "").strip()
        buyer_email = data.get("buyer_email", "").strip()
        buyer_phone = data.get("buyer_phone", "").strip()
        tour_date = data.get("tour_date", "").strip()
        tour_time = data.get("tour_time", "").strip()
        tour_type = data.get("tour_type", "In-Person Guided Tour")
        notes = data.get("notes", "")

        if not all([prop_id, buyer_name, buyer_email, tour_date, tour_time]):
            return {
                "success": False,
                "error": "Missing required fields (property_id, buyer_name, buyer_email, tour_date, tour_time)."
            }

        conn = get_db()
        cur = conn.cursor()

        # Check property exists
        cur.execute("SELECT * FROM properties WHERE id = ?", (prop_id,))
        p_row = cur.fetchone()
        if not p_row:
            conn.close()
            return {"success": False, "error": f"Property with ID {prop_id} not found."}

        property_data = dict(p_row)

        # Check conflict on the same date/time for this property
        cur.execute(
            "SELECT id FROM tours WHERE property_id = ? AND tour_date = ? AND tour_time = ?",
            (prop_id, tour_date, tour_time)
        )
        conflict = cur.fetchone()
        if conflict:
            conn.close()
            return {
                "success": False,
                "error": f"The slot on {tour_date} at {tour_time} is already booked. Please choose an adjacent time."
            }

        # Save tour booking
        cur.execute("""
        INSERT INTO tours (property_id, buyer_name, buyer_email, buyer_phone, tour_date, tour_time, tour_type, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (prop_id, buyer_name, buyer_email, buyer_phone, tour_date, tour_time, tour_type, notes))

        tour_id = cur.lastrowid
        conn.commit()
        conn.close()

        # Generate iCalendar (.ics) content
        ics_content = cls.generate_ics(tour_id, property_data, buyer_name, buyer_email, tour_date, tour_time, tour_type)

        return {
            "success": True,
            "tour_id": tour_id,
            "message": f"Congratulations {buyer_name}! Your {tour_type} has been officially reserved.",
            "details": {
                "property_title": property_data["title"],
                "address": f"{property_data['address']}, {property_data['city']}, {property_data['state']} {property_data['zip']}",
                "tour_date": tour_date,
                "tour_time": tour_time,
                "tour_type": tour_type,
                "listing_agent": {
                    "name": property_data["agent_name"],
                    "phone": property_data["agent_phone"],
                    "email": property_data["agent_email"]
                },
                "calendar_download_url": f"/api/tour/ics/{tour_id}",
                "virtual_meeting_link": f"https://meet.estatesphere.com/tour-{tour_id}" if "video" in tour_type.lower() else None
            }
        }

    @classmethod
    def generate_ics(cls, tour_id: int, property_data: dict, buyer_name: str, buyer_email: str, tour_date: str, tour_time: str, tour_type: str) -> str:
        # tour_date: YYYY-MM-DD
        # tour_time: HH:MM AM/PM
        clean_date = tour_date.replace("-", "")

        # Approximate start/end time
        time_part = "140000"
        if "am" in tour_time.lower():
            time_part = "100000"
        elif "pm" in tour_time.lower():
            time_part = "150000"

        dtstart = f"{clean_date}T{time_part}Z"
        dtend = f"{clean_date}T160000Z"

        address = f"{property_data['address']}, {property_data['city']}, {property_data['state']} {property_data['zip']}"
        summary = f"EstateSphere Tour: {property_data['title']}"
        desc = f"Tour Type: {tour_type}\\nProperty: {property_data['title']}\\nAgent: {property_data['agent_name']} ({property_data['agent_phone']})\\nBuyer: {buyer_name} ({buyer_email})"

        ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//EstateSphere//Property Tours//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:tour-{tour_id}@estatesphere.com
DTSTAMP:{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{dtstart}
DTEND:{dtend}
SUMMARY:{summary}
DESCRIPTION:{desc}
LOCATION:{address}
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""
        return ics

    @classmethod
    def get_ics(cls, tour_id: int):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT t.*, p.title, p.address, p.city, p.state, p.zip, p.agent_name, p.agent_phone, p.agent_email FROM tours t JOIN properties p ON t.property_id = p.id WHERE t.id = ?", (tour_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        p_data = {
            "title": row["title"],
            "address": row["address"],
            "city": row["city"],
            "state": row["state"],
            "zip": row["zip"],
            "agent_name": row["agent_name"],
            "agent_phone": row["agent_phone"],
            "agent_email": row["agent_email"]
        }
        return cls.generate_ics(tour_id, p_data, row["buyer_name"], row["buyer_email"], row["tour_date"], row["tour_time"], row["tour_type"])
