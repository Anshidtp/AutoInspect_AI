# AutoInspect_AI

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-18.2+-61dafb.svg)
![YOLOv11](https://img.shields.io/badge/YOLOv11-Ultralytics-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**An intelligent system that automatically detects car damage using AI and provides instant repair cost estimates.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation)  • [API Docs](#-api-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## 🌟 Overview

This project provides an end-to-end solution for automated car damage assessment using computer vision and AI. Simply upload a photo of a damaged vehicle, and the system will:

1. **Detect** all visible damages using YOLOv11 object detection & Instance Segmentation
2. **Classify** damage severity (minor, moderate, severe)
3. **Estimate** repair costs with detailed breakdowns
4. **Generate** downloadable reports

**Perfect for:** Insurance companies, auto repair shops, car dealerships, rental services, and individual car owners.

---

## ✨ Features

### 🎯 Core Features

- **AI-Powered Detection**: YOLOv11-based damage detection with 11 damage types
- **11 Damage Categories**:
  - damaged-head-light
  - damaged-hood
  - damaged-trunk
  - damaged-window
  - damaged-windscreen
  - damaged_bumper
  - damaged_door
  - damaged_fender
  - damaged_mirror_glass
  - dent-or-scratch
  - missing_grille

- **Automatic Severity Classification**: Minor, Moderate, Severe
- **Part Identification**: Automatically identifies affected car parts
- **Cost Estimation**: Detailed breakdown of parts, labor, paint, and markup
- **RESTful API**: Clean, documented FastAPI backend
- **Modern Web Interface**: Beautiful React frontend with drag & drop
- **Real-time Processing**: Results in seconds
- **Export Reports**: Download cost estimates

### 💎 Technical Features

- **High Accuracy**: Trained YOLOv11 model with customizable confidence threshold
- **Scalable Architecture**: Modular design for easy extension
- **Database Storage**: Persistent storage of all detections and estimates
- **Error Handling**: Comprehensive error handling and validation
- **CORS Enabled**: Ready for cross-origin requests
- **Responsive UI**: Works on desktop, tablet, and mobile

---

## 🏗️ Architecture

```
┌─────────────┐      HTTP/REST      ┌──────────────┐
│   React     │ ◄──────────────────► │   FastAPI    │
│  Frontend   │      JSON API       │   Backend    │
└─────────────┘                     └──────────────┘
                                           │
                                           ├─► YOLOv11 Model
                                           ├─► SQLite Database
                                           └─► Cost Estimator

Flow:
1. User uploads image via React UI
2. Frontend sends to FastAPI endpoint
3. Backend processes with YOLOv8
4. Detections saved to database
5. Cost estimation calculated
6. Results returned to frontend
7. Beautiful visualization displayed
```

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.104+
- **ML/AI**: 
  - Ultralytics YOLOv11
  - PyTorch 2.1+
  - OpenCV 4.8+
- **Database**: SQLAlchemy + SQLite
- **Validation**: Pydantic v2
- **Server**: Uvicorn

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite 5
- **Styling**: Tailwind CSS 3
- **Animations**: Framer Motion
- **HTTP Client**: Axios
- **UI Components**: Lucide React icons
- **File Upload**: React Dropzone


---

## 🚀 Installation

### Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **npm**: 7 or higher
- **GPU** (optional): NVIDIA GPU with CUDA for faster training/inference

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Anshidtp/AutoInspect_AI.git
cd AutoInspect_AI

# Setup backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Setup frontend (in new terminal)
cd frontend
npm install
npm run dev
```

🎉 **Access the app:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---
```

## 📖 Usage

### Web Interface

1. **Open Browser**: Navigate to http://localhost:3000

2. **Upload Image**:
   - Drag & drop a car image
   - Or click to browse files
   - Supported formats: JPG, JPEG, PNG

3. **Detect Damages**:
   - Click "Detect Damage" button
   - Wait for AI processing (1-3 seconds)
   - View detected damages with confidence scores

4. **Get Cost Estimation**:
   - Click "Get Cost Estimation" button
   - View detailed breakdown:
     - Parts cost
     - Labor cost (hours × rate)
     - Paint cost
     - Markup
     - **Total repair cost**

5. **Download Report**:
   - Click download button
   - Save cost estimation report

### API Usage

#### Detect Damages

```bash
curl -X POST "http://localhost:8000/api/v1/detections/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@car_damage.jpg" \
  -F "confidence_threshold=0.25"
```

#### Create Cost Estimation

```bash
curl -X POST "http://localhost:8000/api/v1/estimations/" \
  -H "Content-Type: application/json" \
  -d '{
    "detection_id": 1,
    "include_paint": true
  }'
```


## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Upload & Detect

**POST** `/detections/`

**Request:**
- **Content-Type**: `multipart/form-data`
- **Body**:
  - `file`: Image file (required)
  - `confidence_threshold`: float 0-1 (optional, default: 0.25)
  - `detect_severity`: boolean (optional, default: true)

**Response:**
```json
{
  "detection_id": 1,
  "image_filename": "car.jpg",
  "image_dimensions": {"width": 1920, "height": 1080},
  "damages_detected": [
    {
      "damage_type": "damaged_bumper",
      "severity": "moderate",
      "confidence": 0.87,
      "affected_part": "bumper",
      "bbox_x": 0.45,
      "bbox_y": 0.32,
      "bbox_width": 0.15,
      "bbox_height": 0.18
    }
  ],
  "total_damages": 1,
  "processing_time": 1.23,
  "model_version": "YOLOv8",
  "timestamp": "2024-01-23T10:30:00"
}
```

#### 2. Get Detection by ID

**GET** `/detections/{detection_id}`

**Response:** Full detection record with all damages

#### 3. List Detections

**GET** `/detections/?page=1&page_size=10`

**Response:** Paginated list of detection records

#### 4. Create Cost Estimation

**POST** `/estimations/`

**Request:**
```json
{
  "detection_id": 1,
  "labor_rate_override": 80.0,  // optional
  "markup_override": 25.0,       // optional
  "include_paint": true
}
```

**Response:**
```json
{
  "estimation_id": 1,
  "detection_id": 1,
  "parts_cost": 400.00,
  "labor_cost": 375.00,
  "paint_cost": 600.00,
  "markup": 275.00,
  "total_cost": 1650.00,
  "estimated_labor_hours": 5.0,
  "labor_rate": 75.00,
  "markup_percentage": 20.0,
  "damage_items": [...],
  "created_at": "2024-01-23T10:31:00"
}
```

#### 5. Get Estimation Summary

**GET** `/estimations/summary/{detection_id}`

**Response:**
```json
{
  "detection_id": 1,
  "total_damages": 3,
  "total_cost": 1650.00,
  "estimated_repair_time": "2-3 days",
  "severity_breakdown": {
    "minor": 1,
    "moderate": 2,
    "severe": 0
  }
}
```

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ⚙️ Configuration

### Backend Configuration ()

```env
# Application
APP_NAME="AutoInspect_AI API"
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./data/app.db

# ML Model
MODEL_PATH="model/best.pt"
MODEL_CONFIDENCE_THRESHOLD=0.25
MODEL_IOU_THRESHOLD=0.45

# Cost Estimation
LABOR_RATE_PER_HOUR=75.0
MARKUP_PERCENTAGE=20.0

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
```

### Model Configuration

**Confidence Threshold** (`0.25`):
- Lower (0.15-0.2): More detections, may include false positives
- **Recommended (0.25-0.3)**: Good balance
- Higher (0.5-0.7): Fewer detections, only confident ones

**IOU Threshold** (`0.45`):
- Controls duplicate detection removal
- Standard YOLO default works well

### Cost Database

Edit `data/damage_costs.json` to customize repair costs:

```json
{
  "damaged_bumper": {
    "moderate": {
      "parts": 400,
      "labor_hours": 3.0,
      "paint": 400
    }
  }
}
```
---

## 🤝 Contributing

We welcome contributions! Here's how:

### Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/Anshidtp/AutoInspect_AI.git
   ```
3. **Create** a branch:
   ```bash
   git checkout -b feature/amazing-feature
   ```
4. **Make** your changes
5. **Test** thoroughly
6. **Commit**:
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push**:
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Open** a Pull Request

### Contribution Guidelines

- Follow PEP 8 for Python code
- Use ESLint config for JavaScript
- Write tests for new features
- Update documentation
- Keep commits atomic and well-described

### Areas for Contribution

- 🎯 Improve model accuracy
- 🎨 Enhance UI/UX design
- 📱 Add mobile app
- 🌍 Multi-language support
- 📊 Advanced analytics dashboard
- 🔐 Authentication system
- 📄 PDF report generation
- 🎥 Video damage detection

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Car Damage Detection Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Acknowledgments

- **Ultralytics** for YOLOv11
- **FastAPI** team for the amazing framework
- **React** team for the UI library
- **Tailwind CSS** for styling utilities
- **OpenCV** community

---

## 📞 Contact & Support

- **Email**: connect.anshid@gmail.com
- **Issues**: [GitHub Issues](https://github.com/yourusername/car-damage-detection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/car-damage-detection/discussions)

---

## 🗺️ Roadmap

### Version 1.0 ✅
- [x] YOLOv11 damage detection
- [x] 11 damage types support
- [x] Cost estimation engine
- [x] FastAPI backend
- [x] React frontend
- [x] Basic documentation

### Version 1.1 (Q2 2024)
- [ ] PDF report generation
- [ ] Email notifications
- [ ] User authentication
- [ ] Multi-language support
- [ ] Mobile responsive improvements

### Version 2.0 (Q3 2024)
- [ ] Video damage detection
- [ ] 3D damage visualization
- [ ] Mobile apps (iOS/Android)
- [ ] Advanced analytics dashboard
- [ ] Integration with insurance APIs

### Future
- [ ] Real-time camera detection
- [ ] AR damage overlay
- [ ] Blockchain verification
- [ ] AI-powered repair recommendations

---

## 📊 Performance

### Model Performance
- **Accuracy (mAP@0.5)**: 0.78
- **Inference Speed**: 0.5-2 seconds per image
- **Supported Image Sizes**: Up to 10MB
- **Concurrent Users**: 50+ (depends on hardware)

### System Requirements

**Minimum (CPU):**
- 4GB RAM
- 2 CPU cores
- 10GB storage

**Recommended (GPU):**
- 8GB RAM
- 4 CPU cores
- NVIDIA GPU with 4GB+ VRAM
- 20GB storage

---

## 🎯 Use Cases

1. **Insurance Companies**
   - Automated claim processing
   - Fraud detection
   - Quick damage assessment

2. **Auto Repair Shops**
   - Instant cost quotes
   - Customer communication
   - Inventory planning

3. **Car Dealerships**
   - Used car inspection
   - Trade-in valuation
   - Quality assurance

4. **Rental Services**
   - Damage documentation
   - Return inspection
   - Dispute resolution

5. **Individual Users**
   - Pre-purchase inspection
   - Insurance claims
   - Repair cost estimation

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

<div align="center">

**Made with ❤️ by the AutoInspect Team**

[⬆ Back to Top](#AutoInspect_AI)

</div>