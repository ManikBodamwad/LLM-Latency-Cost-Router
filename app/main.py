from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import time
import asyncio
import os
import hashlib
import redis.asyncio as redis
from prometheus_client import make_asgi_app, Counter, Histogram
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LLM Router API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis client
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

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

CACHE_HITS = Counter('llm_cache_hits_total', 'Number of cache hits')
CACHE_MISSES = Counter('llm_cache_misses_total', 'Number of cache misses')

import litellm

# Constants for pricing mock will be handled by litellm's completion_cost
class ChatRequest(BaseModel):
    prompt: str
    stream: bool = False

async def verify_api_key(x_api_key: str = Header(...)):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key required")
    # Fixed window rate limiter (50 req / minute)
    key = f"rate_limit:{x_api_key}"
    requests = await redis_client.incr(key)
    if requests == 1:
        await redis_client.expire(key, 60)
    if requests > 50:
        raise HTTPException(status_code=429, detail="Rate limit exceeded: 50 requests per minute")
    return x_api_key

def determine_complexity(prompt: str) -> str:
    complex_keywords = ["analyze", "code", "architecture", "summarize", "complex"]
    if len(prompt) > 1000:
        return "complex"
    if any(kw in prompt.lower() for kw in complex_keywords):
        return "complex"
    return "simple"

@app.post("/api/v1/chat/completions")
async def chat_completions(req: ChatRequest, api_key: str = Depends(verify_api_key)):
    tier = determine_complexity(req.prompt)
    
    if tier == "simple":
        target_model = "groq/llama-3.1-8b-instant"
        fallback_model = "groq/llama-3.1-8b-instant"
        timeout_seconds = 5.0
    else:
        target_model = "groq/llama-3.1-70b-versatile"
        fallback_model = "groq/llama-3.1-8b-instant"  
        timeout_seconds = 10.0

    start_time = time.time()
    response = None
    used_model = target_model
    
    messages = [{"role": "user", "content": req.prompt}]

    # Check cache first
    prompt_hash = hashlib.sha256(req.prompt.encode()).hexdigest()
    cached_response = await redis_client.get(prompt_hash)
    
    if cached_response:
        CACHE_HITS.inc()
        latency = time.time() - start_time
        REQUEST_LATENCY.labels(model="cache", tier=tier).observe(latency)
        
        if req.stream:
            async def cache_streamer():
                yield cached_response
            return StreamingResponse(cache_streamer(), media_type="text/event-stream")
            
        return {
            "tier": tier,
            "latency": round(latency, 3),
            "used_model": "cache",
            "response": cached_response,
            "cost_usd": 0.0
        }
        
    CACHE_MISSES.inc()

    if req.stream:
        try:
            response_stream = await litellm.acompletion(model=target_model, messages=messages, timeout=timeout_seconds, stream=True)
        except Exception as e:
            error_type = "timeout" if isinstance(e, asyncio.TimeoutError) else "error_503"
            FAILOVER_COUNT.labels(original_model=target_model, fallback_model=fallback_model, reason=error_type).inc()
            used_model = fallback_model
            
            try:
                response_stream = await litellm.acompletion(model=fallback_model, messages=messages, timeout=timeout_seconds, stream=True)
            except Exception as e2:
                raise HTTPException(status_code=503, detail=f"Core and Fallback LLM failed: {str(e2)}")

        async def stream_generator():
            full_text = ""
            async for chunk in response_stream:
                content = chunk.choices[0].delta.content or ""
                full_text += content
                yield content
                
            latency = time.time() - start_time
            REQUEST_LATENCY.labels(model=used_model, tier=tier).observe(latency)
            
            try:
                await redis_client.setex(prompt_hash, 3600, full_text)
            except Exception:
                pass
                
        return StreamingResponse(stream_generator(), media_type="text/event-stream")

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
        
        try:
            # Call fallback
            response = await litellm.acompletion(
                model=fallback_model,
                messages=messages,
                timeout=timeout_seconds
            )
        except Exception as e2:
            raise HTTPException(status_code=503, detail=f"LLM Quota Exceeded or fully down: {str(e2)}")
    
    latency = time.time() - start_time
    REQUEST_LATENCY.labels(model=used_model, tier=tier).observe(latency)
    
    try:
        cost = litellm.completion_cost(completion_response=response, model=used_model) or 0.0
    except Exception:
        cost = 0.0
        
    TOKEN_COST.labels(model=used_model, tier=tier).inc(cost)
    
    # Extract string from response format
    content_str = response.choices[0].message.content
    
    # Store in cache for 1 hour (3600 seconds)
    try:
        await redis_client.setex(prompt_hash, 3600, content_str)
    except Exception as e:
        pass # Ignore cache write errors

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
