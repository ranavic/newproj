# SkillForge - A Smart AI-Driven E-Learning Platform

SkillForge is a next-generation e-learning platform built using Django that redefines online education by integrating AI-powered personalization, gamified learning, real-time chat support, and blockchain-certified achievements.

## Key Features

- 🎯 AI-Powered Personalized Learning Paths
- 🧠 AI Tutor for Instant Doubt Solving
- 🏅 Gamified Learning System
- 🔗 Blockchain-Based Certificate Issuance
- 🤝 Peer-to-Peer Teaching & Mentoring
- 📶 Offline Study Mode with Auto-Sync
- 🌐 Multi-language Support
- 📊 Interactive Dashboards
- 🧪 Built-in Quiz Engine & Auto-Grading
- 🧩 Modular Course Marketplace

## Technologies Used

- **Backend**: Django, Django REST Framework, PostgreSQL, Celery, Redis, Django Channels
- **Frontend**: HTML5, CSS3, JavaScript, TailwindCSS
- **AI & Data**: OpenAI GPT API, Scikit-learn
- **Other Integrations**: WebRTC, Google Calendar API, IPFS

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

### Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Apply migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Run the development server: `python manage.py runserver`

## Project Modules

- User Management (Signup/Login, Roles)
- Course Creation & Management
- Quizzes & Assignments
- Live Classes & Chat
- Dashboard (Student + Teacher)
- Gamification System
- Blockchain Certification
- AI Tutor Bot
- Peer Mentorship System
- Admin Control Panel