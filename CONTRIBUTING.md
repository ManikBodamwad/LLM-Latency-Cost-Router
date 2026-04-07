# Contributing to Agentic SRE Gateway

Thank you for your interest in contributing to the Agentic SRE Gateway! We are building the most resilient, cost-effective LLM routing layer for production AI systems.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally: `git clone https://github.com/your-username/LLM-Latency-Cost-Router.git`
3. **Set up the backend:** Install dependencies via `pip install -r requirements.txt`.
4. **Create a branch** for your feature or bug fix: `git checkout -b feature/your-feature-name`

## What to Contribute?

We welcome all contributions, including but not limited to:
- **New LLM Providers:** Adding fallback support for Anthropic, Cohere, or local Ollama instances.
- **Enhanced Telemetry:** Adding more Prometheus histograms for streaming time-to-first-token (TTFT).
- **UI/UX:** Improving the Vite SRE dashboard.
- **Documentation:** Fixing typos or adding deployment tutorials.

## Pull Request Process

1. **Test your code:** Ensure the FastAPI server boots successfully and Docker orchestration still works (`docker compose build`).
2. **Commit your changes:** Use clear, descriptive commit messages.
3. **Submit a PR:** Push your branch to GitHub and open a Pull Request against the `main` branch. 
4. **Code Review:** A maintainer will review your code. We may request small architectural changes to ensure SRE best practices are maintained.

## Code of Conduct

Please be respectful and collaborative in issues and pull requests. We operate strictly under standard open-source community guidelines.
