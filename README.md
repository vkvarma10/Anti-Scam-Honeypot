---
title: Anti-Scam Honeypot
emoji: 🛡️
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
---

# 🛡️ Anti-Scam Agentic Honeypot

An intelligent, evaluation-ready Honeypot System designed to trap scammers, extract critical intelligence (UPI IDs, bank accounts, emails, phone numbers, phishing links), calculate threat-levels, and output a strict JSON contract for cyber-crime reporting.

## 🚀 Quick Start (Local Run)

1. **Activate the Virtual Environment**:
   ```bash
   .\.venv\Scripts\Activate.ps1
   ```
2. **Start the API & Dashboard**:
   ```bash
   python -m uvicorn app.main:app --reload
   ```
3. Open your browser and go to:
   **http://localhost:8000**

## 🌐 Deploy to Hugging Face Spaces (Docker)

This repository is stripped of all bloat and runs flawlessly natively as a Docker space on Hugging Face.

1. Go to Hugging Face -> **Create New Space**.
2. Set Space SDK to **Docker** (Blank).
3. Connect your GitHub repository (or directly upload these files).
4. Go to Space Settings -> **Variables and Secrets**.
5. Add a New Secret:
   - Name: `GEMINI_API_KEY`
   - Value: `your-api-key-here`
6. Click **Rebuild Space**. It will automatically use the provided `Dockerfile` to launch the API and host the dashboard on port `7860`.

## 📁 Project Structure

* `app/` - The backend engine (FastAPI + Regex Pipeline + Gemini AI tracking)
* `static/` - The frontend dashboard (HTML, CSS, JS)
* `Dockerfile` - Hugging Face deployment blueprint
* `requirements.txt` - Core dependencies
* `honeypot.db` - SQLite memory tracking database

## ✨ Features

* **Sub-30s Inference**: Hard fallback logic using Regex deduplication guarantees zero hanging sessions.
* **Aggressive Extraction**: Parses text explicitly for emails, UPIs, and bank domains before AI confirmation.
* **100% Schema Validation**: Compiles all findings down to a `status`, `scamDetected`, `extractedIntelligence`, `engagementMetrics`, and `agentNotes` JSON exactly as required by the hackathon testing frameworks.
