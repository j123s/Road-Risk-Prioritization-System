"""
Risk score calculation module
Each road gets a score from 0-100 based on multiple factors
Higher score = higher priority for repair
"""
import numpy as np

def calculate_risk_score(road_data):
    """
    Calculate comprehensive risk score using weighted factors
    Formula: Risk = (0.35 * Accidents) + (0.25 * Traffic) + 
                   (0.20 * Weather) + (0.20 * (Cost_Normalized))
    
    All factors normalized to 0-100 scale
    """
    try:
        # Extract factors with defaults
        accidents = road_data.get('accidents', 0)
        traffic = road_data.get('traffic', 0)
        weather = road_data.get('weather_vulnerability', 0)
        cost = road_data.get('repair_cost', 100000)
        
        # Debug print to see what values we're getting
        # print(f"Processing road: accidents={accidents}, traffic={traffic}, weather={weather}, cost={cost}")
        
        # Normalize factors (example normalization - can be adjusted)
        # Accidents: Assume 0-50 accidents per year range
        accidents_score = min(accidents / 50 * 100, 100) if accidents > 0 else 0
        
        # Traffic: Assume 0-10000 vehicles per day range
        traffic_score = min(traffic / 10000 * 100, 100) if traffic > 0 else 0
        
        # Weather vulnerability: Already 0-100 scale
        weather_score = weather
        
        # Cost: Lower cost = higher priority, so inverse relationship
        # Assume cost range: 10,000 to 1,000,000
        cost_normalized = max(0, 100 - ((cost - 10000) / (1000000 - 10000) * 100))
        
        # Weighted sum
        risk_score = (
            0.35 * accidents_score +
            0.25 * traffic_score +
            0.20 * weather_score +
            0.20 * cost_normalized
        )
        
        return round(risk_score, 2)
    except Exception as e:
        print(f"Error calculating risk score: {e}")
        return 0

def categorize_risk(score):
    """Categorize risk into High, Medium, Low"""
    if score >= 70:
        return "High"
    elif score >= 40:
        return "Medium"
    else:
        return "Low"