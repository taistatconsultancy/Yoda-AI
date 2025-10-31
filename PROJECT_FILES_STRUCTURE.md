# YodaAI Project Files Structure

## 📁 Project Overview
AI-Powered Retrospective Assistant for Teams - Complete 6-phase retrospective workflow with workspace management, voting, discussions, and Disciplined Agile recommendations.

**✨ Status:** All legacy and deprecated files have been removed. Codebase is production-ready with only active files.

---

## 🔴 Critical Runtime Files (DO NOT DELETE)

### **Root Directory Files**

| File | Purpose | Required |
|------|---------|----------|
| `main.py` | FastAPI application entry point, router configuration, CORS setup | ✅ YES |
| `requirements.txt` | Python dependencies list | ✅ YES |
| `start_server.py` | Server startup script with health checks | ✅ YES |
| `alembic.ini` | Alembic database migration configuration | ✅ YES |
| `disciplined_agile_scrape.md` | Disciplined Agile knowledge base for AI recommendations | ✅ YES |

---

## 🗄️ Database Configuration

### **Database Core**
| File | Purpose |
|------|---------|
| `app/database/database.py` | SQLAlchemy engine, session factory, PostgreSQL/Neon & SQLite support |
| `app/database/__init__.py` | Package initialization |

### **Database Migrations (Alembic)**
| File | Purpose |
|------|---------|
| `alembic/env.py` | Alembic environment configuration |
| `alembic/script.py.mako` | Migration script template |
| `alembic/versions/0001_initial.py` | Initial database schema |
| `alembic/versions/0002_add_new_models.py` | Add chat sessions, messages, themes |
| `alembic/versions/0003_add_user_columns.py` | Add user authentication columns |
| `alembic/versions/0004_add_workspace_id_to_action_items.py` | Action items workspace reference |
| `alembic/versions/0004_create_workspace_invitations.py` | Workspace invitations table |
| `alembic/versions/2ca127ca9e75_add_chat_session_id_to_responses.py` | Link responses to chat sessions |
| `alembic/versions/372c7e4d8e04_add_workspace_id_to_retrospectives.py` | Retrospectives workspace migration |
| `alembic/versions/a03c5f94b7ba_fix_chat_sessions_schema.py` | Chat sessions schema fixes |
| `alembic/versions/b67abdb3b1a2_add_missing_chat_messages_columns.py` | Chat messages columns |
| `alembic/versions/bcb50145deeb_add_code_to_retrospectives.py` | Retrospective access codes |
| `alembic/versions/c6f0ca6ec5cb_make_action_items_retrospective_and_.py` | Action items updates |
| `alembic/versions/db0a6db0d497_merge_heads.py` | Migration merge |
| `alembic/versions/db62da066f3b_add_da_recommendations_table.py` | DA recommendations table |

---

## 🧩 Application Models

### **Core Models**
| File | Purpose | Key Tables |
|------|---------|-----------|
| `app/models/user.py` | User authentication & profile | `users` |
| `app/models/email_verification.py` | Email verification tokens | `email_verification_tokens` |
| `app/models/workspace.py` | Workspace & membership management | `workspaces`, `workspace_members`, `workspace_invitations` |
| `app/models/retrospective_new.py` | Complete retrospective workflow | `retrospectives`, `retrospective_participants`, `chat_sessions`, `chat_messages`, `retrospective_responses`, `theme_groups`, `voting_sessions`, `vote_allocations`, `discussion_topics`, `discussion_messages`, `da_recommendations` |
| `app/models/action_item.py` | Action item tracking | `action_items` |
| `app/models/onboarding.py` | User onboarding & scheduling | `user_onboarding`, `scheduled_retrospectives`, `team_preparations`, `automated_reminders` |
| `app/models/__init__.py` | Models package exports |

---

## 📋 Pydantic Schemas

