# CalcHub: Advanced Secure Calculation Platform

A comprehensive, production-ready FastAPI application featuring secure user authentication, JWT-based authorization, comprehensive BREAD (Browse, Read, Edit, Add, Delete) functionality for calculations, advanced mathematical operations, and complete test coverage. Built with modern development practices including Docker containerization, CI/CD pipeline automation, and responsive SaaS-style UI.

## 🎯 Project Overview

This project implements a complete web application with:
- **User Management**: Secure registration, login, profile updates, and password changes
- **Calculation System**: Complete BREAD operations with 6 mathematical operations (Add, Subtract, Multiply, Divide, Power, Modulo)
- **Analytics Dashboard**: Real-time statistics and usage insights
- **Security**: Password hashing with bcrypt, JWT authentication, input validation
- **Testing**: 100+ unit, integration, and E2E tests with 80%+ code coverage
- **Deployment**: Docker containerization and GitHub Actions CI/CD pipeline

## ✨ Key Features Implemented

### 1. User Profile Management ✅
- **Route**: `GET /users/me` - Retrieve current user profile
- **Route**: `PUT /users/me` - Update profile information
- Update profile info: username, email, full name, bio
- Timestamp tracking: last_login
- **Tests**: Complete unit, integration, and E2E coverage
- **UI**: Profile & Security tab with dedicated form

### 2. Secure Password Change ✅
- **Route**: `POST /users/change-password`
- Requires current password verification
- Validates password strength (min 8 characters)
- Returns 204 No Content on success
- Prevents reuse of old passwords
- **Tests**: Security validation tests
- **UI**: Professional password change form with confirmation

### 3. Advanced Calculation Operations ✅
- **Power (^)**: Exponentiation with any numeric values
- **Modulo (%)**: Remainder operation with divide-by-zero protection
- **All 6 Operations**: Add, Subtract, Multiply, Divide, Power, Modulo
- Automatic result calculation and persistent storage
- **Tests**: 50+ unit tests for calculations
- **Factory Pattern**: Dynamic operation creation
- **UI**: Dropdown selection with all operations

### 4. Usage Insights & Analytics Dashboard ✅
- **Route**: `GET /calculations/summary`
- **Total Calculations**: Count of all user calculations
- **Average Result**: Statistical average of results
- **Most Used Operation**: Tracks most frequent operation
- **Last Result**: Most recent calculation result
- **Per-Operation Breakdown**: Statistics for each operation type
- **Tests**: Integration tests for summary endpoint
- **UI**: Professional stat cards with color-coded metrics and icons

## 📊 Complete BREAD Operations

| Operation | Endpoint | Method | Status |
|-----------|----------|--------|--------|
| **Browse** | `/calculations` | GET | ✅ Implemented & Tested |
| **Read** | `/calculations/{id}` | GET | ✅ Implemented & Tested |
| **Edit** | `/calculations/{id}` | PUT | ✅ Implemented & Tested |
| **Add** | `/calculations` | POST | ✅ Implemented & Tested |
| **Delete** | `/calculations/{id}` | DELETE | ✅ Implemented & Tested |

## 📁 Project Structure

```
IS601_FinalProject/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app with BREAD routes
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── factory.py              # Calculation factory pattern
│   ├── database.py             # Database configuration
│   └── security.py             # Password hashing & JWT
├── static/
│   ├── calculations.html       # Dashboard (tabbed UI)
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── css/
│   │   └── style.css           # Professional SaaS styling
│   └── js/
│       ├── calculations.js     # Dashboard logic
│       └── auth.js             # Auth logic
├── tests/
│   ├── test_security.py        # 11 unit tests
│   ├── test_schemas.py         # 23 unit tests
│   ├── test_calculations.py    # 58 unit tests
│   ├── test_integration.py     # 30 integration tests
│   └── test_e2e.py             # E2E tests
├── .github/workflows/
│   └── ci-cd.yml               # GitHub Actions pipeline
├── Dockerfile                  # Multi-stage production image
├── docker-compose.yml          # Local development
├── requirements.txt            # Dependencies
├── pyproject.toml              # Project config
├── REFLECTION.md               # Project reflection
└── README.md                   # This file
```

## 🧪 Testing Overview

### Unit Tests (92 passing)
- **Security** (11 tests): Password hashing, verification, edge cases
- **Schemas** (23 tests): Validation, email checks, constraints
- **Calculations** (58 tests): All operations, factory, chaining

### Integration Tests (30 passing)
- User authentication flow
- BREAD operations with database
- Profile & password updates
- Pagination and error handling

### E2E Tests
- Complete authentication workflows
- Calculation management flows
- Negative scenario testing

