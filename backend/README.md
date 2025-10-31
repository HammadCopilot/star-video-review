# STAR Video Review - Backend API

Flask-based REST API for the STAR Video Review system with JWT authentication, video management, and AI analysis capabilities.

## Features

- 🔐 JWT-based authentication with role-based access control
- 📹 Video upload (local files) and external URL support
- 🏷️ Video annotation with timestamped tags
- 🤖 Hybrid AI analysis (local Whisper + OpenAI API)
- 📊 Review tracking and report generation
- 🔒 Privacy-first design with audit logging

## Tech Stack

- **Framework:** Flask 3.x
- **Database:** SQLAlchemy with SQLite (PostgreSQL ready)
- **Authentication:** Flask-JWT-Extended
- **Video Processing:** FFmpeg, MoviePy, OpenCV
- **AI/ML:** OpenAI API, Whisper (local model)

## Installation

### Prerequisites

- Python 3.9 or higher
- FFmpeg (for video processing)

### Setup

1. **Clone and navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your settings, especially OPENAI_API_KEY
```

5. **Initialize database:**
```bash
python app.py  # Creates database tables automatically
```

6. **Seed initial data:**
```bash
python seed_data.py
```

This creates:
- Admin user: `admin@star.com` / `admin123`
- Reviewer user: `reviewer@star.com` / `reviewer123`
- 50+ best practice criteria
- 10 sample videos from provided URLs

## Running the Server

### Development Mode

```bash
python app.py
```

Server runs at: `http://localhost:5001` (using port 5001 to avoid macOS AirPlay conflict)

### Production Mode

```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login and get JWT | No |
| POST | `/api/auth/refresh` | Refresh access token | Refresh token |
| GET | `/api/auth/me` | Get current user | Yes |
| GET | `/api/auth/users` | Get all users (admin) | Yes (Admin) |
| PUT | `/api/auth/users/:id` | Update user | Yes |
| DELETE | `/api/auth/users/:id` | Delete user (admin) | Yes (Admin) |

### Videos

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/videos` | List all videos | Yes |
| GET | `/api/videos/:id` | Get single video | Yes |
| POST | `/api/videos` | Upload video or add URL | Yes |
| PUT | `/api/videos/:id` | Update video metadata | Yes |
| DELETE | `/api/videos/:id` | Delete video | Yes |
| GET | `/api/videos/:id/stream` | Stream video file | Yes |

### Query Parameters for `/api/videos`:
- `category` - Filter by category (discrete_trial, pivotal_response, functional_routines)
- `status` - Filter by analysis status
- `uploader_id` - Filter by uploader
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 20)

## Example API Calls

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "role": "reviewer"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@star.com",
    "password": "admin123"
  }'
```

### Upload Video (External URL)
```bash
curl -X POST http://localhost:5000/api/videos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "title": "My Training Video",
    "url": "https://example.com/video.mp4",
    "category": "discrete_trial",
    "description": "Example video"
  }'
```

### Upload Video (Local File)
```bash
curl -X POST http://localhost:5000/api/videos \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/video.mp4" \
  -F "title=My Video" \
  -F "category=discrete_trial"
```

### List Videos
```bash
curl -X GET "http://localhost:5000/api/videos?category=discrete_trial&page=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## User Roles

- **Admin**: Full system access, user management, all videos
- **Reviewer**: Upload videos, create annotations, generate reports
- **Viewer**: Read-only access to videos and reports

## Database Models

### User
- Email, password (hashed), role, name
- Relationships: videos, annotations, reviews

### Video
- Title, description, source (local/url), category
- Duration, thumbnail, analysis status
- Relationships: annotations, reviews, transcript

### Annotation
- Video reference, timestamp range (start/end)
- Practice category, best practice reference
- Comment, type (manual/ai), status, confidence

### BestPractice
- Category, title, description, criteria
- Positive/negative indicator, display order

### Review
- Video + reviewer reference
- Status, notes, timestamps

### Transcript
- Video reference, content, method
- Language, confidence, processing time

### AuditLog
- User, action, resource tracking
- IP address, timestamp, details

## Privacy & Security

### Local Processing (Default)
- Videos stored in `backend/uploads/` directory
- Local Whisper model for transcription
- No external API calls for video/audio processing

### Enhanced Mode (Optional)
- Requires explicit user consent per video
- Uses OpenAI Whisper API for faster transcription
- GPT-4 Vision for visual analysis
- All API calls logged in audit trail

### Security Features
- Password hashing with bcrypt
- JWT token authentication
- Role-based access control
- CORS protection
- Audit logging for all actions

## File Structure

```
backend/
├── app.py                 # Flask application factory
├── config.py              # Configuration management
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── seed_data.py          # Database seeding script
├── .env                  # Environment variables
├── routes/
│   ├── __init__.py
│   ├── auth.py           # Authentication endpoints
│   ├── videos.py         # Video management endpoints
│   ├── annotations.py    # (Phase 2)
│   ├── reports.py        # (Phase 2)
│   └── practices.py      # (Phase 2)
├── services/
│   └── ai_analyzer.py    # (Phase 2 - AI processing)
├── uploads/              # Local video storage
└── models/               # AI model storage
```

## Environment Variables

```bash
# Flask
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key

# JWT
JWT_SECRET_KEY=your-jwt-secret

# Database
DATABASE_URL=sqlite:///star_video_review.db

# File Upload
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=2147483648  # 2GB

# OpenAI
OPENAI_API_KEY=sk-...

# AI Settings
USE_ENHANCED_AI=False
WHISPER_MODEL=small
```

## Development

### Running Tests
```bash
python test_api.py
```

### Database Reset
```bash
rm star_video_review.db
python app.py
python seed_data.py
```

## Troubleshooting

### FFmpeg Not Found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Port Already in Use
```bash
# Find process using port 5000
lsof -ti:5000

# Kill the process
kill -9 $(lsof -ti:5000)
```

### Database Lock Error
```bash
# Close all database connections and restart
rm star_video_review.db
python app.py
```

## Next Steps (Phase 2+)

- [ ] Annotation CRUD endpoints
- [ ] AI analysis service integration
- [ ] Report generation
- [ ] Best practices reference endpoints
- [ ] Batch video processing
- [ ] Export functionality (PDF, CSV, JSON)
- [ ] LMS integration API

## Support

For issues or questions, contact the development team.

## License

Proprietary - STAR Program

