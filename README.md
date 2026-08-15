# TyreIQ — Mining Dumper Tyre Intelligence System 🚜⚙️

> **SIH Problem Statement 1557**: Explainable Mining Dumper Tyre Intelligence Platform with IIoT Telemetry, Mamdani Fuzzy Risk Engine, Ultralytics YOLO Damage Detection, and Exposure-Normalized Mine-Road Hotspot Analytics.

---

## 1. System Architecture

```
                       +-----------------------------+
                       |   React + Vite Frontend     |
                       |   (http://localhost:3000)   |
                       +--------------+--------------+
                                      |  Axios API Calls
                                      v
                       +-----------------------------+
                       |   FastAPI REST Backend      |
                       |   (http://localhost:8000)   |
                       +--------------+--------------+
                                      |
     +--------------------------------+--------------------------------+
     |                                |                                |
     v                                v                                v
+----+-----------------+   +----------+---------+   +------------------+----------------+
| SQLAlchemy Database  |   | Mosquitto MQTT     |   | Computer Vision YOLO Pipeline  |
| (Postgres / SQLite)  |   | Telemetry Stream  |   | (preprocessing/quality/severity|
+----------------------+   +--------------------+   +--------------------------------+
     |                                                                 |
     v                                                                 v
+----+-----------------+   +--------------------+   +------------------+----------------+
| Analytics ML Core    |   | IMU Impact Engine  |   | Mamdani Fuzzy Risk Engine      |
| (TKPH/Thermal/Wear)  |   | (resultant/jerk)   |   | (6 stress dimensions -> HIGH)  |
+----------------------+   +----------+---------+   +------------------+----------------+
                                      |                                |
                                      v                                v
                            +---------+----------+  +------------------+----------------+
                            | GeoJSON Hotspot    |  | Maintenance Priority Queue &   |
                            | Road Segment Map   |  | Alert Center Feed              |
                            +--------------------+  +--------------------------------+
```

---

## 2. Prerequisites

- **Python**: `3.11` or `3.14`
- **Node.js**: `v18.0+` or `v20.0+` & `npm`
- **Docker & Docker Compose**: (Optional, for containerized deployment)

---

## 3. Installation

Clone repository and navigate into project directory:
```bash
git clone https://github.com/Sohammire/SIH-TEAM-FRAG.git
cd SIH-TEAM-FRAG
```

---

## 4. Environment Variables

### Backend (`backend/.env`):
```ini
DATABASE_URL=sqlite:///./tyreiq.db
# For PostgreSQL: postgresql://tyreiq_user:tyreiq_password@localhost:5432/tyreiq_db
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
DEBUG=True
```

### Frontend (`frontend/.env`):
```ini
VITE_API_URL=http://localhost:8000/api/v1
VITE_USE_MOCK=false
```

---

## 5. Database Setup

The backend uses SQLAlchemy ORM with automatic schema creation and baseline seeding on startup.
- **SQLite (Default)**: Auto-created at `backend/tyreiq.db`
- **PostgreSQL (Production)**: Supported out of the box via `DATABASE_URL`

---

## 6. MQTT Setup

Mosquitto MQTT broker handles real-time IIoT telemetry ingestion on port `1883`.
Topic structure:
- `mine/{mine_id}/truck/{truck_id}/tyre/{tyre_id}/telemetry`
- `mine/{mine_id}/truck/{truck_id}/imu`
- `mine/{mine_id}/truck/{truck_id}/gps`
- `mine/{mine_id}/tyre/{tyre_id}/inspection`
- `mine/{mine_id}/alerts`

---

## 7. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:3000
```

---

## 8. Backend Setup

```bash
cd backend
py -3 -m pip install -r requirements.txt
py -3 -m uvicorn app.main:app --port 8000
# Server runs at http://localhost:8000
```

---

## 9. ML Core Setup

All ML dependencies (`scikit-learn`, `scikit-fuzzy`, `ultralytics`, `opencv-python`, `shapely`, `pandas`, `numpy`) are installed automatically via `requirements.txt`.
- **Mamdani Fuzzy Risk Engine**: Uses `scikit-fuzzy` for explainable centroid defuzzification.
- **Computer Vision**: Ultralytics YOLOv8 with custom quality check guardrail (blur & darkness detection).
- **Thermal & Wear Models**: Ridge Regression with 70/30 chronological split and Huber Regressor with GroupKFold by `tyre_id`.

---

## 10. Running Simulator

To trigger synthetic multi-scenario telemetry stream (8 scenarios: `normal_cycle`, `pressure_leak`, `high_payload_high_speed`, `high_temperature`, `impact_cluster`, `sidewall_damage_pressure_loss`, `worn_tyre`, `sensor_dropout`):

```bash
curl -X POST http://localhost:8000/api/v1/telemetry/simulate -H "Content-Type: application/json" -d "{\"scenario_id\": \"pressure_leak\"}"
```

---

## 11. Running Complete SIH Demonstration

Run the automated end-to-end demonstrator script:
```bash
cd backend
py -3 scripts/demo_e2e_scenario.py
```

---

## 12. API Documentation

Interactive Swagger OpenAPI docs available at: **http://localhost:8000/docs**

Key Endpoints:
- `GET /api/v1/health` — System health check
- `GET /api/v1/dashboard/summary` — Aggregated KPIs
- `POST /api/v1/telemetry` — Ingest sensor telemetry
- `GET /api/v1/tyres/{tyre_id}/risk` — Mamdani fuzzy risk score, reasons & recommended action
- `POST /api/v1/vision/predict` — YOLO damage detection & quality check
- `GET /api/v1/hotspots` — Exposure-normalized road segment hotspots per 100 truck-km
- `GET /api/v1/maintenance/priorities` — Priority-ranked maintenance queue

---

## 13. Testing

Run complete Pytest test suite (42 automated unit and integration test cases):
```bash
cd backend
py -3 -m pytest -v
```

---

## 14. Docker Deployment

Launch full containerized system (Frontend, Backend, PostgreSQL, Mosquitto MQTT) with health checks:
```bash
docker-compose up --build -d
```
- Frontend: **http://localhost:3000**
- Backend API: **http://localhost:8000**
- PostgreSQL: **port 5432**
- MQTT Broker: **port 1883**