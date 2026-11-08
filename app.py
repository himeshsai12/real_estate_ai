"""Streamlit entry point for the EstateSphere real-estate application."""

import json
import os
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from agents import SchedulingAgent, ValuationAgent, get_db
from data.seed_data import init_db
from reasoning_engine import AdvisorReasoningEngine


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "data" / "estate_sphere.db"
CITIES = ["New York", "San Francisco", "Miami", "Austin", "Seattle", "Los Angeles"]
PROPERTY_TYPES = ["Penthouse", "Villa", "Condo", "Townhouse", "Single Family"]

st.set_page_config(
    page_title="EstateSphere | Real Estate Advisor",
    page_icon="🏠",
    layout="wide",
)


def configure_gemini() -> None:
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        try:
            os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
        except (FileNotFoundError, KeyError):
            pass
    if not os.environ.get("GEMINI_MODEL"):
        try:
            os.environ["GEMINI_MODEL"] = st.secrets["GEMINI_MODEL"]
        except (FileNotFoundError, KeyError):
            pass


def ensure_database() -> None:
    if not DB_PATH.exists():
        init_db()


@st.cache_resource
def get_advisor() -> AdvisorReasoningEngine:
    return AdvisorReasoningEngine()


def get_properties(
    city: str = "All",
    property_type: str = "All",
    max_price: int | None = None,
    min_beds: int = 0,
    search: str = "",
) -> list[dict]:
    clauses = []
    params: list[object] = []
    if city != "All":
        clauses.append("city = ?")
        params.append(city)
    if property_type != "All":
        clauses.append("type = ?")
        params.append(property_type)
    if max_price:
        clauses.append("price <= ?")
        params.append(max_price)
    if min_beds:
        clauses.append("beds >= ?")
        params.append(min_beds)
    if search.strip():
        clauses.append("(title LIKE ? OR address LIKE ? OR description LIKE ? OR features LIKE ?)")
        wildcard = f"%{search.strip()}%"
        params.extend([wildcard] * 4)

    sql = "SELECT * FROM properties"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY price ASC"

    with closing(get_db()) as conn:
        rows = conn.execute(sql, params).fetchall()
        favorites = {
            row["property_id"]
            for row in conn.execute("SELECT property_id FROM favorites").fetchall()
        }

    properties = []
    for row in rows:
        prop = dict(row)
        prop["gallery"] = json.loads(prop["gallery"])
        prop["features"] = json.loads(prop["features"])
        prop["price_history"] = json.loads(prop["price_history"])
        prop["is_favorite"] = prop["id"] in favorites
        properties.append(prop)
    return properties


def toggle_favorite(property_id: int) -> None:
    with closing(get_db()) as conn:
        existing = conn.execute(
            "SELECT property_id FROM favorites WHERE property_id = ?",
            (property_id,),
        ).fetchone()
        if existing:
            conn.execute("DELETE FROM favorites WHERE property_id = ?", (property_id,))
        else:
            conn.execute("INSERT INTO favorites (property_id) VALUES (?)", (property_id,))
        conn.commit()


def render_property(prop: dict, key_suffix: str = "") -> None:
    with st.container(border=True):
        if prop["image_url"]:
            st.image(prop["image_url"], use_container_width=True)
        st.subheader(prop["title"])
        st.markdown(f"**${prop['price']:,.0f}** · {prop['city']} · {prop['type']}")
        st.caption(
            f"{prop['beds']} beds · {prop['baths']} baths · {prop['sqft']:,} sq ft · "
            f"${prop['price'] // max(prop['sqft'], 1):,}/sq ft"
        )
        st.write(prop["description"])
        st.caption(" · ".join(prop["features"][:6]))
        st.caption(
            f"HOA ${prop['hoa_fee']:,}/mo · Taxes ${prop['property_tax']:,}/mo · "
            f"Estimated rent ${prop['est_rent']:,}/mo"
        )
        st.write(f"Listing agent: **{prop['agent_name']}**")
        st.write(f"{prop['agent_phone']} · {prop['agent_email']}")
        if st.button(
            "Remove favorite" if prop["is_favorite"] else "Save favorite",
            key=f"favorite-{prop['id']}-{key_suffix}",
            use_container_width=True,
        ):
            toggle_favorite(prop["id"])
            st.rerun()


def render_explorer() -> None:
    with st.sidebar:
        st.header("Search filters")
        city = st.selectbox("Market", ["All", *CITIES])
        property_type = st.selectbox("Property type", ["All", *PROPERTY_TYPES])
        max_price = st.slider(
            "Maximum price",
            min_value=500_000,
            max_value=15_000_000,
            value=15_000_000,
            step=250_000,
            format="$%d",
        )
        min_beds = st.selectbox("Minimum bedrooms", [0, 1, 2, 3, 4, 5], format_func=lambda n: "Any" if n == 0 else str(n))
        search = st.text_input("Search listings", placeholder="Address, feature, or keyword")
        favorites_only = st.checkbox("Saved properties only")

    properties = get_properties(city, property_type, max_price, min_beds, search)
    if favorites_only:
        properties = [prop for prop in properties if prop["is_favorite"]]

    st.subheader(f"{len(properties)} homes in the portfolio")
    if not properties:
        st.info("No homes match these filters. Try broadening your search.")
        return

    map_column, details_column = st.columns([1, 1.7], gap="large")
    with map_column:
        st.markdown("#### Map")
        st.map(
            pd.DataFrame(
                [{"latitude": prop["lat"], "longitude": prop["lng"]} for prop in properties]
            ),
            latitude="latitude",
            longitude="longitude",
            use_container_width=True,
        )
    with details_column:
        for start in range(0, len(properties), 2):
            card_columns = st.columns(2, gap="medium")
            for column, prop in zip(card_columns, properties[start : start + 2]):
                with column:
                    render_property(prop, "explorer")


