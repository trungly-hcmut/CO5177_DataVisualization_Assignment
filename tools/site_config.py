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

# (name, student ID, role, initials, avatar colour on the web pages)
MEMBERS = [
    ("Ly Minh Trung", "2570349", "Data Scientist", "LT", "var(--lime)"),
    ("Dinh Truong Tue Linh", "2570441", "Data Scientist", "DT", "var(--peach)"),
    ("Nguyen Hoang Nam", "2570261", "Analysis and Visualization", "NH", "var(--blue)"),
]