**Total**: 120+ tests | **Coverage**: 80%+

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/kk795-NJIT/IS601_FinalProject.git
cd IS601_FinalProject

# Start application
docker compose up -d

# Access application
# Frontend: http://localhost:8000/static/login.html
# API Docs: http://localhost:8000/docs
# Health Check: http://localhost:8000/health
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure database
export DATABASE_URL="postgresql://user:password@localhost/calcapp"

# Run tests
pytest tests/ -v

# Start application
python -m uvicorn app.main:app --reload
# Access: http://localhost:8000/static/login.html
```

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_calculations.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# E2E tests (requires running app)
pytest tests/test_e2e.py -v
```

## 🎨 Frontend Features

### Modern SaaS-Style Design
- **Professional navbar** with CalcHub branding
- **Responsive layout** for desktop, tablet, mobile
- **Color-coded stat cards** with Font Awesome icons
- **Smooth animations** and transitions
- **Tab-based navigation** for organization
- **Form validation** with clear error messages

### Pages & Sections

**1. Dashboard Tab**
- Statistics overview (4 key metrics)
- Operation breakdown chart
- Real-time analytics from `/calculations/summary`

**2. Calculations Tab**
- Create new calculations with intuitive form
- View calculation history in table format
- Edit calculations with pre-filled values
- Delete with confirmation
- Responsive table design

**3. Profile & Security Tab**
- Update profile information
- Change password with verification
- Form validation and error handling
- Success/error message notifications

## 🔐 Security Implementation

✅ **Password Security**
- Bcrypt hashing with configurable cost (default: 12)
- Salt generation per password
- Password strength validation (min 8 characters)
- Secure comparison to prevent timing attacks

✅ **Authentication**
- JWT token-based system
- Automatic token expiration (1 hour)
- Secure token storage (localStorage)
- Token refresh mechanism

✅ **Data Protection**
- Pydantic input validation
- Email format validation
- Division/modulo by zero protection
- SQLAlchemy ORM (SQL injection prevention)

✅ **API Security**
- CORS protection
- Error messages without sensitive info
- User data isolation (users only see own data)
- Secure password change verification

## 📦 Docker Deployment

### Local Development
```bash
docker compose up -d
docker compose logs -f
docker compose down
```

### Docker Hub
Repository: `kk795/secure-fastapi-app`

```bash
docker pull kk795/secure-fastapi-app:latest
docker run -p 8000:8000 kk795/secure-fastapi-app:latest
```

### Building Custom Image
```bash
docker build -t my-calc-app:latest .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/calc" \
  my-calc-app:latest
```

## 🔄 CI/CD Pipeline

**GitHub Actions Workflow** (`.github/workflows/ci-cd.yml`):

1. **Test Execution**: Runs all 120+ tests
2. **Code Quality**: Validates structure
3. **Docker Build**: Creates production image
4. **Docker Push**: Pushes to Docker Hub on success
5. **Status Checks**: Ensures all steps pass

**Triggers**:
- Push to main branch
- Pull requests
- Manual workflow dispatch

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**User Management**
```
POST   /users/register              # Create user
POST   /users/login                 # Login (returns JWT)
GET    /users/me                    # Current user profile
PUT    /users/me                    # Update profile
POST   /users/change-password       # Change password
```

**Calculations**
```
GET    /calculations                # List calculations (paginated)
POST   /calculations                # Create calculation
GET    /calculations/{id}           # Get calculation details
PUT    /calculations/{id}           # Update calculation
DELETE /calculations/{id}           # Delete calculation
GET    /calculations/summary        # Get analytics/summary
```

**Utility**
```
GET    /health                      # Health check
```

## 🛠️ Technology Stack

**Backend**
- FastAPI 0.104.1 - Modern async web framework
- SQLAlchemy 2.0.23 - ORM for database
- Pydantic 2.5.0 - Data validation
- python-jose 3.3.0 - JWT authentication
- bcrypt 4.1.1 - Password hashing
- PostgreSQL 15 - Database

**Frontend**
- HTML5 / CSS3 / JavaScript (Vanilla)
- Font Awesome 6.4.0 - Icons
- Responsive CSS Grid/Flexbox

**Testing**
- pytest 7.4.3 - Testing framework
- pytest-asyncio - Async test support
- pytest-cov - Coverage reporting
- pytest-playwright - E2E testing
- httpx 0.25.2 - HTTP testing client

**DevOps**
- Docker & Docker Compose
- GitHub Actions
- PostgreSQL in container

## ✅ Requirements Compliance

