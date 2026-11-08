# app.py
import requests
import streamlit as st
from urllib.parse import urlparse

COURSES = {
    "Mathematics — 1BMATS101": {
        "name": "Engineering Mathematics",
        "codes": ["1BMATS101"],
        "modules": [
            "Multivariate calculus and series expansion",
            "Vector calculus",
            "Vector spaces",
            "Linear transformations",
            "Linear algebra",
        ],
    },
    "Applied Physics — BPHYS102/202": {
        "name": "Applied Physics for CSE",
        "codes": ["BPHYS102", "BPHYS202"],
        "modules": [
            "Quantum mechanics",
            "Electrical properties of metals and semiconductors",
            "Superconductivity",
            "Photonics",
            "Quantum computing",
        ],
    },
    "Electronics — 1BESC104D": {
        "name": "Electronics syllabus you shared",
        "codes": ["1BESC104D"],
        "modules": [
            "Semiconductor diodes and power supplies",
            "Oscillators and operational amplifiers",
            "Digital logic and combinational circuits",
            "Embedded systems",
            "Communication systems",
        ],
    },
}


def search_web(api_key, query):
    response = requests.post(
        "https://api.tavily.com/search",
        json={
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "max_results": 5,
            "include_answer": False,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("results", [])


def source_label(url):
    host = urlparse(url).netloc.lower().removeprefix("www.")
    if host.endswith("sjec.ac.in"):
        return "SJEC-domain result — check the paper details"
    if host.endswith("vtu.ac.in"):
        return "VTU result — it may not match SJEC’s syllabus"
    return "Other source — verify the course code and scheme"


st.set_page_config(page_title="SJEC PYQ Finder", page_icon="📚")
st.title("First-Year CSE PYQ Finder")
st.caption("Searches public web results for papers related to your syllabus.")

st.sidebar.header("Search")
api_key = st.sidebar.text_input(
    "Tavily Search API key",
    type="password",
    help="Enter your key here; do not send it in chat.",
)

subject = st.selectbox("Subject", list(COURSES.keys()))
course = COURSES[subject]
module = st.selectbox("Module", course["modules"])
topic = st.text_input("Optional chapter or topic", placeholder="e.g. Gauss elimination")

if "results" not in st.session_state:
    st.session_state.results = []

if st.button("Search for papers"):
    if not api_key:
        st.error("Enter a Tavily API key in the sidebar to search the web.")
    else:
        search_term = topic.strip() or module
        queries = []

        for code in course["codes"]:
            queries.append(
                f'site:sjec.ac.in "{code}" "{search_term}" question paper'
            )
            queries.append(
                f'"{code}" "{search_term}" SJEC Mangaluru past question paper PDF'
            )

        course_name = course["name"]
        queries.append(
            f'"Saint Joseph Engineering College" "{course_name}" '
            f'"{search_term}" question paper'
        )

        found = {}
        errors = []

        with st.spinner("Searching public sources..."):
            for query in queries:
                try:
                    for result in search_web(api_key, query):
                        url = result.get("url", "")
                        if url:
                            found[url] = result
                except requests.RequestException:
                    errors.append("A search request failed.")

        st.session_state.results = list(found.values())

        if errors and not st.session_state.results:
            st.error("Search failed. Check your internet connection and API key.")
        elif not st.session_state.results:
            st.info("No matching public results were found. Try a shorter topic name.")

if st.session_state.results:
    st.subheader("Search results")
    st.warning(
        "Open each source and check its course code, semester, year, and syllabus. "
        "A search result alone does not prove that it is an SJEC past paper."
    )

    for result in st.session_state.results:
        title = result.get("title") or "Untitled result"
        url = result.get("url", "")

        with st.expander(title):
            st.caption(source_label(url))
            if result.get("content"):
                st.write(result["content"])
            st.markdown(f"[Open original paper or page]({url})")