| File | Purpose |
|------|---------|
| `app/schemas/auth.py` | Authentication request/response schemas |
| `app/schemas/ai_chat.py` | AI chat message schemas |
| `app/schemas/action_item.py` | Action item schemas |
| `app/schemas/__init__.py` | Schemas package exports |

---

## 🌐 API Routes

### **Authentication & Users**
| File | Purpose | Endpoints |
|------|---------|-----------|
| `app/api/routes/user_auth.py` | Email/password authentication | `/api/v1/user-auth/register`, `/login`, `/verify-email` |
| `app/api/routes/google_auth.py` | Google OAuth authentication | `/api/v1/user-auth/google` |
| `app/api/routes/users.py` | User profile management | `/api/v1/users/*` |

### **Workspace Management**
| File | Purpose | Endpoints |
|------|---------|-----------|
| `app/api/routes/workspaces.py` | Workspace CRUD, members, PDF upload | `/api/v1/workspaces/*` |
| `app/api/routes/workspace_invitations.py` | Invitations, validation, acceptance | `/api/v1/workspaces/{id}/invitations/*` |

### **Retrospective Workflow (Primary)**
| File | Purpose | Endpoints | Status |
|------|---------|-----------|--------|
| `app/api/routes/retrospectives_full.py` | **Complete 6-phase retrospective** | `/api/v1/retrospectives/*` | ✅ PRIMARY |
| `app/api/routes/fourls_chat.py` | 4Ls chat sessions & messages | `/api/v1/fourls-chat/*` | ✅ ACTIVE |
| `app/api/routes/grouping.py` | AI grouping, theme management | `/api/v1/grouping/{retro_id}/*` | ✅ ACTIVE |
| `app/api/routes/voting.py` | Voting sessions, submissions | `/api/v1/voting/{retro_id}/*` | ✅ ACTIVE |
| `app/api/routes/discussion_summary.py` | Discussion topics, DA recommendations, PDF | `/api/v1/discussion/{retro_id}/*` | ✅ ACTIVE |
| `app/api/routes/action_items.py` | Action item management | `/api/v1/action-items/*` | ✅ ACTIVE |
| `app/api/routes/scheduling.py` | Retrospective scheduling | `/api/v1/scheduling/*` | ✅ ACTIVE |

### **Route Dependencies**
| File | Purpose |
|------|---------|
| `app/api/dependencies/auth.py` | JWT authentication, `get_current_user()` |
| `app/api/dependencies/permissions.py` | Permission checking |
| `app/api/__init__.py` | Routes package exports |
| `app/api/routes/__init__.py` | Routes exports |

---

## ⚙️ Services Layer

| File | Purpose |
|------|---------|
| `app/services/email_service.py` | SMTP email notifications |
| `app/services/firebase_auth.py` | Firebase Admin SDK integration |
| `app/services/firebase_service.py` | Firebase service helpers |
| `app/services/automation_service.py` | Retrospective automation (schedule, reminders, reports) |
| `app/services/calendar_service.py` | iCal generation for calendar events |
| `app/services/ai_service.py` | General AI service |
| `app/services/enhanced_ai_service.py` | Enhanced AI with Gemini |
| `app/services/action_item_service.py` | Action item business logic |
| `app/services/upload_service.py` | File upload handling |
| `app/services/timezone_utils.py` | Timezone utilities |
| `app/services/__init__.py` | Services package exports |

---

## ⚙️ Configuration

| File | Purpose |
|------|---------|
| `app/core/config.py` | Application settings, environment variables |
| `app/core/__init__.py` | Core package initialization |

---

## 🎨 Frontend UI

| File | Purpose | Route |
|------|---------|-------|
| `app/ui/yodaai-app.html` | Main dashboard & workspace management | `/ui/yodaai-app.html` |
| `app/ui/retrospective.html` | 6-phase retrospective session UI | `/ui/retrospective.html/{code}` |

---

## 📦 Package Files

