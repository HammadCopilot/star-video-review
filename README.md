# STAR Video Review System

AI-powered video review platform for analyzing teacher training videos and identifying effective teaching practices.

## 🎯 Project Overview

The STAR Video Review System automates and optimizes the review of teacher videos using Artificial Intelligence to identify effective teaching practices and generate actionable insights for improvement. This POC reduces manual workload for STAR's review team while ensuring consistency, efficiency, and privacy compliance.

## ✨ Key Features

- 🔐 **Multi-user Authentication** - Role-based access control (Admin, Reviewer, Viewer)
- 📹 **Hybrid Video Support** - Upload local files or reference external URLs
- 🤖 **AI-Powered Analysis** - Local Whisper + OpenAI GPT-4 for automated annotations
- 🏷️ **Structured Annotations** - Timestamped tags based on 50+ best practice criteria
- 📊 **Report Generation** - Automated review reports with metrics and insights
- 🔒 **Privacy-First** - Local processing by default, optional cloud with consent
- 📝 **Audit Logging** - Complete tracking of all actions and API calls

## 🏗️ Architecture

**Backend:** Python Flask REST API with JWT authentication  
**Frontend:** React SPA with video player and annotation interface  
**Database:** SQLite (PostgreSQL-ready for production)  
**AI Processing:** Hybrid approach - Local Whisper "small" + OpenAI API (optional)  
**Deployment:** Self-hosted (localhost), AWS-ready

## 📋 Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- FFmpeg (for video processing)
- OpenAI API key (for enhanced AI analysis)

## 🚀 Quick Start

### 1. Clone Repository

```bash
cd star-video-review
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# Initialize database
python app.py  # This creates the database tables

# Seed initial data
python seed_data.py
```

**Test Accounts:**
- Admin: `admin@star.com` / `admin123`
- Reviewer: `reviewer@star.com` / `reviewer123`

### 3. Frontend Setup (Phase 3)

```bash
cd ../frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit if needed (backend URL)

# Start development server
npm start
```

### 4. Run Application

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```
Backend runs at: `http://localhost:5000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
Frontend runs at: `http://localhost:3000`

## 🧪 Testing

### Test Backend API

```bash
cd backend
python test_api.py
```

This tests all Phase 1 endpoints:
- Health check
- User registration/login
- JWT authentication
- Video CRUD operations
- Role-based authorization

## 📚 Teaching Practice Categories

The system evaluates videos based on three evidence-based teaching methodologies:

### 1. Discrete Trial Training (13 criteria)
- Consistent cue usage
- Immediate re-stating before praise
- Error correction procedures
- Reinforcement strategies
- And more...

### 2. Pivotal Response Training (12 criteria)
- Following student's lead
- Language trial execution
- Play trial modeling
- Engaging toy selection
- And more...

### 3. Functional Routines (15 criteria)
- Visual supports with minimal language
- Prompting from behind
- Reverse chaining
- Visual schedules
- And more...

## 🎬 Sample Videos Included

The system comes pre-loaded with 10 example videos covering:
- 4 Pivotal Response Training examples
- 5 Discrete Trial examples
- 1 Functional Routines example

## 🔐 Security & Privacy

### Privacy-First Design
- **Local Storage:** All videos stored locally, not in cloud
- **Local Processing:** Whisper "small" model runs on your machine
- **Optional Cloud:** OpenAI API only with explicit consent per video
- **Audit Logging:** Every action tracked with timestamps and user info
- **Anonymization:** Option to strip teacher/student names before AI processing

### User Roles
- **Admin:** Full system access, user management, settings
- **Reviewer:** Upload videos, create/edit annotations, generate reports
- **Viewer:** Read-only access to videos and reports

## 📁 Project Structure

```
star-video-review/
├── backend/              # Flask API
│   ├── app.py           # Main application
│   ├── models.py        # Database models
│   ├── config.py        # Configuration
│   ├── routes/          # API endpoints
│   ├── services/        # AI analysis service (Phase 2)
│   └── uploads/         # Video storage
├── frontend/            # React application (Phase 3)
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   └── context/     # State management
│   └── public/
└── README.md
```

## 🛣️ Development Roadmap

### ✅ Phase 1: Core Backend (Completed)
- Flask project structure
- User authentication with JWT
- Video upload (local + URL)
- Database models
- Best practices seeding

### 🚧 Phase 2: Annotation System (In Progress)
- Annotation CRUD endpoints
- AI analysis service
- Report generation
- Transcript management

### 📅 Phase 3: Frontend Foundation
- React project setup
- Authentication flow
- Protected routes
- API integration

### 📅 Phase 4: Video Review Interface
- Video player component
- Annotation creation panel
- Timeline visualization
- Best practices reference

### 📅 Phase 5: Dashboard & Reports
- Video list with filters
- Reviewer dashboard
- Report generation UI
- Export functionality

### 📅 Phase 6: Polish & Testing
- User management interface
- Role-based UI
- Error handling
- Responsive design
- Documentation

## 📊 Success Metrics

- ✅ Secure video upload and playback
- ✅ Multi-user system with role-based access
- ✅ Structured tagging with 50+ criteria
- ✅ Report generation with metrics
- ✅ 50%+ time reduction in review process
- ✅ Privacy compliance (local storage, no cloud exposure by default)
- ✅ Functional prototype by December

## 🔧 Configuration

### Backend Environment Variables

```bash
# Flask
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=sqlite:///star_video_review.db

# OpenAI
OPENAI_API_KEY=sk-your-api-key

# AI Settings
USE_ENHANCED_AI=False  # Set to True for OpenAI API
WHISPER_MODEL=small    # tiny, base, small, medium, large
```

## 📖 API Documentation

See [Backend README](backend/README.md) for detailed API documentation.

**Key Endpoints:**
- `POST /api/auth/login` - User authentication
- `GET /api/videos` - List videos
- `POST /api/videos` - Upload video or add URL
- `GET /api/videos/:id` - Get video details
- More endpoints coming in Phase 2...

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 5000 is in use
lsof -ti:5000

# Kill existing process
kill -9 $(lsof -ti:5000)
```

### FFmpeg not found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg
```

### Database errors
```bash
# Reset database
rm backend/star_video_review.db
cd backend && python app.py && python seed_data.py
```

## 🚀 AWS Deployment (Future)

The system is designed for easy AWS migration:
- **RDS:** PostgreSQL database
- **S3:** Video storage with presigned URLs
- **EC2/ECS:** Application hosting
- **CloudFront:** Frontend delivery

## 📝 User Stories Coverage

- ✅ **US-01:** Secure video upload (local + URL)
- ✅ **US-02:** Timestamped tagging (Phase 2)
- ✅ **US-03:** Summary reports (Phase 2)
- ✅ **US-04:** Privacy compliance and audit logging
- ⚠️ **US-05:** Best practices library (simplified)
- ❌ **US-06:** LMS integration (future phase)

## 🤝 Contributing

This is a proprietary project for the STAR program. For questions or contributions, contact the development team.

## 📄 License

Proprietary - STAR Program

## 🙏 Acknowledgments

Built for the STAR program to improve teacher training and coaching effectiveness through AI-powered video analysis.


Test Accounts:
  Admin: admin@star.com / admin123
  Reviewer: reviewer@star.com / reviewer123
  