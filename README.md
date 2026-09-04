# Automated Job Researcher & Alert System

An automated job discovery and alert system that collects job listings, processes and stores the data, generates semantic embeddings, and makes the results available through a web interface, REST API, and Telegram bot.

## 🚀 Live

- 🌐 Website: https://vjoe1.github.io/automated-job-researcher-alert-system/
- 📡 API Docs: https://automated-job-researcher-alert-system.fastapicloud.dev/docs
- 🤖 Telegram Bot: https://t.me/thejob_helperbot

## ✨ Features

- 🔎 Automated job discovery
- 🧹 Data cleaning and normalization
- 🤖 Find similar jobs using AI
- 💰 Salary-based job matching
- 🌍 Remote-work filtering
- 📡 REST API built with FastAPI
- 📱 Full Telegram UI with job search, filtering, and notifications
- 🌐 Interactive web interface for job discovery and search
- ⚙️ Fully automated daily job pipeline
- 🗄️ PostgreSQL database

## 🏗️ Architecture

```text
GitHub Actions
      │
      ▼
   Scraper
      │
      ▼
   PostgreSQL
   (Supabase)
      │
      ▼
   Cleaner
      │
      ▼
  Embeddings
      │
      ▼
   FastAPI
    ┌─┴─┐
    ▼   ▼
Website Telegram Bot
```

## 🧠 Semantic Search

The system uses `multi-qa-MiniLM-L6-cos-v1` to generate embeddings for job data and user queries.

Search results are ranked using semantic similarity, with additional scoring based on salary and remote-work preferences.

## 🛠️ Tech Stack

**Language:** Python

**Backend:** FastAPI, SQLAlchemy

**Data:** Pandas, PostgreSQL, Supabase

**Scraping:** SeleniumBase, Playwright

**AI:** Sentence Transformers, Hugging Face Inference API

**Automation:** GitHub Actions

**Bot:** python-telegram-bot

**Frontend:** HTML, CSS, JavaScript

## 📁 Project Structure

```text
├── backend/
│   ├── api/
│   │   ├── jobs.py
│   │   ├── bot.py
│   │   └── users.py
│   ├── core/
│   │   ├── constants.py
│   │   └── security.py
│   ├── database/
│   │   └── database.py
│   ├── models/
│   │   └── models.py
│   ├── schemas/
│   │   └── schemas.py
│   ├── __init__.py
│   └── main.py
│
├── bot/
│   ├── handlers/
│   │   ├── menu.py
│   │   ├── notifier.py
│   │   ├── text.py
│   │   ├── start.py
│   │   └── __init__.py
│   ├── config.py
│   ├── keyboards.py
│   ├── services.py
│   └── main.py
│
├── cleaner/
│   ├── data_cleaning.py
│   ├── build_embeddings.py
│   ├── constants.py
│   └── main.py
│
├── scraper/
│   ├── scraper.py
│   ├── constants.py
│   ├── parser.py
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── js/
│   │     ├── components/
│   │     │   ├── charts.js
│   │     │   └── ui.js
│   │     ├── api.js
│   │     ├── config.js
│   │     ├── state.js
│   │     └── main.js
│   └── css/
│       └── styles.css
│
├── .github/
│   └── workflows/
│       ├── scraper.yml
│       └── static.yml
│
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md```

## ⚙️ Local Setup

Clone the repository:

```bash
git clone https://github.com/vjoe1/automated-job-researcher-alert-system.git
cd automated-job-researcher-alert-system
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root and add the required environment variables.

Run the components you need locally, such as the FastAPI server or Telegram bot.

## 🔄 Automation

The system automatically runs the job pipeline on a daily schedule:

```text
Scrape → Clean → Generate Embeddings → Store
```

The processed data is then consumed by the FastAPI backend, website, and Telegram bot.

## 📌 About

This project is a complete end-to-end job research and alert system, combining automated job discovery, data processing, AI-powered similarity search, backend APIs, and user-facing interfaces.