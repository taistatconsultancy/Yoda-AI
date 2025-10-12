# 🤖 YodaAI - Conversational 4Ls Retrospective Assistant

> *"Do or do not, there is no try... but with retrospectives, we always try to improve!"*

YodaAI is an intelligent retrospective assistant that guides agile teams through structured 4Ls retrospectives using AI-powered conversation. Built with FastAPI and modern web technologies, it provides a seamless experience for conducting meaningful team retrospectives.

## ✨ Features

### 🎯 Core Capabilities
- **4Ls Framework**: Structured retrospectives (Liked, Learned, Lacked, Longed For)
- **AI Chat Assistant**: Intelligent guidance during retrospective sessions
- **Team Management**: Multi-team support with role-based permissions
- **Action Items**: Track and manage improvement actions
- **Real-time Analytics**: Insights and patterns from retrospective data

### 🤖 AI-Powered Features
- **Conversational Guidance**: Natural language assistance during retrospectives
- **Pattern Recognition**: Identify trends and themes across sessions
- **Action Item Generation**: AI-suggested improvements based on feedback
- **Sentiment Analysis**: Understand team mood and engagement
- **Follow-up Questions**: Intelligent prompts to deepen insights

### 👥 Team Collaboration
- **Role-based Access**: Scrum Master, Product Owner, Developer, QA, Designer, DevOps
- **Multi-team Support**: Manage multiple teams and concurrent projects
- **Calendar Integration**: Schedule retrospectives and automated reminders
- **Collaborative Sessions**: Real-time team retrospectives with AI facilitation

### 📊 Analytics & Insights
- **Retrospective Trends**: Track patterns and improvements over time
- **Action Item Completion**: Monitor progress on team improvements
- **Team Engagement**: Analyze participation rates and feedback quality
- **AI Recommendations**: Data-driven suggestions for process improvement

## 🚀 Quick Start

### Option 1: Simple Start (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd YodaAI

# Run the startup script
python start.py
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env file (see SETUP.md for details)
cp env.example .env
# Edit .env with your configuration

# 3. Run database migrations
alembic upgrade head

# 4. Start the application
python main.py
```

### 5. Access the Application
- **User Interface**: http://localhost:8000/ui
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎮 Demo Mode

The application includes a demo mode that allows you to explore all features without setting up authentication:

1. Start the application
2. Click "Try Demo Mode" on the login screen
3. Explore the full interface with sample data

## 🏗️ Architecture

### Backend (FastAPI)
- **API Layer**: RESTful endpoints with automatic documentation
- **Service Layer**: Business logic and AI integration
- **Data Layer**: SQLAlchemy ORM with PostgreSQL/SQLite support
- **Authentication**: Firebase Auth integration with JWT tokens

### Frontend (Modern Web UI)
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Chat**: Interactive AI conversation interface
- **Dashboard**: Comprehensive project and team management
- **Analytics**: Visual insights and trend analysis

### AI Integration
- **OpenAI GPT-4**: Advanced conversational AI for retrospective guidance
- **Context Awareness**: Maintains conversation context across sessions
- **Pattern Analysis**: Identifies trends and suggests improvements
- **Action Generation**: Creates actionable items from retrospective insights

## 📋 API Endpoints

### Authentication
- `GET /api/v1/auth/me` - Get current user information

### Retrospectives
- `POST /api/v1/retrospectives/` - Create new retrospective
- `GET /api/v1/retrospectives/` - List user's retrospectives
- `GET /api/v1/retrospectives/{id}` - Get specific retrospective
- `POST /api/v1/retrospectives/{id}/responses` - Submit 4Ls response

### Teams
- `POST /api/v1/teams/` - Create new team
- `GET /api/v1/teams/` - List user's teams
- `POST /api/v1/teams/{id}/members` - Add team member
- `DELETE /api/v1/teams/{id}/members/{member_id}` - Remove team member

### Action Items
- `POST /api/v1/action-items/` - Create action item
- `GET /api/v1/action-items/` - List action items with filters
- `PUT /api/v1/action-items/{id}` - Update action item
- `POST /api/v1/action-items/{id}/complete` - Mark as completed

### AI Chat
- `POST /api/v1/ai-chat/sessions` - Create chat session
- `POST /api/v1/ai-chat/sessions/{id}/messages` - Send message
- `GET /api/v1/ai-chat/sessions/{id}/messages` - Get chat history
- `POST /api/v1/ai-chat/retrospective/{id}/analyze` - Analyze retrospective

## 🔧 Configuration

### Environment Variables
```env
# Database
DATABASE_URL=sqlite:///./yodaai.db

# OpenAI (Required for AI features)
OPENAI_API_KEY=your_openai_api_key

# Authentication
SECRET_KEY=your_secret_key

# Firebase (Optional)
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email
```

See `SETUP.md` for detailed configuration instructions.

## 🎯 Use Cases

### For Scrum Masters
- **Facilitate Retrospectives**: AI assistance for new or experienced facilitators
- **Track Team Health**: Monitor patterns and team engagement over time
- **Action Item Management**: Ensure follow-through on improvement commitments

### For Product Owners
- **Process Improvement**: Identify bottlenecks and improvement opportunities
- **Team Collaboration**: Understand team dynamics and communication patterns
- **Sprint Planning**: Use retrospective insights to improve future sprints

### For Development Teams
- **Structured Reflection**: Guided 4Ls framework for consistent retrospectives
- **Voice Concerns**: Safe space to discuss challenges and improvements
- **Celebrate Successes**: Recognize and reinforce positive practices

### For Organizations
- **Scale Retrospectives**: Manage retrospectives across multiple teams
- **Data-Driven Insights**: Analytics on team performance and improvement trends
- **Knowledge Sharing**: Capture and share lessons learned across teams

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production with Docker
```bash
docker build -t yodaai .
docker run -p 8000:8000 yodaai
```

### Cloud Deployment
- **Vercel**: Deploy with `vercel --prod`
- **Railway**: Connect GitHub repository
- **Heroku**: Use included Procfile
- **AWS/GCP**: Use container deployment

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing the GPT-4 API
- **FastAPI** for the excellent web framework
- **SQLAlchemy** for robust database ORM
- **Firebase** for authentication services
- **The Agile Community** for the 4Ls retrospective framework

## 📞 Support

- **Documentation**: See `SETUP.md` for detailed setup instructions
- **Issues**: Report bugs and request features on GitHub Issues
- **Discussions**: Join community discussions on GitHub Discussions

---

*"The best teacher, failure is. But with retrospectives, we learn from it and grow stronger, we do."* - YodaAI 🤖