def render_chat() -> None:
    st.subheader("Chat with Aria")
    st.caption("Ask general questions or explore homes in the EstateSphere catalog.")
    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        st.info(
            "For open-ended AI chat, add a Gemini key to Streamlit Cloud under "
            "**App settings → Secrets** as `GEMINI_API_KEY = \"your-key\"`. "
            "For local use, add it to the project `.env` file and restart."
        )

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                for prop in message.get("properties", []):
                    with st.expander(f"{prop['title']} · ${prop['price']:,.0f}"):
                        st.write(f"{prop['city']} · {prop['beds']} beds · {prop['baths']} baths")
                        st.write(prop["description"])
                        st.caption(" · ".join(prop["features"][:6]))
                if message.get("sources"):
                    st.caption("Property sources: " + ", ".join(message["sources"]))

    prompt = st.chat_input("Chat with Aria or ask about homes...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        history = st.session_state.chat_history[-12:]
        with st.spinner("Aria is thinking..."):
            result = get_advisor().reason(prompt, history=history)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["response"],
            "properties": result.get("properties", []),
            "sources": [source["title"] for source in result.get("rag_context_used", [])],
        })
        st.rerun()


def render_valuation(properties: list[dict]) -> None:
    st.subheader("Apex · Property valuation")
    if not properties:
        st.info("There are no properties available to value.")
        return
    selected = st.selectbox(
        "Choose a property",
        properties,
        format_func=lambda prop: f"{prop['title']} · ${prop['price']:,.0f}",
        key="valuation_property",
    )
    if st.button("Calculate valuation", type="primary"):
        st.session_state.valuation_result = ValuationAgent.evaluate(property_id=selected["id"])

    result = st.session_state.get("valuation_result")
    if not result:
        return
    st.markdown(f"### {result['property_title']}")
    metric_columns = st.columns(4)
    metric_columns[0].metric("Estimated value", f"${result['estimated_value']:,.0f}")
    metric_columns[1].metric(
        "Valuation range",
        f"${result['valuation_range']['low']:,.0f}–${result['valuation_range']['high']:,.0f}",
    )
    metric_columns[2].metric("Deal score", f"{result['deal_score']}/100")
    metric_columns[3].metric("Gross rental yield", f"{result['investment_metrics']['gross_rental_yield_pct']:.2f}%")
    st.write(result["verdict"])
    st.write(result["negotiation_advice"])
    st.caption(
        "Portfolio estimate only; not a formal appraisal or financial advice. "
        f"Model confidence indicator: {result['confidence_score']}%."
    )
    if result["comparables"]:
        st.markdown("#### Portfolio comparables")
        st.dataframe(result["comparables"], use_container_width=True, hide_index=True)


def render_tours(properties: list[dict]) -> None:
    st.subheader("Atlas · Schedule a property tour")
    if not properties:
        st.info("There are no properties available for scheduling.")
        return

    with st.form("tour_booking"):
        prop = st.selectbox(
            "Property",
            properties,
            format_func=lambda item: f"{item['title']} · {item['city']}",
        )
        buyer_name = st.text_input("Your name")
        buyer_email = st.text_input("Email")
        buyer_phone = st.text_input("Phone")
        tour_date = st.date_input("Date", value=date.today() + timedelta(days=1), min_value=date.today())
        tour_time = st.selectbox("Time", ["10:00 AM", "02:00 PM", "04:30 PM"])
        tour_type = st.selectbox("Tour type", ["In-Person VIP Guided Tour", "Live 4K Virtual Walkthrough"])
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Book tour", type="primary")

    if submitted:
        booking = SchedulingAgent.book_tour({
            "property_id": prop["id"],
            "buyer_name": buyer_name,
            "buyer_email": buyer_email,
            "buyer_phone": buyer_phone,
            "tour_date": tour_date.isoformat(),
            "tour_time": tour_time,
            "tour_type": tour_type,
            "notes": notes,
        })
        if not booking["success"]:
            st.error(booking["error"])
        else:
            st.session_state.last_tour_id = booking["tour_id"]
            st.success(booking["message"])

    tour_id = st.session_state.get("last_tour_id")
    if tour_id:
        calendar_file = SchedulingAgent.get_ics(tour_id)
        if calendar_file:
            st.download_button(
                "Download calendar invite (.ics)",
                data=calendar_file,
                file_name=f"estatesphere-tour-{tour_id}.ics",
                mime="text/calendar",
            )

    with closing(get_db()) as conn:
        tours = conn.execute(
            """
            SELECT tours.*, properties.title AS property_title
            FROM tours JOIN properties ON properties.id = tours.property_id
            ORDER BY tour_date, tour_time
            """
        ).fetchall()
    if tours:
        st.markdown("#### Scheduled tours")
        st.dataframe([dict(tour) for tour in tours], use_container_width=True, hide_index=True)


def main() -> None:
    ensure_database()
    configure_gemini()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    st.title("EstateSphere")
    st.caption("Real-estate discovery, valuation, and tour scheduling")

    properties = get_properties()
    explore_tab, chat_tab, valuation_tab, tours_tab = st.tabs(
        ["Explore homes", "Chat with Aria", "Apex valuation", "Atlas tours"]
    )
    with explore_tab:
        render_explorer()
    with chat_tab:
        render_chat()
    with valuation_tab:
        render_valuation(properties)
    with tours_tab:
        render_tours(properties)


if __name__ == "__main__":
    main()