| File | Purpose |
|------|---------|
| `app/__init__.py` | App package initialization |
| `app/api/__init__.py` | API package initialization |
| `app/models/__init__.py` | Models package initialization |
| `app/schemas/__init__.py` | Schemas package initialization |
| `app/services/__init__.py` | Services package initialization |
| `app/database/__init__.py` | Database package initialization |
| `app/core/__init__.py` | Core package initialization |
| `app/api/dependencies/__init__.py` | Dependencies package initialization |

---

## 🔧 Utility Scripts (Optional but Useful)

| File | Purpose |
|------|---------|
| `start_server.py` | Enhanced server startup with checks |
| `check_db_schema.py` | Database schema validation |
| `test_firebase_connection.py` | Firebase connection testing |
| `quick_clear_db.py` | Database cleanup utility |
| `sync_users_to_firebase.py` | User synchronization |
| `get_verification_link.py` | Email verification helper |
| `fix_action_items_schema.py` | Schema fixes |
| `check_null_bytes.py` | Database validation |

---

## 🗂️ Directory Structure

```
V3_Assistant/
├── main.py                          # ✅ FastAPI app entry
├── requirements.txt                 # ✅ Dependencies
├── start_server.py                  # ✅ Startup script
├── alembic.ini                      # ✅ Migration config
├── disciplined_agile_scrape.md      # ✅ DA knowledge base
├── alembic/                         # ✅ Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_initial.py
│       ├── 0002_add_new_models.py
│       └── ... (11 more migrations)
└── app/
    ├── __init__.py                  # ✅
    ├── core/
    │   ├── __init__.py              # ✅
    │   └── config.py                # ✅ Configuration
    ├── database/
    │   ├── __init__.py              # ✅
    │   └── database.py              # ✅ Database setup
    ├── models/
    │   ├── __init__.py              # ✅
    │   ├── user.py                  # ✅ User model
    │   ├── email_verification.py    # ✅ Email tokens
    │   ├── workspace.py             # ✅ Workspaces
    │   ├── retrospective_new.py     # ✅ Retrospective models
    │   ├── action_item.py           # ✅ Action items
    │   └── onboarding.py            # ✅ Onboarding models
    ├── schemas/
    │   ├── __init__.py              # ✅
    │   ├── auth.py                  # ✅
    │   ├── ai_chat.py               # ✅
    │   └── action_item.py           # ✅
    ├── api/
    │   ├── __init__.py              # ✅
    │   ├── dependencies/
    │   │   ├── __init__.py          # ✅
    │   │   ├── auth.py              # ✅ JWT auth
    │   │   └── permissions.py       # ✅
    │   └── routes/
    │       ├── __init__.py              # ✅
    │       ├── user_auth.py             # ✅ Email/password auth
    │       ├── google_auth.py           # ✅ Google OAuth
    │       ├── users.py                 # ✅ User management
    │       ├── workspaces.py            # ✅ Workspace CRUD
    │       ├── workspace_invitations.py # ✅ Invitations
    │       ├── retrospectives_full.py   # ✅ PRIMARY retrospective workflow
    │       ├── fourls_chat.py           # ✅ Chat sessions
    │       ├── grouping.py              # ✅ AI grouping
    │       ├── voting.py                # ✅ Voting
    │       ├── discussion_summary.py    # ✅ Discussion & PDF
    │       ├── action_items.py          # ✅ Action items
    │       └── scheduling.py            # ✅ Scheduling
    ├── services/
    │   ├── __init__.py              # ✅
    │   ├── email_service.py         # ✅ SMTP
    │   ├── firebase_auth.py         # ✅ Firebase
    │   ├── firebase_service.py      # ✅
    │   ├── automation_service.py    # ✅ Automation
    │   ├── calendar_service.py      # ✅ iCal
    │   ├── ai_service.py            # ✅ AI
    │   ├── enhanced_ai_service.py   # ✅ Enhanced AI
    │   ├── action_item_service.py   # ✅
    │   ├── upload_service.py        # ✅
    │   └── timezone_utils.py        # ✅
    └── ui/
        ├── yodaai-app.html          # ✅ Main dashboard
        └── retrospective.html       # ✅ Retro session

Legend:
✅ = ACTIVE - Required for production
```

