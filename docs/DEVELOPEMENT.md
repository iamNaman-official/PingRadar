# 🚀 PingRadar Development Journey

## Overview

PingRadar started as a learning project to understand backend engineering by building a real-world website uptime monitoring system.

The goal was not only to create a functional application, but also to explore how backend systems are designed, structured, tested, optimized, and improved over time.

Throughout the development of PingRadar, I focused on understanding:

- Django application architecture
- Database design and relationships
- Django ORM
- Authentication and authorization
- Asynchronous programming
- Background processing
- Automated testing
- Performance optimization
- CI/CD practices

PingRadar represents my journey from building basic Django functionality to understanding real backend engineering concepts.

---

# 🎯 Project Goals

The main objectives behind PingRadar were:

## Learn Django Beyond Basic CRUD

Instead of only creating simple database operations, the project focused on:

- Designing models
- Managing relationships
- Creating secure views
- Structuring applications
- Understanding Django internals


## Understand Backend Architecture

The project helped me understand:

- How web applications are structured
- How different components communicate
- Why background processes are needed
- How databases interact with applications


## Explore Asynchronous Programming

Website monitoring involves multiple network requests.

The project was used to understand:

- I/O-bound workloads
- Event loops
- Concurrent execution
- Async HTTP requests


## Build Engineering Practices

The project introduced:

- Automated testing
- Code quality checks
- CI pipelines
- Documentation
- Performance benchmarking

---

# 🏗️ Development Phases

## Phase 1: Django Foundation

The initial phase focused on understanding Django fundamentals.

Implemented:

- Django project setup
- Application structure
- URLs
- Views
- Templates
- Models
- Database migrations


Key learning:

Understanding the difference between:

```
Django Project
        |
        |
Django Applications
        |
        |
Models, Views, Templates
```

This helped establish a proper project structure before adding advanced features.

---

# Phase 2: Database Design

The next step was designing the database structure.

PingRadar uses two main models:

---

## Website Model

Responsible for storing monitored website information.

Stores:

- Website owner
- Website name
- URL
- Creation timestamp
- Pause status


Important concepts learned:

- ForeignKey relationships
- Model methods
- Database constraints
- Query optimization


---

## StatusCheck Model

Stores monitoring results.

Stores:

- Website relationship
- Website availability
- HTTP status code
- Response time
- Timestamp


This allows PingRadar to maintain monitoring history.

---

# Phase 3: Authentication and Authorization

Authentication was added using Django's built-in authentication system.

Implemented:

- User registration
- Login
- Session management
- User-specific websites


A major learning was understanding the difference between:

## Authentication

```
Who are you?
```

Example:

A user logs into PingRadar.


## Authorization

```
What are you allowed to access?
```

Example:

A user can only access their own websites.


Security improvement:

Before:

```
/website/5
```

could potentially expose another user's data.


After:

```
Website access is restricted by ownership.
```

---

# Phase 4: Building the Monitoring System

The first design idea was:

```
Django View

      |
      |
Check Website

      |
      |
Save Result
```

However, this approach creates problems:

- Slow HTTP responses
- Blocking requests
- Poor scalability
- Difficult debugging


The architecture was improved by separating monitoring from the web application.

New design:

```
Django Application

        +

Monitoring Worker
```

The Django application handles:

- Users
- Dashboard
- Website management


The monitoring worker handles:

- Website checks
- HTTP requests
- Status recording

---

# Phase 5: Async Programming

Website monitoring is an I/O-heavy workload.

Most of the time is spent waiting for external servers.

Example:

Sequential approach:

```
Website A
   |
   wait
   |
Website B
   |
   wait
   |
Website C
```

Each request blocks the next request.


Async approach:

```
Website A ───┐
Website B ───┼── asyncio.gather()
Website C ───┘
```

Multiple requests can wait at the same time.


PingRadar uses:

- asyncio
- httpx.AsyncClient
- concurrent tasks


Through this, I learned:

- Event loops
- Async functions
- Task scheduling
- Concurrent I/O

---

# Phase 6: Performance Benchmarking

To understand the impact of asynchronous programming, a benchmark system was created.

Created:

```
benchmark.py
```

The benchmark compares:

## Sequential Requests

Using:

```
httpx.Client
```

Requests execute one after another.


## Concurrent Requests

Using:

```
httpx.AsyncClient
asyncio.gather()
```

Multiple requests execute concurrently.


A custom mock server was also created:

```
mock_server.py
```

It simulates:

- Successful responses
- Slow responses
- Server errors
- Timeout scenarios


This helped understand real-world performance differences between blocking and non-blocking approaches.

---

# Phase 7: Testing

Testing was added to improve reliability and confidence during development.

Implemented tests for:

## Model Testing

Covers:

