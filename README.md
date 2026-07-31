<div align="center">

# 🚀 PingRadar

**A real-time website uptime monitor built with Django and asyncio.**

PingRadar continuously monitors websites in the background, records their
availability and response time, and visualizes uptime history through a
clean dashboard.

<p>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://www.djangoproject.com/">
    <img src="https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white" alt="Django">
  </a>
  <a href="https://docs.python.org/3/library/asyncio.html">
    <img src="https://img.shields.io/badge/Concurrency-asyncio-blue" alt="asyncio">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License">
  </a>
</p>

*An engineering-focused project exploring asynchronous programming,
concurrent I/O, and scalable website monitoring.*

</div>

---

# 📖 Table of Contents

- [✨ Features](#-features)
- [💡 Why this exists](#-why-this-exists)
- [⚡ Performance Benchmark](#-performance-benchmark)
- [🏗️ Architecture](#️-architecture)
- [🗄️ Database Design](#️-database-design)
- [🚨 A Real Edge Case: Rate Limiting](#-a-real-edge-case-rate-limiting)
- [🧪 Testing](#-testing)
- [🚀 Installation](#-installation)
- [📁 Project Structure](#-project-structure)
- [⚠️ Known Limitations](#️-known-limitations)
- [🛣️ Roadmap](#️-roadmap)
- [🤝 Development Note](#-development-note)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

# ✨ Features

- 🌐 Monitor multiple websites simultaneously
- ⚡ Concurrent health checks using **asyncio** and **httpx**
- 📊 Uptime history tracking
- ⏱️ Response time monitoring
- 🚦 HTTP status monitoring
- 👤 User-specific monitoring dashboard
- 📈 Automatic uptime percentage calculation
- 🔄 Background monitoring worker
- 🧪 Automated test suite
- 📉 Performance benchmark comparing sequential vs concurrent execution

---

# 💡 Why this exists

If you run a website, API, or side project, you generally don't know it's
down until someone reports it or you manually check it yourself.

Commercial services such as **UptimeRobot**, **Pingdom**, and
**StatusCake** solve this problem.

PingRadar is a lightweight implementation of the same idea, built to
explore one engineering question:

> **How can many websites be monitored efficiently without the monitoring process itself becoming the bottleneck?**

Website monitoring is an **I/O-bound** problem.

Almost all execution time is spent waiting for remote servers to respond
rather than performing computations locally.

That makes asynchronous programming the ideal solution.

Instead of simply claiming that async is faster, PingRadar demonstrates
the difference through measurable benchmarks.

---

# ⚡ Performance Benchmark

`benchmark.py` checks the same **37 websites** using two different
approaches.

| 🚀 Strategy | ⏱️ Total Time |
|------------|--------------:|
| Sequential (`requests`) | 20.21 s |
| Concurrent (`asyncio.gather()`) | 2.12 s |
| **🏆 Speedup** | **≈ 9.5× Faster** |

Sequential monitoring waits for each request to finish before starting
the next.

Concurrent monitoring overlaps waiting time across all requests, making
the runtime approach the duration of the **slowest request**, rather than
the sum of every request.

Run the benchmark yourself:

```bash
python benchmark.py
```

---

# 🏗️ Architecture

```
                     ┌───────────────────────────────┐
                     │          Django App           │
                     │                               │
                     │ Authentication                │
                     │ Website Management            │
                     │ Dashboard                     │
                     │ Admin                         │
                     └──────────────┬────────────────┘
                                    │
                             Shared Database
                                    │
                     ┌──────────────▼────────────────┐
                     │        run_monitor            │
                     │                               │
                     │ asyncio Event Loop            │
                     │ httpx.AsyncClient             │
                     │ asyncio.gather()              │
                     │ Concurrent Health Checks      │
                     └──────────────┬────────────────┘
                                    │
                                    ▼
                           External Websites
```

The application runs as **two independent processes** sharing the same
database.

| 🖥️ Process | 💻 Command | 🎯 Responsibility |
|------------|-----------|------------------|
| Web Server | `python manage.py runserver` | Authentication, Dashboard, Website Management |
| Monitor Worker | `python manage.py run_monitor` | Continuous Monitoring & Recording Results |

Separating these responsibilities ensures that slow network requests
never block the responsiveness of the web application.

---

# 🗄️ Database Design

## 🌐 Website

Represents a monitored website.

Stores:

- Name
- URL
- Owner
- Creation Timestamp

Provides helper methods:

- `uptime_percentage()`
- `latest_check()`
- `response_time_history()`

These values are calculated dynamically instead of storing redundant
data.

---

## 📊 StatusCheck

Represents a **single monitoring event**.

Each row stores:

- Timestamp
- HTTP Status Code
- Response Time
- Success / Failure Status

Historical monitoring data is simply the accumulation of these rows.

---

# 🚨 A Real Edge Case: Rate Limiting

During testing, one monitored service (**TryHackMe**) started returning

```
429 Too Many Requests
```

Initially, every non-2xx response was treated as downtime.

This created **false outage reports** even though the website itself was
fully operational.

The monitoring logic was updated so HTTP **429** is treated as a special
case.

Instead of incorrectly marking the site as either **Up** or **Down**, the
check is skipped because neither result would accurately reflect the
website's state.

Future improvements include:

- 📨 Custom User-Agent
- 🔄 Exponential Backoff
- 📈 Adaptive Monitoring Intervals

---

# 🧪 Testing

Run tests using:

```bash
python manage.py test monitor
```

Current test coverage includes:

- ✅ Uptime percentage calculations
- ✅ Zero-history edge cases
- ✅ All-up scenarios
- ✅ All-down scenarios
- ✅ Mixed uptime calculations
- ✅ Ownership security
- ✅ Unauthorized access prevention
- ✅ Correct deletion behaviour

---

# 🚀 Installation

Clone the repository

```bash
git clone https://github.com/iamNaman-official/PingRadar.git
cd PingRadar
```

Create a virtual environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Apply migrations

```bash
python manage.py migrate
python manage.py createsuperuser
```

Run the project

Terminal 1

```bash
python manage.py runserver
```

Terminal 2

```bash
python manage.py run_monitor
```

---

# 📁 Project Structure

```
PingRadar/
│
├── monitor/
│   ├── management/
│   │   └── commands/
│   │       └── run_monitor.py
│   ├── models.py
│   ├── views.py
│   ├── tests.py
│   ├── urls.py
│   └── templates/
│
├── pingradar_project/
│   ├── settings.py
│   └── urls.py
│
├── benchmark.py
├── requirements.txt
├── manage.py
├── README.md
└── .env.example
```

---

# ⚠️ Known Limitations

These are intentional engineering decisions rather than oversights.

| Limitation | Reason | Production Solution |
|------------|--------|---------------------|
| Single monitoring worker | Multiple workers would duplicate monitoring | Celery + Redis |
| Refresh-based dashboard | Simpler architecture | Django Channels + Redis |
| SQLite | Suitable for development | PostgreSQL |

The project intentionally focuses on asynchronous monitoring instead of
introducing unnecessary infrastructure.

---

# 🛣️ Roadmap

- [ ] 📧 Email Notifications
- [ ] 💬 Discord Alerts
- [ ] 📱 Telegram Notifications
- [ ] 💼 Slack Integration
- [ ] 🐳 Docker Support
- [ ] 🐘 PostgreSQL Support
- [ ] 🔌 REST API
- [ ] ⚙️ Celery + Redis
- [ ] 📡 Live Dashboard (WebSockets)
- [ ] 🔍 Custom Health Checks
- [ ] 📊 Prometheus Metrics
- [ ] 📈 Grafana Dashboards

---

# 🤝 Development Note

PingRadar was built as a backend systems engineering project exploring
asynchronous I/O, concurrent network programming, and scalable monitoring
architecture with Django.

The **backend architecture, asynchronous monitoring engine, database
design, benchmarking, business logic, testing, debugging, and overall
system design** were designed, implemented, and are actively maintained
by the author.

The **frontend (HTML, CSS, and JavaScript)** was developed with AI
assistance to accelerate interface development.

Every AI-generated component was reviewed, modified, integrated, and
adapted to fit the overall architecture of the project.

AI was used as a development assistant rather than a replacement for
engineering decisions.

---

# 🤝 Contributing

Contributions are welcome.

```bash
git checkout -b feature/my-feature
git commit -m "Add my feature"
git push origin feature/my-feature
```

Then open a Pull Request.

---

# 📄 License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for details.

---

# 👨‍💻 Author

**Naman**

GitHub: **https://github.com/iamNaman-official**

---

<div align="center">

### ⭐ If you found PingRadar useful, consider giving it a star!

It helps others discover the project and motivates future development.

</div>