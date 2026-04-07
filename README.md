# Agentic API Gateway | SRE Edge Router

A production-grade, highly resilient API Gateway that dynamically routes Large Language Model (LLM) prompts based on complexity and minimizes cost through semantic caching. 

Built strictly with **Site Reliability Engineering (SRE)** principles, it implements automated failovers, Redis-backed rate limiters, token-cost telemetry routing to Prometheus, and features a glowing, immersive UI dashboard built beautifully in Vanilla JS/Vite.

## 🚀 Core SRE Features

- **Dynamic Tier Routing**: Uses a heuristics engine to parse prompt intent. Simple queries route to blazing-fast models (`groq/llama-3.1-8b`), while complex queries (e.g. system design) automatically route to heavy models (`groq/llama-3.1-70b`).
- **Zero-Latency Semantic Caching**: SHA-256 hashes intercepts inbound requests. Identical requests skip the LLM network entirely, serving an exact match directly from Redis memory in `< 0ms` for `$0USD` cost.
- **Intelligent Failover Resiliency**: Wraps primary model calls in strict `asyncio` timeouts. If a provider throws a quota limit, `503`, or hangs, the router gracefully degrades to alternative models before ever throwing an error to the user.
- **Vite SRE Telemetry Dashboard**: Complete visual interface built without bulky frameworks—utilizing raw CSS glassmorphism, flexbox scaling, and micro-animated charts showcasing true request latency and cost updates on every stream.
- **DDoS/Billing Defense**: Implements a Redis token-bucket API rate limiter (50 req/min) requiring an `x-api-key` header to prevent billing exhaustion.
- **Prometheus & Grafana Observability**: Instrumentated with custom Python metrics exposing End-to-End Latency Histograms, LLM Token Cost accumulations, and Routing Cache Hit/Miss rates to `/metrics`.

## 🛠️ Tech Stack & Architecture

- **Backend Route Logic**: `Python 3.11`, `FastAPI`, `LiteLLM` (for multi-provider standardization)
- **Frontend Dashboard**: Raw `HTML5`, Vanilla Base `CSS`, `Vite` Node-Server, `marked.js`
- **Cache & Memory**: `Redis` alpine container
- **Orchestration**: `Docker Compose`
- **Observability**: `Prometheus` (Scraping), `Grafana` (Visualization)
- **Inference Hardware**: `Groq LPU` (Llama 3.1 models config standard)

## ⚡ Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ManikBodamwad/LLM-Latency-Cost-Router.git
   cd "LLM Latency & Cost router"
   ```

2. **Supply your API Keys:**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY="gsk_your_groq_key_here"
   ```

3. **Deploy via Docker Compose:**
   ```bash
   docker compose up -d --build
   ```

4. **Experience the Application:**
   Open [http://localhost:5173](http://localhost:5173) in your web browser. Type a complex prompt like *"Can you explain the Medallion Architecture?"* and observe the SRE dashboard dynamically tracking the latency, the exact Token Cost, and the routing strategy in real-time.

## 📦 Usage as a Python Package

This repository is built as a portable Python package so engineering teams can inject edge-routing into their own systems natively without bulky Docker containers!

If you install this via pip:
```bash
pip install agentic-sre-gateway
```

You can instantly spin up the SRE-optimized Routing API on your local terminal using the globally injected command:
```bash
export GROQ_API_KEY="your_key"
export REDIS_URL="redis://localhost:6379/0"
agentic-gateway
```
This serves teams that want a drop-in API proxy to massively reduce LLM bills and monitor token consumption locally without rewriting complex LiteLLM and Prometheus wrappers themselves.

## 📊 View Local Development Telemetry

For local visualization during development, the `docker-compose` orchestration automatically spins up standard metrics scrape targets. 

- **Prometheus Scraper UI**: `http://localhost:9090`
- **Grafana Workspace**: `http://localhost:3000` 
  *(Note: This uses the default local-dev credentials Login: `admin` / Password: `admin`)*

---

*Developed by Manik Bodamwad to solve enterprise-level LLM deployment friction points: Cost Runaway, High Latency, and Provider Downtime.*
