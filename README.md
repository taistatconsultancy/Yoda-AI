# 🚀 YodaAI - Conversational 4Ls Retrospective Assistant

## Vision

YodaAI is an AI-powered Conversational Retrospective Assistant that facilitates the 4Ls format (Liked, Learned, Lacked, Longed for) using structured prompts, intelligent follow-ups, and AI-driven summarization. Our goal is to make retrospectives easier, structured, and more actionable for Junior PMs and distributed agile teams.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│  Chat Interface │────│     FastAPI     │
└─────────────────┘    └─────────────────┘
                              │
                              ├─── Database (PostgreSQL)
                              │
                              └─── OpenAI GPT Model
                                      │
                                      └─── Vector DB
```

### Core Components

- **Chat Interface**: User-facing conversational interface
- **FastAPI Backend**: Python-based API server handling business logic
- **PostgreSQL Database**: Primary data storage for user data, conversations, and retrospective responses
- **OpenAI GPT Model**: AI engine for dynamic prompts, follow-ups, and summarization
- **Vector DB**: Embeddings storage for enhanced AI capabilities

## Development Phases

### Phase 1: Foundation Setup ✅
- [x] Project documentation and README
- [ ] Authentication system (Firebase/Auth0)
- [ ] Basic project dashboard UI
- [ ] PostgreSQL connection using Neon
- [ ] Sample sprint summary upload endpoint

### Phase 2: Conversational 4Ls MVP
- [ ] Chat UI using Google Design System
- [ ] Chat flow manager (frontend + backend socket)
- [ ] LangChain/OpenAI API integration for:
  - Dynamic 4L prompts
  - Follow-up question generation
  - Sentiment/context tagging
- [ ] Response storage with user attribution
- [ ] AI summary generation for each L

### Phase 3: Brainstorm & Voting
- [ ] Idea card generation API
- [ ] Voting interface (emoji, stars, upvote)
- [ ] AI clustering of top-voted themes
- [ ] Final discussion themes storage

### Future Phases
- More phases to be defined...

## Technology Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL (Neon)
- **AI/ML**: OpenAI GPT, LangChain, Vector Database
- **Authentication**: Firebase/Auth0
- **Frontend**: React/Next.js (to be implemented)
- **Design System**: Google Material Design

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL database (Neon)
- OpenAI API key
- Firebase/Auth0 account

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables
4. Run the application: `python main.py`

## Project Structure

```
yodaai/
├── backend/
│   ├── api/
│   ├── models/
│   ├── services/
│   └── utils/
├── frontend/
├── database/
├── docs/
└── tests/
```

## Contributing

This project follows agile development practices with clear phase-based milestones. Each phase builds upon the previous one to create a comprehensive retrospective assistant.

## License

[To be determined]

---

*"Do or do not, there is no try."* - YodaAI helps teams reflect, learn, and improve through structured retrospectives.
