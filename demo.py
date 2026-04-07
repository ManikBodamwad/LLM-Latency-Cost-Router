import asyncio
import httpx
import time
from rich.console import Console
from rich.panel import Panel

console = Console()
API_URL = "http://localhost:8000/api/v1/chat/completions"
HEADERS = {"x-api-key": "demo_super_secret_key"}

async def test_endpoint():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Complex Prompt (Should route to Pro and take longer)
        console.print("[bold cyan]\n--- TEST 1: Complex Request (Cache Miss expected) ---[/bold cyan]")
        start = time.time()
        payload = {"prompt": "Write a complex architecture design for a distributed system.", "stream": False}
        resp = await client.post(API_URL, json=payload, headers=HEADERS)
        latency = time.time() - start
        
        if resp.status_code == 200:
            data = resp.json()
            console.print(Panel(f"🎯 Tier: {data['tier']}\n⏱ Latency: {data['latency']}s\n💸 Cost: ${data['cost_usd']}\n\n{data['response'][:100]}...", title="Gateway Response"))
        else:
            console.print(f"[red]Failed: {resp.text}[/red]")

        # Test 2: Identical Prompt (Should hit Redis Cache)
        console.print("[bold yellow]\n--- TEST 2: Identical Request (Cache Hit expected) ---[/bold yellow]")
        start = time.time()
        resp2 = await client.post(API_URL, json=payload, headers=HEADERS)
        latency2 = time.time() - start
        
        if resp2.status_code == 200:
            data2 = resp2.json()
            console.print(Panel(f"🎯 Tier: {data2['tier']} (Cached)\n⏱ Latency: {data2['latency']}s\n💸 Cost: ${data2['cost_usd']}\n\n{data2['response'][:100]}...", title="Gateway Response"))
            if data2['latency'] < latency:
                console.print(f"[green]✅ CACHE HIT SUCCESS! Sped up by {round(latency - data2['latency'], 2)}s with zero cost.[/green]")

        # Test 3: Simple Request Streaming
        console.print("[bold magenta]\n--- TEST 3: Streaming a Simple Request ---[/bold magenta]")
        payload3 = {"prompt": "Hi, tell me a short joke.", "stream": True}
        console.print("[dim]Streaming response chunks:[/dim] ", end="")
        async with client.stream("POST", API_URL, json=payload3, headers=HEADERS) as stream_resp:
            if stream_resp.status_code == 200:
                async for chunk in stream_resp.aiter_bytes():
                    console.print(chunk.decode("utf-8"), end="", style="bold white")
            else:
                console.print(f"[red]Stream Failed: {await stream_resp.aread()}[/red]")
        print("\n")

        # Test 4: Rate Limit
        console.print("[bold red]\n--- TEST 4: Triggering the Rate Limiter (Spamming requests) ---[/bold red]")
        tasks = []
        for _ in range(55):
            tasks.append(client.post(API_URL, json={"prompt": "spam"}, headers=HEADERS))
        
        # We fire 55 requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        blocked_count = sum(1 for r in results if not isinstance(r, Exception) and r.status_code == 429)
        console.print(f"[red]🛑 Successfully blocked {blocked_count} requests via HTTP 429 Rate Limiter.[/red]")


if __name__ == "__main__":
    console.print("[bold green]Starting LLM Router Emulation Client...[/bold green]")
    try:
        asyncio.run(test_endpoint())
    except Exception as e:
        console.print(f"[bold red]Cannot connect to router: {e}[/bold red]")
        console.print("\n[yellow]Did you start the Docker container with `docker compose up -d`?[/yellow]")