---

## 🔑 Environment Variables Required

Create a `.env` file in the root directory with these variables:

```bash
# Database
DATABASE_URL=sqlite:///./yodaai.db
NEON_DATABASE_URL=postgresql://...  # Optional: for PostgreSQL/Neon
USE_LOCAL_DB=False

# OpenAI
OPENAI_API_KEY=sk-...

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yodaai.com

# Firebase (Optional)
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-...@your-project.iam.gserviceaccount.com

# App
DEBUG=True
ENVIRONMENT=development
APP_URL=http://localhost:8000
```

---

## 📝 Installation Steps

1. **Install Python 3.9+**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file**
   - Copy settings from `app/core/config.py`
   - Add your API keys

4. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start server**
   ```bash
   python start_server.py
   # OR
   python main.py
   ```

6. **Access application**
   - Main App: http://localhost:8000/ui/yodaai-app.html
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

---

## 🎯 Key Features

### **6-Phase Retrospective Workflow**
1. **Input Phase** - 4Ls chat with AI
2. **Grouping Phase** - AI-powered theme grouping
3. **Voting Phase** - Allocate 10 votes to themes
4. **Discussion Phase** - Top themes + DA recommendations + AI chat
5. **Summary Phase** - Downloadable PDF
6. **Completed Phase** - Redirect to dashboard

### **Workspace Management**
- Create/manage workspaces
- Invite members with email validation
- Role-based permissions (Scrum Master, Project Manager, Developer)
- PDF reference document upload

### **Automation**
- Scheduled retrospectives
- Automated email reminders
- Calendar event generation (iCal)
- Action item tracking

### **AI Features**
- GPT-4 powered 4Ls facilitation
- AI theme grouping
- Disciplined Agile recommendations
- PDF summary generation
- Discussion support

---

## ⚠️ Important Notes

1. **Primary Routes**: Use `retrospectives_full.py` for all retrospective operations
2. **Database**: Supports both SQLite (local) and PostgreSQL/Neon Cloud
3. **Authentication**: JWT-based with optional Firebase OAuth
4. **PDF Generation**: Requires `reportlab==4.0.9`
5. **AI Models**: GPT-4 for chat, grouping, and recommendations

---

## ✅ Cleanup Status

**All deprecated legacy files have been successfully removed from the codebase!**

The following files were deleted:
- ✅ All `.bak` backup files from `app/models/`
- ✅ All legacy route files (`retrospectives.py`, `teams.py`, `ai_chat.py`, `ai_chat_openai.py`)
- ✅ All deprecated service files
- ✅ All unused onboarding and reminder files
- ✅ All legacy schema files

The codebase is now clean and only contains active, production-ready files.

---

## 📊 Database Tables Overview

| Table | Purpose |
|-------|---------|
| `users` | User accounts & profiles |
| `email_verification_tokens` | Email verification |
| `workspaces` | Team workspaces |
| `workspace_members` | Workspace membership |
| `workspace_invitations` | Invitation tracking |
| `retrospectives` | Retrospective sessions |
| `retrospective_participants` | Participation tracking |
| `chat_sessions` | 4Ls chat sessions |
| `chat_messages` | Chat conversation history |
| `retrospective_responses` | Extracted 4Ls responses |
| `theme_groups` | Grouped themes |
| `voting_sessions` | Voting session tracking |
| `vote_allocations` | Individual votes |
| `discussion_topics` | Top themes for discussion |
| `discussion_messages` | Discussion conversation |
| `da_recommendations` | Disciplined Agile suggestions |
| `action_items` | Action item tracking |
| `scheduled_retrospectives` | Scheduled retrospectives |
| `user_onboarding` | Onboarding progress |
| `team_preparations` | Pre-retro prep responses |
| `automated_reminders` | Automated reminders |

---