- Website creation
- StatusCheck creation
- Uptime calculation
- Latest status retrieval


## Authentication Testing

Covers:

- Signup page loading
- User registration


## Security Testing

Covers:

- User ownership protection
- Preventing unauthorized access


## View Testing

Covers:

- Dashboard access
- Website creation
- Website deletion
- Pause/resume functionality
- Duplicate website prevention


Key learning:

Testing is not only about finding bugs.

It allows developers to safely improve software without breaking existing functionality.

---

# Phase 8: Code Quality and CI/CD

To improve development workflow, automated quality checks were introduced.

Implemented:

## Ruff

Used for:

- Import checking
- Code formatting
- Code quality validation


## GitHub Actions

The CI pipeline automatically performs:

```
Code Push

      |

Install Dependencies

      |

Run Tests

      |

Run Quality Checks

      |

Build Status
```

This ensures that changes are validated before merging.

---

# 🐛 Challenges Faced During Development

## 1. Understanding Async Programming

Challenge:

Understanding why asynchronous programming improves monitoring performance.


Solution:

Built a benchmark comparing:

- Sequential HTTP requests
- Async HTTP requests


Learning:

Async improves performance for I/O-heavy workloads because waiting time can be shared between multiple tasks.

---

# 2. Separating Monitoring From Django Views

Challenge:

Initially understanding where monitoring logic should live.


Problem:

Running monitoring inside views would:

- Increase response time
- Block user requests
- Make scaling difficult


Solution:

Created a separate Django management command.

---

# 3. Understanding Database Queries

Challenge:

Learning how Django ORM translates into database queries.


Current learning:

The dashboard works correctly, but large-scale systems require query optimization.


Potential improvements:

- `select_related()`
- `prefetch_related()`
- Database annotations
- Better indexing


---

# 4. Implementing Ownership Security

Challenge:

Ensuring users cannot access other users' websites.


Solution:

Added ownership-based access validation and automated tests.

---

# 🤖 AI Assisted Development

AI tools were used as development assistants and learning support throughout this project.

As a beginner exploring backend engineering, AI helped me:

- Understand Django concepts
- Explore architecture decisions
- Debug errors
- Review implementation approaches
- Improve documentation
- Learn backend concepts faster


AI was used for:

- Frontend development assistance
- UI improvement ideas
- Understanding Django architecture
- Guidance while designing models and views
- Testing strategy discussions
- Debugging support
- Documentation improvements
- Learning async programming and ORM concepts


The overall engineering decisions remained mine.

The following were designed, implemented, tested, and reviewed by me:

- Project architecture
- Database design
- Monitoring workflow
- Async implementation
- Testing strategy
- Final code decisions


AI acted as a learning companion and productivity tool while maintaining ownership of the final implementation.

---

# 📈 Current Project State

PingRadar currently supports:

✅ User authentication  
✅ Website monitoring  
✅ Async health checks  
✅ Dashboard visualization  
✅ Database tracking  
✅ Automated testing  
✅ CI pipeline  
✅ Code quality checks  
✅ Performance benchmarking  


---

# 🔮 Future Improvements

## Infrastructure

Planned:

- PostgreSQL migration
- Docker support
- Production deployment


## Background Processing

Future improvements:

- Celery
- Redis
- Multiple monitoring workers
- Scheduled tasks


## Monitoring Features

Future additions:

- Email notifications
- Discord notifications
- Telegram notifications
- Metrics collection


## Backend Improvements

Future improvements:

- REST API
- WebSocket dashboard
- Better caching
- Advanced query optimization

---

# 🧠 Interview Discussion Points

## Why use a Django management command?

A management command allows background scripts to run inside the Django environment.

Benefits:

- Access to Django ORM
- Reuse project configuration
- Keep monitoring logic separate from web requests


---

## Why use asyncio?

Website monitoring is an I/O-bound problem.

Asyncio allows multiple network requests to wait concurrently instead of blocking execution.


---

## Why separate monitoring from views?

Because monitoring involves external network communication.

Keeping it separate:

- Improves response speed
- Prevents blocking
- Makes the system easier to maintain


---

## Why SQLite?

SQLite was chosen because:

- Simple setup
- Good for development
- No extra infrastructure required


For production:

- PostgreSQL would provide better scalability.


---

## What would you improve next?

Possible improvements:

- Add Celery and Redis
- Move to PostgreSQL
- Optimize ORM queries
- Add real-time updates
- Add monitoring notifications


---

# 📚 Final Thoughts

PingRadar represents my progression while learning backend engineering.

The project helped me understand that backend development is not only about writing code.

It is about:

- Designing systems
- Making engineering decisions
- Understanding trade-offs
- Testing reliability
- Improving performance
- Continuously learning


The current architecture reflects my present understanding, and the project will continue evolving as I learn more about scalable backend systems.