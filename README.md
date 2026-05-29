# StudyRoom

A real-time collaborative study room platform built using FastAPI, Next.js, PostgreSQL, Redis, and WebSockets.

## Live Demo

Frontend:
[StudyRoom Frontend](https://study-room-mu-orcin.vercel.app)

Backend API:
[StudyRoom API](https://studyapi.granth.tech/health)

---

# Overview

StudyRoom is a full-stack collaborative platform designed to enable users to create and join shared study rooms with real-time communication and synchronized study sessions.

The application focuses on:

* real-time collaboration
* scalable async backend architecture
* responsive frontend UX
* production-ready deployment
* modular maintainable code structure

The project was implemented as Assessment 4 and includes several additional enhancements beyond the mandatory deliverables.

---

# Features

## Authentication

* JWT-based authentication
* Secure login and registration
* Persistent auth state
* Protected frontend routes

## Study Rooms

* Create public study rooms
* Browse active public rooms
* Join collaborative study spaces
* View active participants

## Real-Time Collaboration

* WebSocket-powered real-time communication
* Live participant presence tracking
* Instant room updates
* Real-time synchronization across clients

## Study Sessions

* Start/end collaborative study sessions
* Single active session per room
* Shared session state synchronization

## Modern Frontend

* Responsive Next.js frontend
* Modern dark-mode UI
* Reusable component architecture
* Mobile-friendly layouts

---


# Additional Enhancements

The following additional features and improvements were implemented beyond the basic assessment requirements:

* Full production deployment
* HTTPS-enabled backend deployment
* Dockerized backend infrastructure
* Redis Pub/Sub real-time architecture
* WebSocket room synchronization
* Load testing using Locust
* Async PostgreSQL integration
* Responsive UI redesign
* Production-grade Nginx reverse proxy setup
* Persistent authentication state handling
* Structured backend service/repository architecture

---

# Tech Stack

## Frontend

* Next.js (App Router)
* React
* TypeScript
* Tailwind CSS
* Zustand
* TanStack Query

## Backend

* FastAPI
* SQLAlchemy
* Alembic
* Pydantic
* AsyncIO
* WebSockets

## Infrastructure & DevOps

* Docker
* Nginx
* AWS EC2
* Vercel

## Database & Realtime

* PostgreSQL (Neon)
* Redis Pub/Sub (Upstash Redis)

## Testing

* Pytest
* Locust

---

# Architecture

## Frontend Architecture

The frontend is structured using Next.js App Router and reusable UI primitives. Zustand is used for authentication and client-side realtime state management, while TanStack Query manages API synchronization and caching.

## Backend Architecture

The backend follows a layered architecture pattern:

```text id="9d2mqp"
API Routes
    ↓
Services
    ↓
Repositories
    ↓
Database Models
```

This separation improves maintainability, testing, and scalability.

## Real-Time System

Real-time communication is implemented using:

* FastAPI WebSockets
* Redis Pub/Sub
* Centralized WebSocket connection manager

This architecture enables:

* scalable room broadcasts
* synchronized room state
* real-time participant updates
* instant message propagation

## Performance Testing & Production Validation

The application was load tested using Locust to validate concurrent request handling, API responsiveness, and realtime synchronization stability in a production deployment environment.

### Validation Highlights

* Concurrent user simulation using Locust
* Stable WebSocket synchronization under concurrent activity
* Low average API response times (~40ms–120ms)
* P95 response times remained under ~250ms during normal concurrent load
* Near-zero error rate after deployment stabilization
* Stable Redis Pub/Sub communication
* Successful Dockerized production deployment on AWS EC2 with HTTPS-enabled Nginx reverse proxy

### Production Engineering Improvements

During deployment and testing, several production-stage issues were identified and resolved, including:

* PostgreSQL SSL configuration handling
* Alembic migration orchestration
* Docker dependency management
* CORS configuration
* WebSocket proxying through Nginx
* Environment variable synchronization

These improvements significantly enhanced deployment reliability and realtime system stability.

---

# Project Structure

```text id="7f1wla"
study-room/
├── frontend/
│   ├── app/
│   ├── hooks/
│   ├── lib/
│   ├── store/
│   ├── types/
│   └── components/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── redis/
│   │
│   ├── alembic/
│   ├── tests/
│   ├── docker/
│   └── scripts/
│
└── README.md
```

---

# Local Development Setup

## Prerequisites

* Node.js
* Python 3.12+
* Docker
* PostgreSQL
* Redis

---

# Backend Setup

```bash id="4x7nzb"
cd backend

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

alembic upgrade head

uvicorn app.main:app --reload
```

Backend runs on:

```text id="q1v6ht"
http://localhost:8000
```

---

# Frontend Setup

```bash id="8j3pyr"
cd frontend

npm install

npm run dev
```

Frontend runs on:

```text id="0m4cza"
http://localhost:3000
```

---

# Environment Variables

## Backend

```env id="5b9kds"
DATABASE_URL=
REDIS_URL=
JWT_SECRET_KEY=
ALLOWED_ORIGINS=
```

## Frontend

```env id="2q7nex"
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_WS_URL=
```

---

# Deployment

## Frontend Deployment

The frontend is deployed on Vercel.

## Backend Deployment

The backend is containerized using Docker and deployed on AWS EC2 behind an Nginx reverse proxy with HTTPS enabled via Let's Encrypt.

## Infrastructure Overview

```text id="1r9kcv"
Frontend (Vercel)
        ↓
HTTPS Requests
        ↓
Nginx Reverse Proxy
        ↓
FastAPI Backend (Docker)
        ↓
PostgreSQL + Redis
```

---

# API Design

REST APIs are exposed under:

```text id="6n2yaf"
/api/v1
```

Core API groups:

* Authentication
* Users
* Rooms
* Sessions
* WebSocket endpoints

---

# Performance & Load Testing

The backend was load tested using Locust to validate concurrent request handling and realtime stability.

## Tested Operations

* User registration
* Authentication
* Room creation
* Public room listing
* Room detail retrieval
* Session start/end
* User profile retrieval
* Health checks

## Load Testing Results

The deployed backend maintained:

* stable API responsiveness under concurrent load
* low average response times
* consistent request throughput
* successful concurrent session handling
* stable Redis Pub/Sub communication
* reliable WebSocket synchronization

## Engineering Optimizations

Performance improvements included:

* async FastAPI endpoints
* async SQLAlchemy engine
* Redis Pub/Sub event propagation
* connection pooling
* stateless JWT authentication
* Dockerized deployment
* Nginx reverse proxying

## Observations

During deployment and testing, production bottlenecks related to:

* PostgreSQL SSL configuration
* migration orchestration
* Docker dependency management
* CORS handling

were identified and resolved successfully.

---

# Design Decisions

## PostgreSQL over MongoDB

PostgreSQL was selected due to:

* strong relational consistency
* transactional guarantees
* structured room/session relationships
* scalability for collaborative systems

## FastAPI

FastAPI was chosen because of:

* async-first architecture
* native WebSocket support
* clean typing support
* high development velocity

## Redis Pub/Sub

Redis was used to support:

* real-time room synchronization
* scalable websocket broadcasting
* low-latency event propagation

---

# Future Improvements

* Voice/video study rooms
* Room moderation tools
* Notifications
* File sharing
* Collaborative notes
* Horizontal WebSocket scaling
* Study analytics dashboard

---

# Author

Granth Agarwal

Portfolio:
[granth.tech](https://granth.tech)

GitHub:
[GitHub Profile](https://github.com/hey-granth)

---

# License

This project was developed as part of a technical assessment and portfolio project.
