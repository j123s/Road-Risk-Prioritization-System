"""
Flask API server for Road Risk System
"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
import pandas as pd
from data_processor import RoadDataProcessor
from sample_data import load_default_data, save_sample_data


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

app = Flask(
    __name__,
    template_folder=os.path.join(parent_dir, 'templates'),
    static_folder=os.path.join(parent_dir, 'static')
)
CORS(app)


UPLOAD_FOLDER = os.path.join(parent_dir, 'uploads')
TEMPLATE_FOLDER = os.path.join(parent_dir, 'templates')
STATIC_FOLDER = os.path.join(parent_dir, 'static')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMPLATE_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


processor = RoadDataProcessor()
master_processor = RoadDataProcessor()

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/api/areas', methods=['GET'])
def get_areas():
    try:
      
        data = load_default_data()

        areas = sorted(set(r["area"] for r in data))
        zones = sorted(set(r["zone"] for r in data))

        return jsonify({
            "areas": areas,
            "zones": zones
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/roads', methods=['GET'])
def get_roads():
    try:
        area = request.args.get('area')
        zone = request.args.get('zone')

        data = master_processor.roads

        if area:
            data = [r for r in data if r['area'].lower() == area.lower()]
        if zone:
            data = [r for r in data if r['zone'].lower() == zone.lower()]

        return jsonify({"roads": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload_csv():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.endswith(".csv"):
            return jsonify({"error": "Only CSV files are allowed"}), 400

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        df = pd.read_csv(filepath)

        required = [
            "road_id", "road_name", "area", "zone",
            "latitude", "longitude",
            "accidents", "traffic",
            "weather_vulnerability", "repair_cost"
        ]

        missing = [c for c in required if c not in df.columns]
        if missing:
            return jsonify({
                "error": "Missing required columns",
                "missing": missing
            }), 400

       
        numeric_cols = ["latitude", "longitude", "accidents", "traffic",
                        "weather_vulnerability", "repair_cost"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

       
        df = df.dropna(subset=["latitude", "longitude"])

        
        df.to_csv("road_data.csv", index=False)
        processor.load_from_csv("road_data.csv")
        processor.calculate_all_risk_scores()

        return jsonify({
            "success": True,
            "message": "CSV uploaded successfully",
            "roads_loaded": len(df)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        budget = float(data.get('budget', 1000000))
        area = data.get('area')
        zone = data.get('zone')
        use_default = data.get('use_default', True)

       
        if use_default:
            processor.roads = master_processor.roads.copy()

        processor.calculate_all_risk_scores()

        selected_roads, total_cost, remaining, risk_dist, all_roads = processor.prioritize_roads(
            budget, area, zone
        )

        stats = processor.get_statistics(all_roads)

        return jsonify({
            "success": True,
            "analysis": {
                "selected_roads": selected_roads,
                "all_roads": all_roads,
                "budget_used": total_cost,
                "budget_remaining": remaining,
                "budget_utilization": (total_cost / budget * 100) if budget > 0 else 0,
                "roads_selected": len(selected_roads),
                "roads_total": len(all_roads),
                "risk_distribution": risk_dist,
                "statistics": stats
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/generate-sample', methods=['POST'])
def generate_sample():
    try:
        df = save_sample_data()
        if df is not None:
            return jsonify({"success": True, "message": "Sample data generated"})
        else:
            return jsonify({"error": "Failed to generate sample data"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_FOLDER, path)


if __name__ == '__main__':
   
    master_processor.roads = load_default_data()
    master_processor.calculate_all_risk_scores()

   
    processor.roads = master_processor.roads.copy()

    print("\n" + "="*60)
    print("Road Risk System Backend Starting...")
    print("="*60)
    print("Dashboard: http://localhost:5000")
    print("API: http://localhost:5000/api")
    print("="*60 + "\n")

    app.run(debug=True, port=5000, host='0.0.0.0')
