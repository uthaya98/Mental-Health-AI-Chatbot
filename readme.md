# 🧠 Mental Health AI Chatbot – Conversational Analytics & Emotional Tracking Platform

<div align="center">

**A full-stack AI-powered mental health companion designed to help users reflect on their emotional well-being through conversations, visual analytics, and time-based emotional tracking.**

[Features](#-core-features) • [Architecture](#-system-architecture) • [Setup](#-getting-started) • [API](#-api-reference) • [Demo](#-screenshots)

</div>

---

## 📋 Table of Contents

- [Project Vision](#-project-vision)
- [Core Features](#-core-features)
- [System Architecture](#-system-architecture-overview)
- [RAG Implementation](#-rag-retrieval-augmented-generation-flow)
- [ETL & Data Pipeline](#-calendar--etl-data-flow)
- [Project Structure](#-project-structure)
- [Authentication](#-authentication--middleware-design)
- [Screenshots](#-screenshots)
- [Getting Started](#-getting-started)
- [API Reference](#-api-reference)
- [Data Models](#-data-models)
- [Why Enterprise-Ready](#-why-this-project-is-enterprise-ready)
- [Future Enhancements](#-future-enhancements)
- [Author](#-author)

---

## 🌟 Project Vision

Mental health is deeply contextual and time-dependent. Traditional mental health applications often lack the sophisticated AI capabilities and temporal analysis needed to provide meaningful insights. This project aims to bridge that gap by:

- **Enabling safe, structured AI conversations** that adapt to user emotional states
- **Capturing emotional signals over time** to identify patterns and trends
- **Visualizing behavioral and emotional patterns** through interactive dashboards
- **Providing actionable daily and weekly insights** based on aggregated data
- **Demonstrating enterprise-grade middleware and AI architecture** suitable for production environments

This system is built with **production-level patterns**, incorporating best practices from FastAPI, React, and modern data engineering. It's designed for real-world deployment, technical presentations, and as a reference implementation for AI-driven health applications.

---

## ✨ Core Features

### 💬 Conversational AI Chat

A sophisticated chat system that goes beyond simple question-and-answer:

- **🔐 Secure JWT-authenticated chat sessions** - Every conversation is protected and user-specific
- **😊 Emotion detection per message** - Real-time analysis of emotional content using NLP
- **📊 Loneliness score computation** - Quantitative measurement of social isolation indicators
- **🚨 Crisis detection with safe fallback messaging** - Automatic identification of concerning content with appropriate resources
- **✏️ ChatGPT-style edit & regenerate** - Edit your last message and get a new AI response
- **🗑️ Soft-delete & regeneration-safe message handling** - Maintains conversation integrity while allowing edits

**Technical Highlights:**
- Streaming responses for real-time interaction
- Context-aware replies using RAG (Retrieval-Augmented Generation)
- Emotion classification using transformer-based models
- Safety filters to prevent harmful content

---

### 📅 Emotional Calendar (Dynamic)

A unique feature that transforms abstract emotional data into visual, actionable insights:

- **📆 Non-static calendar populated from backend data** - Real data, not placeholder UI
- **Each day displays:**
  - 🎭 **Dominant emotion** - The most frequent emotional state
  - 💬 **Message count** - Activity level tracking
  - 📈 **Average loneliness score** - Daily emotional wellness indicator
- **🔍 Click on a day** → View complete chat history for that date
- **🤖 AI-generated daily emotional reflection** - Automated summaries powered by LLMs

**Why This Matters:**
Traditional mood trackers require manual input. This calendar automatically aggregates emotional data from natural conversations, providing a retrospective view without user friction.

---

### 📊 Analytics Dashboard

Enterprise-grade visualizations for longitudinal emotional tracking:

- **📈 Weekly emotion & loneliness trends** - Line charts showing emotional trajectories
- **📊 Message frequency visualization** - Bar charts indicating engagement patterns
- **🎨 Built using Recharts** - Production-ready charting library
- **⚡ Backed by aggregated daily summaries** - ETL-driven data pipeline for performance

**Insights Provided:**
- Are loneliness scores improving over time?
- Which days see the most/least engagement?
- Correlation between message frequency and emotional states
- Weekly emotional patterns and trends

---

### 🧠 AI Intelligence Layer

The core intelligence system powering all features:

| Component | Description | Technology |
|-----------|-------------|------------|
| **Emotion Classification** | Detects joy, sadness, anger, fear, surprise, neutral | DistilBERT / GPT-based |
| **Loneliness Scoring** | 1-10 scale based on social isolation indicators | Custom NLP model |
| **Crisis Detection** | Identifies self-harm, suicidal ideation | Safety classifiers |
| **Context-Aware Replies** | RAG-based responses with relevant context | Vector embeddings + LLM |
| **Daily Summarization** | ETL job generates emotional insights | GPT-4 / Claude |

![Backend Services Architecture](screenshots/backend-services.png)

---

## 🏗️ System Architecture Overview

### General Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐    │
│  │  Chat   │  │ Calendar │  │Analytics │  │  Auth   │    │
│  │  UI     │  │   View   │  │Dashboard │  │  Flow   │    │
│  └─────────┘  └──────────┘  └──────────┘  └─────────┘    │
└────────────┬────────────────────────────────────────────────┘
             │ Axios (JWT Interceptor)
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                          │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Middleware Layer                         │  │
│  │  • JWT Validation  • CORS  • Rate Limiting            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  API Routes                           │  │
│  │  /chat  /calendar  /sessions  /users  /health        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               Service Layer                           │  │
│  │  • LLM Service      • RAG Service                     │  │
│  │  • Emotion Service  • Safety Check                    │  │
│  │  • Loneliness Calc  • Drift Detection                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                 CRUD Layer                            │  │
│  │  Database operations, query optimization              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬────────────────────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                      │
│  • Users  • Sessions  • Messages                            │
│  • DailyEmotionSummaries  • RAG Knowledge Store             │
└────────────┬────────────────────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dagster ETL Pipeline                      │
│  • Daily aggregation  • Weekly summaries                    │
│  • Emotion analytics  • Data quality checks                 │
└─────────────────────────────────────────────────────────────┘
```

![General System Flow](screenshots/general-flow.png)

### Backend Services Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Chat Service │ │Calendar Svc  │ │ User Service │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ├────────────────┼────────────────┤
       │                │                │
       ▼                ▼                ▼
┌─────────────────────────────────────────────┐
│            Core AI Services                 │
│  ┌──────────────────────────────────────┐  │
│  │  LLM Service                          │  │
│  │  • OpenAI/Anthropic Integration       │  │
│  │  • Prompt Engineering                 │  │
│  │  • Response Streaming                 │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │  RAG Service                          │  │
│  │  • Vector Embedding                   │  │
│  │  • Similarity Search                  │  │
│  │  • Context Retrieval                  │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │  Emotion Analysis Service             │  │
│  │  • Emotion Classification             │  │
│  │  • Loneliness Scoring                 │  │
│  │  • Sentiment Analysis                 │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │  Safety Check Service                 │  │
│  │  • Crisis Detection                   │  │
│  │  • Self-harm Identification           │  │
│  │  • Resource Recommendation            │  │
│  └──────────────────────────────────────┘  │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│          Database Access Layer              │
│  • SQLAlchemy ORM                           │
│  • Connection Pooling                       │
│  • Query Optimization                       │
└─────────────────────────────────────────────┘
```

![Backend Services Architecture](screenshots/backend-services.png)

**Architecture Principles:**
- **Separation of Concerns** - Clear boundaries between layers
- **Dependency Injection** - Services injected into routes
- **Stateless Authentication** - JWT tokens, no server-side sessions
- **ETL-Driven Analytics** - Pre-aggregated data for performance
- **RAG for Context** - Relevant information retrieval before LLM generation

---

## 🧠 RAG (Retrieval-Augmented Generation) Flow

RAG prevents hallucination and improves response quality by grounding the AI in relevant context:

```
┌─────────────────────────────────────────────────────────────┐
│                     User Message Received                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Emotion & Safety Analysis (Parallel)           │
│                                                               │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │ Emotion Detection│          │  Crisis Check     │        │
│  │ • Joy/Sad/Angry  │          │  • Self-harm      │        │
│  │ • Fear/Surprise  │          │  • Suicidal       │        │
│  └──────────────────┘          └──────────────────┘        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Retrieve Relevant Context                  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Vector Similarity Search                             │  │
│  │  • Query embedding                                    │  │
│  │  • FAISS index lookup                                 │  │
│  │  • Top-K similar documents                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Previous Conversation Context                        │  │
│  │  • Last N messages from session                       │  │
│  │  • User emotional history                             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  User Historical Patterns                             │  │
│  │  • Recurring themes                                   │  │
│  │  • Emotional triggers                                 │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Domain Knowledge Base                                │  │
│  │  • Mental health resources                            │  │
│  │  • Coping strategies                                  │  │
│  │  • Professional guidance                              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Build Enriched Prompt                      │
│                                                               │
│  [Retrieved Context] +                                       │
│  [User Message] +                                            │
│  [System Instructions] +                                     │
│  [Emotional State] +                                         │
│  [Safety Constraints]                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  LLM Generates Response                     │
│                                                               │
│  • GPT-4 / Claude / Llama                                   │
│  • Temperature: 0.7                                          │
│  • Max tokens: 500                                           │
│  • Stream: true                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Persist Message + Metadata                     │
│                                                               │
│  • Message content                                           │
│  • Emotion label (joy/sad/angry/etc)                        │
│  • Loneliness score (1-10)                                   │
│  • Timestamp                                                 │
│  • Session ID                                                │
│  • User ID                                                   │
│  • Crisis flag (if applicable)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Return to User                           │
│  • Streamed response                                         │
│  • Emotion indicator                                         │
│  • Safety resources (if needed)                              │
└─────────────────────────────────────────────────────────────┘
```

![RAG Flow Diagram](screenshots/rag-flowchart.png)

### Why RAG?

| Challenge | How RAG Solves It |
|-----------|-------------------|
| **Hallucination** | Grounds responses in retrieved facts |
| **Context Loss** | Maintains conversation history |
| **Domain Knowledge** | Injects mental health expertise |
| **Personalization** | Retrieves user-specific patterns |
| **Scalability** | Knowledge base grows independently of model |

**Implementation Details:**
- Vector embeddings using `sentence-transformers`
- FAISS for efficient similarity search
- Hybrid search (vector + keyword)
- Context window management (sliding window)

---

## 📅 Calendar & ETL Data Flow

The calendar feature relies on a sophisticated ETL (Extract, Transform, Load) pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                     Chat Messages (Raw)                     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Message 1: "I feel lonely today..."                 │  │
│  │  • Emotion: sad                                       │  │
│  │  • Loneliness: 8                                      │  │
│  │  • Timestamp: 2024-01-15 09:30                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Message 2: "Thanks for listening..."                │  │
│  │  • Emotion: neutral                                   │  │
│  │  • Loneliness: 6                                      │  │
│  │  • Timestamp: 2024-01-15 09:45                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Message 3: "I'm feeling better now"                 │  │
│  │  • Emotion: joy                                       │  │
│  │  • Loneliness: 4                                      │  │
│  │  • Timestamp: 2024-01-15 10:15                        │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│            Daily Aggregation (Group by Date + User)         │
│                                                               │
│  Extract:                                                    │
│  • Fetch all messages for date range                         │
│  • Group by (date, user_id)                                  │
│                                                               │
│  Transform:                                                  │
│  • Calculate dominant emotion (mode)                         │
│  • Compute average loneliness score                          │
│  • Count total messages                                      │
│  • Identify crisis messages                                  │
│  • Generate AI summary prompt                                │
│                                                               │
│  Load:                                                       │
│  • Upsert into daily_emotion_summaries table                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dagster ETL Job                           │
│                                                               │
│  Schedule: Daily at 2:00 AM UTC                              │
│  Trigger: On-demand via API                                  │
│                                                               │
│  Steps:                                                      │
│  1. Extract messages from previous day                       │
│  2. Calculate statistical aggregations                       │
│  3. Call LLM for daily summary generation                    │
│  4. Data quality validation                                  │
│  5. Write to daily_emotion_summaries                         │
│  6. Update analytics cache                                   │
│  7. Send notifications (if configured)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         daily_emotion_summaries Table (Aggregated)          │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  date: 2024-01-15                                     │  │
│  │  user_id: 123                                         │  │
│  │  dominant_emotion: "sad"                              │  │
│  │  avg_loneliness_score: 6.0                            │  │
│  │  message_count: 3                                     │  │
│  │  crisis_detected: false                               │  │
│  │  ai_summary: "User expressed loneliness in..."        │  │
│  │  created_at: 2024-01-16 02:05:00                      │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Calendar & Analytics APIs                      │
│                                                               │
│  GET /api/calendar/month?year=2024&month=1                   │
│  • Returns daily summaries for calendar grid                 │
│                                                               │
│  GET /api/calendar/day/{date}                               │
│  • Returns detailed summary + message list                   │
│                                                               │
│  GET /api/calendar/weekly-trend?week=3                       │
│  • Returns 7-day emotion & loneliness trends                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 React Components                            │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Calendar Grid Component                              │  │
│  │  • Renders month view                                 │  │
│  │  • Color-codes emotions                               │  │
│  │  • Shows message count badges                         │  │
│  │  • Click handler for day details                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Recharts Analytics                                   │  │
│  │  • Line chart: loneliness over time                   │  │
│  │  • Bar chart: message frequency                       │  │
│  │  • Pie chart: emotion distribution                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

![ETL Flow Diagram](screenshots/etl-flow.png)

**Benefits of ETL Approach:**
- ⚡ **Performance** - Pre-aggregated data = fast queries
- 📊 **Consistency** - Single source of truth for analytics
- 🔄 **Scalability** - Handles millions of messages efficiently
- 🧹 **Data Quality** - Validation and cleaning at ETL stage
- 🤖 **AI Summaries** - Automated daily reflections without blocking user interactions

---

## 🗂️ Project Structure

### Backend Structure

```
backend/
├── app/
│   ├── api/                     # API route handlers
│   │   ├── chat.py              # Chat endpoints (send, edit, regenerate)
│   │   ├── calendar.py          # Calendar data endpoints
│   │   ├── sessions.py          # Session management
│   │   ├── users.py             # User authentication
│   │   └── health.py            # Health check endpoint
│   │
│   ├── db/                      # Database layer
│   │   ├── models.py            # SQLAlchemy ORM models
│   │   ├── crud.py              # Database operations
│   │   └── database.py          # DB connection setup
│   │
│   ├── core/                    # Core configurations
│   │   ├── auth.py              # JWT handling, password hashing
│   │   ├── config.py            # Environment variables
│   │   └── security.py          # Security utilities
│   │
│   ├── services/                # Business logic layer
│   │   ├── llm.py               # LLM API integration (OpenAI/Anthropic)
│   │   ├── rag.py               # RAG implementation
│   │   ├── emotion.py           # Emotion classification
│   │   ├── loneliness.py        # Loneliness scoring algorithm
│   │   ├── safety_check.py      # Crisis detection
│   │   └── drift.py             # Model drift monitoring
│   │
│   ├── middleware/              # Custom middleware
│   │   ├── auth.py              # JWT validation middleware
│   │   ├── rate_limit.py        # Rate limiting
│   │   └── logging.py           # Request/response logging
│   │
│   ├── schemas/                 # Pydantic models
│   │   ├── user.py
│   │   ├── message.py
│   │   └── analytics.py
│   │
│   └── main.py                  # FastAPI application entry point
│
├── dagster/                     # ETL orchestration
│   ├── jobs/                    # ETL job definitions
│   │   ├── daily_summary.py     # Daily emotion aggregation
│   │   └── weekly_report.py     # Weekly analytics
│   ├── assets/                  # Data assets
│   └── repository.py            # Dagster repository
│
├── tests/                       # Test suite
│   ├── test_api/
│   ├── test_services/
│   └── test_db/
│
├── alembic/                     # Database migrations
│   └── versions/
│
├── requirements.txt
└── README.md
```

### Frontend Structure

```
frontend/
├── src/
│   ├── components/              # React components
│   │   ├── ChatSidebar.jsx      # Session list sidebar
│   │   ├── ChatWindow.jsx       # Main chat interface
│   │   ├── MessageBubble.jsx    # Individual message component
│   │   ├── Calendar.jsx         # Emotion calendar view
│   │   ├── Analytics.jsx        # Dashboard charts
│   │   └── EditMessageModal.jsx # Edit functionality
│   │
│   ├── pages/                   # Page components
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   └── ChatPage.jsx
│   │
│   ├── services/                # API client
│   │   ├── api.js               # Axios instance + interceptors
│   │   ├── authService.js       # Login/logout methods
│   │   └── chatService.js       # Chat-related API calls
│   │
│   ├── contexts/                # React context providers
│   │   ├── AuthContext.jsx      # Authentication state
│   │   └── ChatContext.jsx      # Active session state
│   │
│   ├── hooks/                   # Custom React hooks
│   │   ├── useAuth.js
│   │   └── useChat.js
│   │
│   ├── utils/                   # Utility functions
│   │   ├── dateFormatter.js
│   │   └── emotionColors.js
│   │
│   └── App.js                   # Root component
│
├── public/
│   └── index.html
│
├── package.json
└── README.md
```

---

## 🔐 Authentication & Middleware Design

This project follows **enterprise-grade authentication patterns** inspired by Spring Boot and Django:

### JWT Flow

```
1. User Login
   │
   ▼
2. Credentials Validation
   │  (bcrypt password check)
   ▼
3. JWT Token Generation
   │  {user_id, email, exp}
   ▼
4. Token Returned to Client
   │  (stored in localStorage)
   ▼
5. Client Includes Token
   │  Authorization: Bearer <token>
   ▼
6. Middleware Validates JWT
   │  (FastAPI dependency)
   ▼
7. Request Proceeds
   │  (user_id extracted from token)
   ▼
8. Response Returned
```

### Middleware Philosophy

| Layer | Responsibility | Example |
|-------|----------------|---------|
| **Authentication** | Verify user identity | JWT validation |
| **Authorization** | Check permissions | User owns session? |
| **Validation** | Input sanitization | Pydantic schemas |
| **Logging** | Request tracking | Structured logging |
| **Error Handling** | Consistent responses | Global exception handler |

**Key Security Features:**
- 🔒 **Password Hashing** - bcrypt with salt
- 🔑 **JWT Tokens** - Short-lived, stateless
- 🚫 **CORS Protection** - Configurable origins
- ⏱️ **Rate Limiting** - Prevent abuse
- 🔍 **SQL Injection Prevention** - ORM-based queries

---

## ✏️ Edit & Regenerate Design Rules

Mimics ChatGPT's behavior for intuitive UX:

| Rule | Description | Rationale |
|------|-------------|-----------|
| ✅ **Editable** | Only latest **user** message | Prevents timeline corruption |
| 🔄 **Regeneration** | Deletes assistant reply | Maintains cause-effect relationship |
| 🔒 **Integrity** | No rewriting of history | Ensures analytics accuracy |
| 🎯 **UX Match** | ChatGPT-style behavior | Familiar user experience |

### Technical Implementation

```python
# Edit endpoint
@router.put("/message/{message_id}")
async def edit_message(
    message_id: int,
    new_content: str,
    user: User = Depends(get_current_user)
):
    # 1. Verify message is user's latest
    # 2. Update message content
    # 3. Soft-delete assistant's response
    # 4. Regenerate new response
    # 5. Return updated conversation
```

---

## 📊 Weekly Emotion Analytics

The analytics dashboard provides actionable insights through multiple visualization types:

- **📈 Weekly emotion & loneliness trends** - Line charts showing emotional trajectories
- **📊 Message frequency visualization** - Bar charts indicating engagement patterns
- **🎨 Built using Recharts** - Production-ready charting library
- **⚡ Backed by aggregated daily summaries** - ETL-driven data pipeline for performance

**Insights Provided:**
- Are loneliness scores improving over time?
- Which days see the most/least engagement?
- Correlation between message frequency and emotional states
- Weekly emotional patterns and trends

---

## 📷 Screenshots

### System Architecture Flowcharts

#### 1. General System Flow
![General System Flow](screenshots/general-architecture.png)
*Complete architecture from React frontend through FastAPI backend to PostgreSQL and Dagster ETL*

---

#### 2. Backend Services Architecture
![Backend Services Architecture](screenshots/backend-services.png)
*Service layer organization including LLM, RAG, emotion analysis, and safety check services*

---

#### 3. RAG Flow
![RAG Flow Diagram](screenshots/rag-flow.png)
*Retrieval-Augmented Generation process with context retrieval and LLM integration*

---

#### 4. ETL Flow
![ETL Flow Diagram](screenshots/etl-flowchart.png)
*Data pipeline showing chat message transformation into aggregated daily summaries*

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 16+**
- **PostgreSQL 13+**
- **pip / npm**

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials and API keys

# Run database migrations
alembic upgrade head

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

---

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with API base URL

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

---

### Dagster ETL Setup

```bash
# Navigate to dagster directory
cd backend/dagster

# Set environment variables
export DAGSTER_HOME=$(pwd)

# Start Dagster daemon (for scheduled jobs)
dagster-daemon run

# Start Dagster UI (in separate terminal)
dagster dev
```

Dagster UI will be available at `http://localhost:3000`

---

### Environment Variables

#### Backend `.env`

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/mental_health_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI / Anthropic
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

#### Frontend `.env`

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_ENVIRONMENT=development
```

---

## 🔌 API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/users/register` | Create new user account |
| `POST` | `/api/users/login` | Login and receive JWT token |
| `POST` | `/api/users/logout` | Logout (client-side token removal) |
| `GET` | `/api/users/me` | Get current user profile |

---

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Send message and receive AI response |
| `GET` | `/api/chat/sessions` | List all user chat sessions |
| `POST` | `/api/chat/sessions` | Create new chat session |
| `GET` | `/api/chat/history/{session_id}` | Get messages for a session |
| `PUT` | `/api/chat/{session_id}/message/{message_id}` | Edit user message |
| `POST` | `/api/chat/{session_id}/regenerate` | Regenerate last AI response |
| `DELETE` | `/api/chat/sessions/{session_id}` | Delete chat session |

---

### Calendar Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/calendar/month` | Get emotion data for entire month |
| `GET` | `/api/calendar/day/{date}` | Get detailed data for specific day |
| `GET` | `/api/calendar/weekly-trend` | Get 7-day emotion trend |

---

### Analytics Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/analytics/weekly` | Weekly emotion and message stats |
| `GET` | `/api/analytics/monthly` | Monthly aggregated insights |
| `GET` | `/api/analytics/emotion-distribution` | Emotion percentage breakdown |

---

### Example API Request

```bash
# Login
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com"
  }
}

# Send chat message
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"session_id": 1, "content": "I feel lonely today"}'

# Response
{
  "message_id": 42,
  "ai_response": "I hear that you're feeling lonely...",
  "emotion": "sadness",
  "loneliness_score": 7.5
}
```

---

## 🧪 Data Models

### User Model

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = relationship("Session", back_populates="user")
```

---

### Session Model

```python
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session")
```

---

### Message Model

```python
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    role = Column(Enum("user", "assistant"))
    content = Column(Text, nullable=False)
    
    # AI-generated metadata
    emotion = Column(String)  # joy, sadness, anger, etc.
    loneliness_score = Column(Float)  # 1-10 scale
    is_crisis = Column(Boolean, default=False)
    
    # Lifecycle
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    edited_at = Column(DateTime, nullable=True)
    
    # Relationships
    session = relationship("Session", back_populates="messages")
```

---

### DailyEmotionSummary Model

```python
class DailyEmotionSummary(Base):
    __tablename__ = "daily_emotion_summaries"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, nullable=False)
    
    # Aggregated data
    dominant_emotion = Column(String)
    avg_loneliness_score = Column(Float)
    message_count = Column(Integer)
    
    # AI-generated
    ai_summary = Column(Text)
    
    # ETL metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='unique_user_date'),
    )
```

---

## 🛠️ Why This Project Is Enterprise-Ready

This isn't a prototype or proof-of-concept—it's built with production principles:

| Principle | Implementation |
|-----------|----------------|
| **Separation of Concerns** | Clear API / Service / CRUD layers |
| **Middleware-First** | JWT, validation, logging at middleware level |
| **Stateless Authentication** | JWT tokens, no server-side sessions |
| **ETL-Driven Analytics** | Pre-aggregated data for performance |
| **RAG Architecture** | Context-aware AI with vector search |
| **Scalable Data Models** | Optimized indexes, temporal partitioning |
| **Test Coverage** | Unit, integration, and E2E tests |
| **CI/CD Ready** | Docker, GitHub Actions workflows |
| **Monitoring** | Structured logging, error tracking |
| **Documentation** | API docs (OpenAPI), architecture diagrams |

**Production Deployment Considerations:**
- ✅ Horizontal scaling (stateless design)
- ✅ Database connection pooling
- ✅ Redis caching layer
- ✅ Rate limiting per user
- ✅ HTTPS enforcement
- ✅ Environment-based configuration
- ✅ Automated backups
- ✅ Model versioning for A/B testing

---

## 🔮 Future Enhancements

### Near-Term (Next 3 Months)

- [ ] **Therapist / Admin Dashboard**
  - Aggregated patient insights
  - Alert system for crisis detection
  - Anonymized analytics

- [ ] **Push Notifications**
  - Daily check-in reminders
  - Motivational messages
  - Crisis follow-ups

- [ ] **PDF Emotional Reports**
  - Weekly/monthly summaries
  - Exportable for therapists
  - Data visualization

---

### Mid-Term (6 Months)

- [ ] **Mobile App** (React Native)
  - iOS and Android
  - Push notifications
  - Offline mode

- [ ] **Multi-Language AI**
  - Spanish, French, Mandarin
  - Cultural adaptation

- [ ] **Voice Interaction**
  - Speech-to-text
  - Emotional tone analysis

---

### Long-Term (1 Year)

- [ ] **Wearable Data Integration**
  - Heart rate variability
  - Sleep patterns
  - Activity levels

- [ ] **Group Therapy Sessions**
  - Anonymous chat rooms
  - Moderated discussions

- [ ] **Insurance Integration**
  - HIPAA compliance
  - Claims processing

---

## 👤 Author

**Uthayasurian Salavamani**  
*Junior Software Engineer*  
📍 Klang, Malaysia

[![GitHub](https://img.shields.io/badge/GitHub-uthaya98-181717?style=for-the-badge&logo=github)](https://github.com/uthaya98)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Uthaya%20Surian-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/uthaya-surian-019853125)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - UI library
- **OpenAI / Anthropic** - LLM providers
- **Dagster** - Data orchestration
- **Recharts** - Data visualization
- **Hugging Face** - Emotion classification models

---

## ⭐ Final Note

This project demonstrates how **AI, middleware, analytics, and frontend engineering** can be combined into a cohesive, production-grade system.

**Suitable For:**
- 🎤 **Technical interviews** - Showcase full-stack and AI capabilities
- 🎓 **Academic presentations** - Demonstrate software engineering principles
- 🚀 **Proof-of-concept demos** - Validate mental health tech ideas
- 🏢 **Real-world expansion** - Foundation for commercial products

---

<div align="center">

**🚀 Built with scalability, safety, and clarity in mind.**

![Made with Love](https://img.shields.io/badge/Made%20with-❤-red?style=for-the-badge)

</div>
