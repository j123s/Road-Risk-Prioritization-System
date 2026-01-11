import pandas as pd
from risk_score import calculate_risk_score, categorize_risk

class RoadDataProcessor:
    def __init__(self):
        self.roads = []

    def load_from_csv(self, filepath):
        try:
            df = pd.read_csv(filepath)
            self.roads = df.to_dict('records')
            return True, "Data loaded successfully"
        except Exception as e:
            return False, f"Error loading CSV: {str(e)}"

    def calculate_all_risk_scores(self):
        for road in self.roads:
            road['risk_score'] = float(calculate_risk_score(road))
            road['risk_category'] = categorize_risk(road['risk_score'])

    def prioritize_roads(self, budget, area=None, zone=None):
        filtered_roads = self.roads.copy()

        if area:
            filtered_roads = [r for r in filtered_roads if r['area'].lower() == area.lower()]

        if zone:
            filtered_roads = [r for r in filtered_roads if r['zone'].lower() == zone.lower()]

        if not filtered_roads:
            return [], 0.0, budget, {"High": 0, "Medium": 0, "Low": 0}, []

        sorted_roads = sorted(filtered_roads, key=lambda x: x['risk_score'], reverse=True)

        selected_roads = []
        total_cost = 0.0
        remaining_budget = float(budget)

        for road in sorted_roads:
            cost = float(road['repair_cost'])
            if cost <= remaining_budget:
                selected_roads.append(road)
                total_cost += cost
                remaining_budget -= cost

        risk_distribution = {
            "High": int(len([r for r in sorted_roads if r['risk_category'] == "High"])),
            "Medium": int(len([r for r in sorted_roads if r['risk_category'] == "Medium"])),
            "Low": int(len([r for r in sorted_roads if r['risk_category'] == "Low"]))
        }

        return selected_roads, total_cost, remaining_budget, risk_distribution, sorted_roads

    def get_statistics(self, roads=None):
        if roads is None:
            roads = self.roads

        if not roads:
            return {
                "total_roads": 0,
                "avg_risk_score": 0.0,
                "total_repair_cost": 0.0,
                "avg_accidents": 0.0,
                "avg_traffic": 0.0
            }

        df = pd.DataFrame(roads)

        return {
            "total_roads": int(len(roads)),
            "avg_risk_score": float(df['risk_score'].mean()),
            "total_repair_cost": float(df['repair_cost'].sum()),
            "avg_accidents": float(df['accidents'].mean()),
            "avg_traffic": float(df['traffic'].mean())
        }
