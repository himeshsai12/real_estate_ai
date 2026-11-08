"""
EstateSphere - Multi-Threaded HTTP & REST API Server
Runs out of the box with zero third-party dependencies using Python standard library.
"""

import sys
import os
import json
import sqlite3
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# Import agents
from agents import SearchAgent, ValuationAgent, SchedulingAgent, get_db
from rag_engine import RAGEngine
from reasoning_engine import AdvisorReasoningEngine

# Global reasoning advisor instance
advisor_engine = AdvisorReasoningEngine()

PORT = 8000
PUBLIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public")

class EstateSphereHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS and caching headers
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, message, status=400):
        self.send_json({"success": False, "error": message}, status=status)

    def read_post_json(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length == 0:
                return {}
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw)
        except Exception as e:
            return None

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        query = urllib.parse.parse_qs(url.query)

        # ---------------------------------------------------------------------
        # API: Favicon redirect / handler
        # ---------------------------------------------------------------------
        if path == "/favicon.ico":
            self.send_response(302)
            self.send_header("Location", "/favicon.svg")
            self.end_headers()
            return

        # ---------------------------------------------------------------------
        # API: GET /api/properties
        # ---------------------------------------------------------------------
        if path == "/api/properties":
            conn = get_db()
            cur = conn.cursor()

            sql = "SELECT * FROM properties WHERE 1=1"
            params = []

            # Filters
            city = query.get("city", [None])[0]
            if city and city.lower() != "all":
                sql += " AND city LIKE ?"
                params.append(f"%{city}%")

            ptype = query.get("type", [None])[0]
            if ptype and ptype.lower() != "all":
                sql += " AND type = ?"
                params.append(ptype)

            min_price = query.get("min_price", [None])[0]
            if min_price:
                sql += " AND price >= ?"
                params.append(int(min_price))

            max_price = query.get("max_price", [None])[0]
            if max_price:
                sql += " AND price <= ?"
                params.append(int(max_price))

            beds = query.get("beds", [None])[0]
            if beds and beds != "any":
                sql += " AND beds >= ?"
                params.append(int(beds))

            baths = query.get("baths", [None])[0]
            if baths and baths != "any":
                sql += " AND baths >= ?"
                params.append(float(baths))

            search = query.get("search", [None])[0]
            if search:
                sql += " AND (title LIKE ? OR address LIKE ? OR description LIKE ? OR features LIKE ?)"
                term = f"%{search}%"
                params.extend([term, term, term, term])

            # Sorting
            sort = query.get("sort", ["featured"])[0]
            if sort == "price_asc":
                sql += " ORDER BY price ASC"
            elif sort == "price_desc":
                sql += " ORDER BY price DESC"
            elif sort == "sqft_desc":
                sql += " ORDER BY sqft DESC"
            elif sort == "newest":
                sql += " ORDER BY year_built DESC"
            else:
                sql += " ORDER BY id ASC"

            cur.execute(sql, params)
            rows = cur.fetchall()

            cur.execute("SELECT property_id FROM favorites")
            favs = set(r[0] for r in cur.fetchall())
            conn.close()

            items = []
            for r in rows:
                item = dict(r)
                item["gallery"] = json.loads(item["gallery"])
                item["features"] = json.loads(item["features"])
                item["price_history"] = json.loads(item["price_history"])
                item["is_favorite"] = item["id"] in favs
                items.append(item)

            self.send_json({"success": True, "count": len(items), "properties": items})
            return

        # ---------------------------------------------------------------------
        # API: Favicon redirect / handler
        # ---------------------------------------------------------------------
        if path == "/favicon.ico":
            self.send_response(302)
            self.send_header("Location", "/favicon.svg")
            self.end_headers()
            return

        # ---------------------------------------------------------------------
        # API: GET /api/properties/<id>
        # ---------------------------------------------------------------------
        if path.startswith("/api/properties/"):
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[2].isdigit():
                pid = int(parts[2])
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT * FROM properties WHERE id = ?", (pid,))
                row = cur.fetchone()
                if not row:
                    conn.close()
                    self.send_error_json("Property not found", 404)
                    return

                item = dict(row)
                item["gallery"] = json.loads(item["gallery"])
                item["features"] = json.loads(item["features"])
                item["price_history"] = json.loads(item["price_history"])

                cur.execute("SELECT property_id FROM favorites WHERE property_id = ?", (pid,))
                item["is_favorite"] = bool(cur.fetchone())

                # Nearby comps
                cur.execute("SELECT id, title, price, beds, baths, sqft, image_url, address FROM properties WHERE city = ? AND id != ? LIMIT 3", (item["city"], pid))
                item["comps"] = [dict(c) for c in cur.fetchall()]
                conn.close()

                self.send_json({"success": True, "property": item})
                return

        # ---------------------------------------------------------------------
        # API: GET /api/stats
        # ---------------------------------------------------------------------
        if path == "/api/stats":
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*), AVG(price), AVG(price / sqft), COUNT(DISTINCT city) FROM properties")
            tot, avg_p, avg_psq, cities_cnt = cur.fetchone()
            cur.execute("SELECT COUNT(*) FROM tours")
            tours_cnt = cur.fetchone()[0]
            conn.close()

            self.send_json({
                "success": True,
                "total_properties": tot or 0,
                "average_price": int(avg_p or 0),
                "avg_price_per_sqft": int(avg_psq or 0),
                "cities_covered": cities_cnt or 0,
                "total_tours_scheduled": tours_cnt or 0
            })
            return

        # ---------------------------------------------------------------------
        # API: GET /api/tours
        # ---------------------------------------------------------------------
        if path == "/api/tours":
            conn = get_db()
            cur = conn.cursor()
            cur.execute("""
            SELECT t.*, p.title as property_title, p.address as property_address, p.city, p.image_url, p.agent_name, p.agent_phone
            FROM tours t
            JOIN properties p ON t.property_id = p.id
            ORDER BY t.created_at DESC
            """)
            tours = [dict(r) for r in cur.fetchall()]
            conn.close()
            self.send_json({"success": True, "count": len(tours), "tours": tours})
            return

        # ---------------------------------------------------------------------
        # API: GET /api/tour/ics/<id>
        # ---------------------------------------------------------------------
        if path.startswith("/api/tour/ics/"):
            parts = path.strip("/").split("/")
            if len(parts) == 4 and parts[3].isdigit():
                tour_id = int(parts[3])
                ics_text = SchedulingAgent.get_ics(tour_id)
                if not ics_text:
                    self.send_error_json("Tour not found", 404)
                    return

                ics_bytes = ics_text.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/calendar; charset=utf-8")
                self.send_header("Content-Disposition", f"attachment; filename=tour_{tour_id}.ics")
                self.send_header("Content-Length", str(len(ics_bytes)))
                self.end_headers()
                self.wfile.write(ics_bytes)
                return

        # Fallback to standard static file server
        super().do_GET()

    def do_POST(self):
        url = urllib.parse.urlparse(self.path)
        path = url.path
        payload = self.read_post_json()
        if payload is None:
            self.send_error_json("Invalid JSON body", 400)
            return

        # ---------------------------------------------------------------------
        # RAG AGENT ENGINE: POST /api/agents/rag
        # ---------------------------------------------------------------------
        if path == "/api/agents/rag":
            query = payload.get("query", "").strip()
            history = payload.get("history", [])
            if not query:
                self.send_error_json("Search query cannot be empty", 400)
                return

            result = advisor_engine.reason(query, history=history)
            self.send_json({"success": True, "result": result})
            return

        # ---------------------------------------------------------------------
        # AGENT 1: POST /api/agents/search (Aria)
        # ---------------------------------------------------------------------
        if path == "/api/agents/search":
            query = payload.get("query", "").strip()
            history = payload.get("history", [])
            if not query:
                self.send_error_json("Search query cannot be empty", 400)
                return

            result = advisor_engine.reason(query, history=history)
            self.send_json({"success": True, "result": result})
            return

        # ---------------------------------------------------------------------
        # AGENT 2: POST /api/agents/valuation (Apex)
        # ---------------------------------------------------------------------
        if path == "/api/agents/valuation":
            prop_id = payload.get("property_id")
            custom_inputs = payload.get("custom_inputs")
            result = ValuationAgent.evaluate(property_id=prop_id, custom_inputs=custom_inputs)
            self.send_json({"success": True, "result": result})
            return

        # ---------------------------------------------------------------------
        # AGENT 3: POST /api/agents/schedule (Atlas)
        # ---------------------------------------------------------------------
        if path == "/api/agents/schedule":
            result = SchedulingAgent.book_tour(payload)
            if not result.get("success"):
                self.send_error_json(result.get("error", "Failed to book tour"), 400)
                return
            self.send_json({"success": True, "result": result})
            return

        # ---------------------------------------------------------------------
        # API: POST /api/favorites/toggle
        # ---------------------------------------------------------------------
        if path == "/api/favorites/toggle":
            pid = payload.get("property_id")
            if not pid:
                self.send_error_json("property_id required", 400)
                return

            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT property_id FROM favorites WHERE property_id = ?", (pid,))
            exists = cur.fetchone()

            if exists:
                cur.execute("DELETE FROM favorites WHERE property_id = ?", (pid,))
                is_fav = False
            else:
                cur.execute("INSERT INTO favorites (property_id) VALUES (?)", (pid,))
                is_fav = True

            conn.commit()
            conn.close()
            self.send_json({"success": True, "property_id": pid, "is_favorite": is_fav})
            return

        self.send_error_json("Endpoint not found", 404)

def run_server(port=PORT):
    server_address = ("", port)
    httpd = ThreadingHTTPServer(server_address, EstateSphereHandler)
    print(f"============================================================")
    print(f"  ESTATESPHERE REAL ESTATE PLATFORM WITH MULTI-AGENT SUITE   ")
    print(f"============================================================")
    print(f"  Server listening at: http://localhost:{port}")
    print(f"  Serving UI from:     {PUBLIC_DIR}")
    print(f"  Press Ctrl+C to terminate.")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
        httpd.server_close()

if __name__ == "__main__":
    p = PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        p = int(sys.argv[1])
    run_server(p)
