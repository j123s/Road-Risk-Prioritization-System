"""
Road Infrastructure Risk & Repair Prioritization System
Round-1 Prototype

Purpose:
Demonstrate core decision logic for risk-based road repair prioritization
using mock data and a budget constraint.
"""

import pandas as pd

# -------------------------------
# Mock road-level data
# -------------------------------
data = {
    "road_id": ["R1", "R2", "R3", "R4"],
    "accidents": [10, 4, 7, 12],
    "traffic": [0.8, 0.4, 0.6, 0.9],
    "weather": [0.5, 0.3, 0.4, 0.6],
    "repair_cost": [50, 30, 40, 60]
}

df = pd.DataFrame(data)

# -------------------------------
# Data normalization (0–1 scale)
# -------------------------------
df["A"] = df["accidents"] / df["accidents"].max()
df["T"] = df["traffic"]
df["W"] = df["weather"]

# -------------------------------
# Risk score weights (sum to 1)
# -------------------------------
W_ACCIDENT = 0.5
W_TRAFFIC = 0.3
W_WEATHER = 0.2

# -------------------------------
# Risk score calculation
# -------------------------------
df["risk_score"] = (
    W_ACCIDENT * df["A"]
    + W_TRAFFIC * df["T"]
    + W_WEATHER * df["W"]
)

# -------------------------------
# Cost-aware prioritization (ROI)
# -------------------------------
df["priority_score"] = df["risk_score"] / df["repair_cost"]

# -------------------------------
# Rank roads by priority score
# -------------------------------
df_sorted = df.sort_values(
    by="priority_score", ascending=False
)

# -------------------------------
# Budget constraint
# -------------------------------
TOTAL_BUDGET = 100
used_budget = 0
selected_roads = []

for _, road in df_sorted.iterrows():
    if used_budget + road["repair_cost"] <= TOTAL_BUDGET:
        selected_roads.append(road)
        used_budget += road["repair_cost"]

# -------------------------------
# Output results
# -------------------------------
print("\nPriority Road Repair List (Round-1 Prototype)\n")

for road in selected_roads:
    print(
        f"Road {road['road_id']} | "
        f"Risk Score: {road['risk_score']:.3f} | "
        f"Cost: {road['repair_cost']}"
    )

print("\nTotal Budget Used:", used_budget)
print("Remaining Budget:", TOTAL_BUDGET - used_budget)
