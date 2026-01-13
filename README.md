# 🎯 YodaAI - Conversational 4Ls Retrospective Assistant

**AI-Powered Sprint Retrospective Tool for Agile Teams**

YodaAI is an intelligent retrospective assistant that helps agile teams conduct effective 4Ls (Liked, Learned, Lacked, Longed For) retrospectives using conversational AI. All data is securely stored in **Neon Cloud PostgreSQL**.

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Database Setup](#-database-setup)
- [Running the Application](#-running-the-application)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Endpoints](#-api-endpoints)
- [Environment Variables](#-environment-variables)
- [Contributing](#-contributing)

---

## ✨ Features

### Core Features
- **🤖 AI-Powered Conversations** - Interactive retrospective sessions using OpenAI GPT
- **📊 4Ls Framework** - Structured retrospectives (Liked, Learned, Lacked, Longed For)
- **🎨 Thematic Analysis** - AI-driven pattern detection and insights
- **✅ Action Item Generation** - Automatic extraction of actionable items
- **👥 Team Management** - Multi-team support with role-based access
- **📅 Scheduling** - Automated retrospective scheduling
- **💾 Cloud Storage** - Secure data storage in Neon PostgreSQL
- **🔐 Authentication** - Email/password authentication with JWT tokens

### User Experience
- **Single-Page Application** - Modern, responsive UI
- **Real-time AI Responses** - Streaming AI chat interface
- **Onboarding Flow** - Guided setup for new users
- **Dashboard** - Overview of retrospectives and action items
- **Mobile-Friendly** - Responsive design for all devices

---

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **Alembic** - Database migrations
- **Neon PostgreSQL** - Cloud-hosted database
- **OpenAI API** - AI-powered chat and analysis
- **Pydantic** - Data validation
- **JWT** - Secure authentication

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **HTML5/CSS3** - Modern web standards
- **Fetch API** - RESTful API communication

### AI & NLP
- **OpenAI GPT-4** - Conversational AI
- **LangChain** - AI orchestration
- **ChromaDB** - Vector database for embeddings
- **Thematic Analysis** - Pattern detection in retrospectives

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **pip** - Python package installer
- **Git** - Version control
- **Neon Account** - [Sign up](https://neon.tech/) for free cloud PostgreSQL

### API Keys Required
- **OpenAI API Key** - [Get one here](https://platform.openai.com/api-keys)
- **Neon Database URL** - From your Neon project dashboard

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/yoda-ai.git
cd yoda-ai
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv ai
ai\Scripts\activate

# macOS/Linux
python3 -m venv ai
source ai/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the example environment file and fill in your credentials:

```bash
cp env.example .env
```

Edit `.env` with your actual values:

```env
# Database Configuration
NEON_DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Authentication
SECRET_KEY=your-super-secret-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
DEBUG=True
ENVIRONMENT=development
APP_URL=http://localhost:8000
```

---

## 💾 Database Setup

### Option 1: Automated Setup (Recommended)

1. **Access Neon Console**
   - Go to [https://console.neon.tech/](https://console.neon.tech/)
   - Select your project

2. **Run Database Migrations**
```bash
   # Activate virtual environment first
   ai\Scripts\activate  # Windows
   # source ai/bin/activate  # macOS/Linux

   # Run migrations
   alembic upgrade head
```

### Option 2: Manual Setup

If automated migrations fail due to permissions:

1. Open [Neon SQL Editor](https://console.neon.tech/)
2. Run the following SQL commands:

```sql
-- Grant permissions
GRANT CREATE ON SCHEMA public TO neondb_owner;
GRANT ALL ON SCHEMA public TO neondb_owner;

-- Tables will be created automatically on first run
```

### Verify Database Setup

The application will create these tables:
- `users` - User accounts and authentication
- `teams` - Team management
- `retrospectives` - Retrospective sessions
- `retrospective_responses` - User responses (4Ls)
- `action_items` - Generated action items
- `chat_sessions` - AI chat history
- `chat_messages` - Individual chat messages
- `sprint_summaries` - Sprint analysis data
- Additional supporting tables

---

## ▶️ Running the Application

### Start the Server

```bash
# Activate virtual environment
ai\Scripts\activate  # Windows
# source ai/bin/activate  # macOS/Linux

# Run the application
python start_server.py
```

Or use uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access the Application

- **Main Application**: http://localhost:8000/

- **Direct App Access**: http://localhost:8000/ui/yodaai-app.html
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health


---

## 📖 Usage

### First-Time Setup

1. **Navigate to the App**
   - Open http://localhost:8000/ in your browser

2. **Create an Account**
   - Click "Sign Up"
   - Enter email, password, and full name
   - Or use "Demo Login" for quick testing

3. **Complete Onboarding**
   - Set up your team
   - Configure preferences
   - Schedule retrospectives (optional)

### Conducting a Retrospective

1. **Start New Retrospective**
   - Click "New Retrospective" from dashboard
   - Enter sprint details

2. **AI-Guided Session**
   - Answer the AI's questions about:
     - **Liked** - What went well?
     - **Learned** - What did you learn?
     - **Lacked** - What was missing?
     - **Longed For** - What do you wish you had?

3. **Review Insights**
   - AI analyzes responses for patterns
   - Generates thematic insights
   - Creates action items automatically

4. **Export & Share**
   - Download retrospective summary
   - Share with team members
   - Track action items

### Managing Teams

1. **Create a Team**
   - Go to Team Settings
   - Invite members via email
   - Assign roles (Admin, Member, Viewer)

2. **Schedule Retrospectives**
   - Set up recurring meetings
   - Configure reminders
   - Automate notifications

---

## 📁 Project Structure

```
Yoda-AI/
├── ai/                          # Python virtual environment
├── alembic/                     # Database migrations
│   ├── versions/               # Migration scripts
│   │   ├── 0001_initial.py
│   │   └── 0002_add_new_models.py
│   └── env.py                  # Alembic configuration
├── app/                        # Main application code
│   ├── api/                    # API layer
│   │   ├── dependencies/       # Shared dependencies
│   │   │   └── auth.py        # Authentication middleware
│   │   └── routes/            # API endpoints
│   │       ├── user_auth.py   # User authentication
│   │       ├── retrospectives.py
│   │       ├── action_items.py
│   │       ├── teams.py
│   │       ├── ai_chat.py     # AI chat endpoints
│   │       ├── ai_chat_openai.py # OpenAI integration
│   │       ├── onboarding.py  # User onboarding
│   │       └── scheduling.py  # Meeting scheduling
│   ├── core/                  # Core configuration
│   │   └── config.py         # App settings
│   ├── database/             # Database layer
│   │   └── database.py      # SQLAlchemy setup
│   ├── models/              # Database models
│   │   ├── user.py
│   │   ├── team.py
│   │   ├── retrospective.py
│   │   ├── action_item.py
│   │   ├── ai_chat.py
│   │   ├── onboarding.py
│   │   └── sprint_summary.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py
│   │   ├── retrospective.py
│   │   ├── action_item.py
│   │   ├── team.py
│   │   └── ai_chat.py
│   ├── services/            # Business logic
│   │   ├── ai_service.py           # AI orchestration
│   │   ├── enhanced_ai_service.py  # Advanced AI features
│   │   ├── firebase_service.py     # Optional Firebase
│   │   ├── retrospective_service.py
│   │   ├── action_item_service.py
│   │   ├── team_service.py
│   │   ├── email_service.py
│   │   ├── automation_service.py
│   │   └── onboarding_service.py
│   └── ui/                  # Frontend application
│       └── yodaai-app.html # Single-page application
├── disciplined_agile_scrape.md  # Agile methodology reference
├── env.example              # Environment template
├── requirements.txt         # Python dependencies
├── main.py                 # FastAPI application entry
├── start_server.py         # Server startup script
└── README.md              # This file
```

---

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/user-auth/register` - Create new account
- `POST /api/v1/user-auth/login` - User login
- `POST /api/v1/user-auth/demo-login` - Demo account
- `GET /api/v1/user-auth/verify-token` - Verify JWT token

### Retrospectives
- `GET /api/v1/retrospectives/` - List retrospectives
- `POST /api/v1/retrospectives/` - Create retrospective
- `GET /api/v1/retrospectives/{id}` - Get retrospective details
- `PUT /api/v1/retrospectives/{id}` - Update retrospective
- `DELETE /api/v1/retrospectives/{id}` - Delete retrospective

### Action Items
- `GET /api/v1/action-items/` - List action items
- `POST /api/v1/action-items/` - Create action item
- `PUT /api/v1/action-items/{id}` - Update action item
- `DELETE /api/v1/action-items/{id}` - Delete action item

### AI Chat
- `POST /api/v1/ai-chat/proxy/stream` - Stream AI responses
- `POST /api/v1/ai-chat/thematic-analysis` - Analyze retrospective themes

### Teams
- `GET /api/v1/teams/` - List teams
- `POST /api/v1/teams/` - Create team
- `POST /api/v1/teams/members` - Add team member

### Onboarding
- `POST /api/v1/onboarding/complete-step` - Complete onboarding step
- `GET /api/v1/onboarding/status` - Get onboarding status

### Scheduling
- `POST /api/v1/scheduling/schedule` - Schedule retrospective
- `GET /api/v1/scheduling/upcoming` - Get upcoming meetings

Full API documentation available at: http://localhost:8000/docs

---

## 🔐 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEON_DATABASE_URL` | Neon PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `OPENAI_API_KEY` | OpenAI API key for AI features | `sk-...` |
| `SECRET_KEY` | JWT secret key (min 32 chars) | `your-secret-key` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Fallback database URL | `sqlite:///./yodaai.db` |
| `GEMINI_API_KEY` | Google Gemini API (alternative AI) | None |
| `DEBUG` | Enable debug mode | `True` |
| `ENVIRONMENT` | Environment name | `development` |
| `APP_URL` | Application base URL | `http://localhost:8000` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiration time | `30` |

---

## 🔒 Security Features

- **Password Hashing** - Bcrypt encryption for all passwords
- **JWT Tokens** - Secure session management
- **SSL/TLS** - Encrypted database connections
- **CORS Protection** - Configurable origin restrictions
- **SQL Injection Prevention** - SQLAlchemy ORM protection
- **XSS Protection** - Input validation and sanitization

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Test database connection
python -c "from app.database.database import test_connection; test_connection()"
```

### Permission Errors
- Ensure `NEON_DATABASE_URL` is correct
- Check database user has CREATE privileges
- Verify SSL mode is set to `require`

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is valid
- Check API quota/billing
- Review rate limits

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

## 📊 Data Storage

All application data is stored in **Neon Cloud PostgreSQL**:

- ✅ User accounts and authentication
- ✅ Team and member data
- ✅ Retrospective sessions and responses
- ✅ AI chat conversations
- ✅ Action items and sprint summaries
- ✅ All metadata and relationships

**No local database is used** - everything is cloud-based for reliability and scalability.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Disciplined Agile** - Agile methodology framework
- **OpenAI** - GPT-4 API for conversational AI
- **Neon** - Cloud PostgreSQL database
- **FastAPI** - Modern Python web framework

---

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: mulingwastephen200@gmail.com

---

## 🎓 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Neon Documentation](https://neon.tech/docs)
- [Disciplined Agile](https://www.pmi.org/disciplined-agile) - See `disciplined_agile_scrape.md`

---

**Built with ❤️ by the YodaAI Team**

*Making sprint retrospectives smarter, one conversation at a time.*

