# LLM Latency & Cost Router

An intelligent API Gateway written in Python (FastAPI) that dynamically routes Large Language Model (LLM) prompts based on complexity and cost. 

Built with Site Reliability Engineering (SRE) principles, it automatically provides failovers for API timeouts or downtime, and captures vital usage metrics for Prometheus and Grafana.

## Features

- **Dynamic Routing**: Analyzes prompt length and keywords to route requests. Simple prompts hit fast/cheap models (gemini-1.5-flash), while complex logic routes to capable models (gemini-1.5-pro).
- **Zero-Latency Semantic Caching**: Powered by Redis, identical prompts skip the LLM entirely, resulting in <5ms latency and $0.00 cost.
- **Intelligent Failovers**: Wraps primary model calls with strict `asyncio` timeouts. If the primary provider returns an HTTP 503 or hangs, it instantly falls back to a secondary model.
- **High-Performance Streaming (SSE)**: Supports chunk-by-chunk generator streaming for real-time AI UI rendering, with simultaneous cache write-behind.
- **API Key Rate Limiting**: Fixed-window token bucket implementation limits users to 50 requests/min via `x-api-key` headers protecting billing loops.
- **Cost & Latency Tracking**: Integrated `prometheus_client` records total token cost (USD), latency (Histogram), and failure counts, all exposed via `/metrics`.
- **Docker Ready**: Complete orchestrator setup for the API, Prometheus data-scraper, and Grafana dashboard out-of-the-box.

## Tech Stack

- **Python 3.11** / **FastAPI**
- **LiteLLM**: For standardized LLM API integrations and exact cost tracking.
- **Redis**: For semantic caching and atomic rate-limiting token buckets.
- **Docker Compose**: For container orchestration.
- **Prometheus & Grafana**: For deep observability and SRE metrics.

## Quickstart

1. Clone the repository.
2. Create a `.env` file and add your target API key (default configured for Gemini):
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```
3. Run the orchestration:
   ```bash
   docker compose up -d --build
   ```

### Endpoints
- **POST `/api/v1/chat/completions`**: Main entrypoint for prompts. 
  - **Headers**: Requires `x-api-key`. 
  - **Body**: Expects `{"prompt": "Hello world", "stream": false}`
- **GET `/metrics`**: Prometheus scraping endpoint.

## Observability

To view the dashboard metrics:
- **Prometheus Native UI**: `http://localhost:9090`
- **Grafana Visualization**: `http://localhost:3000` (Login: `admin` / `admin`)
