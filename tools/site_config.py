"""Shared settings for tools/build_pages.py and tools/build_reports.py."""

REPO = "trungly-hcmut/CO5177_DataVisualization_Assignment"
GITHUB_BLOB = f"https://github.com/{REPO}/blob/main"
PAGES_URL = "https://trungly-hcmut.github.io/CO5177_DataVisualization_Assignment/"

# Paste the YouTube link of each presentation here (Public or Unlisted),
# then re-run tools/build_pages.py and tools/build_reports.py.
VIDEO_URLS = {
    "tabular": None,
    "text": None,
    "timeseries": None,
}

# Show member roles on the project pages? (temporarily hidden; the PDF report covers still list them)
SHOW_ROLES = False

# Main contribution of each member, shown on the PDF report covers (keyed by student ID)
CONTRIBUTIONS = {
    "2570349": "Tabular and time-series analysis; website design and deployment",
    "2570441": "Text analysis (Vietnamese news classification)",
    "2570261": "Text analysis (Vietnamese news classification)",
}

# (name, student ID, role, initials, avatar colour on the web pages)
MEMBERS = [
    ("Ly Minh Trung", "2570349", "Data Scientist", "LT", "var(--lime)"),
    ("Dinh Truong Tue Linh", "2570441", "Data Scientist", "DT", "var(--peach)"),
    ("Nguyen Hoang Nam", "2570261", "Analysis and Visualization", "NH", "var(--blue)"),
]
