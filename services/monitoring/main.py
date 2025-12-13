"""
Monitoring Service - Simulates monitoring/observability systems
"""
from fastapi import FastAPI
import os
import asyncio
from datetime import datetime

app = FastAPI(title="Monitoring Service", version="0.1.0")

monitoring_active = False


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "monitoring", "monitoring_active": monitoring_active}


@app.post("/monitoring/start")
async def start_monitoring():
    """Start monitoring loop"""
    global monitoring_active
    monitoring_active = True
    return {"status": "started"}


@app.post("/monitoring/stop")
async def stop_monitoring():
    """Stop monitoring loop"""
    global monitoring_active
    monitoring_active = False
    return {"status": "stopped"}


@app.get("/monitoring/status")
async def get_monitoring_status():
    """Get monitoring status"""
    return {"monitoring_active": monitoring_active}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MONITORING_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