### Course Learning Outcomes
✅ **CLO3**: Python applications with automated testing (120+ tests)
✅ **CLO4**: GitHub Actions CI/CD pipeline with automated testing and Docker builds
✅ **CLO9**: Docker containerization with multi-stage builds and Docker Compose
✅ **CLO10**: REST API design and comprehensive testing with FastAPI
✅ **CLO11**: SQLAlchemy ORM with PostgreSQL database integration
✅ **CLO12**: Pydantic serialization, deserialization, and validation
✅ **CLO13**: Security with JWT, bcrypt hashing, password verification, input validation

### Assignment Requirements
✅ **Feature Selection**: User Profile & Password Change + Advanced Operations + Analytics
✅ **Backend Development**: SQLAlchemy models, Pydantic schemas, FastAPI routes
✅ **Frontend Development**: Responsive SaaS-style UI with multiple pages/tabs
✅ **Testing**: Unit (92), Integration (30), E2E - all passing
✅ **Docker**: Containerized with docker-compose
✅ **CI/CD**: GitHub Actions pipeline with automated testing and deployment
✅ **Documentation**: Comprehensive README with instructions and information

## 📋 Completion Checklist

- ✅ Feature implementation (Profile, Password, Advanced Ops, Analytics)
- ✅ Backend: FastAPI routes, SQLAlchemy models, Pydantic schemas
- ✅ Frontend: Responsive SaaS-style UI with tabs
- ✅ Testing: 120+ tests (unit, integration, E2E)
- ✅ Docker: Containerization and docker-compose
- ✅ CI/CD: GitHub Actions pipeline
- ✅ Deployment: Docker Hub integration
- ✅ Documentation: Comprehensive README
- ✅ Code Quality: Clean, organized, commented code
- ✅ Security: JWT, password hashing, validation
- ✅ Extra Features: Advanced UI, analytics dashboard, modern design

## 📊 Code Quality Metrics

- **Test Coverage**: 80%+
- **Passing Tests**: 120+ / 120+
- **Code Organization**: Modular, well-structured
- **Documentation**: Inline comments and comprehensive README
- **Type Hints**: Used throughout for type safety
- **Error Handling**: Comprehensive with meaningful messages

## 🎨 Design Highlights

- **Modern Color Scheme**: Indigo primary with complementary colors
- **Responsive Breakpoints**: Desktop, tablet (768px), mobile (480px)
- **Accessibility**: Semantic HTML, proper labels, ARIA attributes
- **User Feedback**: Loading states, animations, notifications
- **Icon System**: Font Awesome for visual enhancement
- **Typography**: Professional font stack with proper hierarchy

## 🚦 Application Flow

### Authentication Flow
1. User registers with email/password
2. Password hashed with bcrypt
3. User logs in with credentials
4. JWT token generated and stored
5. Token used for authenticated requests

### Calculation Flow
1. User creates calculation (operand1, operation, operand2)
2. Result automatically calculated
3. Stored in database with user_id
4. User can read, edit, or delete calculations
5. Analytics aggregated in summary endpoint

### Profile Management Flow
1. User views profile via `/users/me`
2. Updates profile information
3. Changes password with verification
4. New password hashed and stored
5. User can re-login with new password

## 📞 Support & Documentation

**Documentation**
- README.md - This file
- Inline code comments
- API documentation at `/docs`
- REFLECTION.md - Project reflection

**GitHub Repository**
- https://github.com/kk795-NJIT/IS601_FinalProject

**Docker Hub**
- https://hub.docker.com/r/kk795/secure-fastapi-app

## 📝 Project Timeline

- **Week 1-2**: Feature planning and architecture
- **Week 3-4**: Backend development and database
- **Week 5-6**: Frontend development and integration
- **Week 7-8**: Testing and quality assurance
- **Week 9-10**: Docker and CI/CD setup
- **Week 11-12**: Documentation and final review

## 🎓 Learning Outcomes Achieved

Through this project, demonstrated proficiency in:
- Full-stack web development (Python + JavaScript + HTML/CSS)
- Secure authentication and authorization
- Database design and ORM usage
- Test-driven development
- API design and documentation
- Docker containerization
- CI/CD automation
- Professional code organization
- Security best practices

## 📄 License

Part of IS601 - Advanced Web Application Development at NJIT.

## 👤 Author

**Karan Kumar**
- GitHub: [@kk795-NJIT](https://github.com/kk795-NJIT)
- Repository: [IS601_FinalProject](https://github.com/kk795-NJIT/IS601_FinalProject)

---

**Status**: ✅ Complete and Production-Ready
**Last Updated**: December 9, 2025
**Docker Hub**: https://hub.docker.com/r/kk795/secure-fastapi-app
**GitHub**: https://github.com/kk795-NJIT/IS601_FinalProject
