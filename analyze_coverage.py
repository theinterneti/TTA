#!/usr/bin/env python3
"""Analyze coverage by component from test output."""

# Logseq: [[TTA.dev/Analyze_coverage]]

import re
from collections import defaultdict

# Read test output
with open("test_run_output.txt") as f:
    lines = f.readlines()

# Find coverage section
coverage_started = False
component_data = defaultdict(lambda: {"stmts": 0, "miss": 0, "branch": 0, "brpart": 0})

for line in lines:
    # Match lines like: src/agent_orchestration/...  numbers ...
    if line.startswith("src/"):
        match = re.match(
            r"(src/[^/]+)/.*?\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)%", line
        )
        if match:
            component = match.group(1)
            stmts = int(match.group(2))
            miss = int(match.group(3))
            branch = int(match.group(4))
            brpart = int(match.group(5))

            component_data[component]["stmts"] += stmts
            component_data[component]["miss"] += miss
            component_data[component]["branch"] += branch
            component_data[component]["brpart"] += brpart

# Calculate and print component coverage

sorted_components = sorted(
    component_data.items(),
    key=lambda x: (x[1]["stmts"] - x[1]["miss"]) / x[1]["stmts"]
    if x[1]["stmts"] > 0
    else 0,
    reverse=True,
)

for component, data in sorted_components:
    if data["stmts"] > 0:
        coverage = ((data["stmts"] - data["miss"]) / data["stmts"]) * 100
        covered = data["stmts"] - data["miss"]
