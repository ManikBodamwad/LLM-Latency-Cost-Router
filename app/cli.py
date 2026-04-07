import uvicorn
import os

def start_gateway():
    """
    Entrypoint for the CLI. Starts the Agentic SRE Gateway via Uvicorn.
    """
    print("🚀 Starting Agentic SRE Gateway on http://0.0.0.0:8000")
    print("Make sure you have Redis running and GROQ_API_KEY in your environment.")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    start_gateway()
