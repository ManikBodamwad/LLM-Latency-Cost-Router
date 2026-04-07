from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import time
import asyncio
from prometheus_client import make_asgi_app, Counter, Histogram

app = FastAPI(title="LLM Router API")

# Metrics definitions
REQUEST_LATENCY = Histogram(
    'llm_request_latency_seconds',
    'Latency of LLM requests',
    ['model', 'tier']
)

TOKEN_COST = Counter(
    'llm_token_cost_total',
    'Estimated cost in USD',
    ['model', 'tier']
)

FAILOVER_COUNT = Counter(
    'llm_failover_count_total',
    'Number of failovers',
    ['original_model', 'fallback_model', 'reason']
)

import litellm

# Constants for pricing mock will be handled by litellm's completion_cost
class ChatRequest(BaseModel):
    prompt: str

def determine_complexity(prompt: str) -> str:
    complex_keywords = ["analyze", "code", "architecture", "summarize", "complex"]
    if len(prompt) > 1000:
        return "complex"
    if any(kw in prompt.lower() for kw in complex_keywords):
        return "complex"
    return "simple"

@app.post("/api/v1/chat/completions")
async def chat_completions(req: ChatRequest):
    tier = determine_complexity(req.prompt)
    
    if tier == "simple":
        target_model = "gemini/gemini-1.5-flash"
        fallback_model = "gemini/gemini-1.0-pro"
        timeout_seconds = 5.0
    else:
        target_model = "gemini/gemini-1.5-pro"
        fallback_model = "gemini/gemini-1.5-flash"  # Fallback to faster model if pro fails
        timeout_seconds = 10.0

    start_time = time.time()
    response = None
    used_model = target_model
    
    messages = [{"role": "user", "content": req.prompt}]

    try:
        # Attempt primary model
        response = await litellm.acompletion(
            model=target_model,
            messages=messages,
            timeout=timeout_seconds
        )
    except Exception as e:
        # Handle timeout or 503 or any exception by falling back
        error_type = "timeout" if isinstance(e, asyncio.TimeoutError) else "error_503"
        FAILOVER_COUNT.labels(original_model=target_model, fallback_model=fallback_model, reason=error_type).inc()
        used_model = fallback_model
        
        # Call fallback
        response = await litellm.acompletion(
            model=fallback_model,
            messages=messages,
            timeout=timeout_seconds
        )
    
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(model=used_model, tier=tier).observe(latency)
    
    cost = litellm.completion_cost(response) or 0.0
    TOKEN_COST.labels(model=used_model, tier=tier).inc(cost)
    
    # Extract string from response format
    content_str = response.choices[0].message.content
    
    return {
        "tier": tier, 
        "latency": round(latency, 3), 
        "used_model": used_model,
        "response": content_str,
        "cost_usd": cost
    }

# Mount prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
