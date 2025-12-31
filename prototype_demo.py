
roads = [
    {"name": "Road A", "accidents": 12, "traffic": 3, "cost": 40},
    {"name": "Road B", "accidents": 5,  "traffic": 2, "cost": 25},
    {"name": "Road C", "accidents": 9,  "traffic": 1, "cost": 30},
    {"name": "Road D", "accidents": 15, "traffic": 3, "cost": 50}
]


accident_weight = 0.6
traffic_weight = 0.4


for road in roads:
    road["risk_score"] = (
        accident_weight * road["accidents"]
        + traffic_weight * road["traffic"]
    )


roads.sort(key=lambda r: r["risk_score"], reverse=True)

budget = 80
used_budget = 0
selected = []

for road in roads:
    if used_budget + road["cost"] <= budget:
        selected.append(road)
        used_budget += road["cost"]

print("Priority Road Repair List :\n")

for r in selected:
    print(
        f"{r['name']} | "
        f"Risk Score: {r['risk_score']} | "
        f"Repair Cost: {r['cost']}"
    )

print("\nBudget Used:", used_budget)
print("Remaining Budget:", budget - used_budget)

