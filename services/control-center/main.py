"""
Control Center API - WebSocket server for interactive incident simulation
"""
import os
import json
import logging
import asyncio
from typing import Set
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from actions.action_handlers import handle_error_trigger, handle_normal_action
from state.system_state import system_state
from datadog.simulator import process_product_action

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Control Center API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# Request models
class ActionRequest(BaseModel):
    action: str
    error_type: str = None
    intensity: int = None

# Background task to send periodic state updates
async def send_periodic_updates():
    """Send periodic state updates to all connected clients."""
    while True:
        try:
            await asyncio.sleep(2)  # Update every 2 seconds
            if manager.active_connections:
                state = system_state.get_state()
                await manager.broadcast({
                    "type": "state_update",
                    "data": state
                })
        except Exception as e:
            logger.error(f"Error in periodic updates: {e}")

# Start background task
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_periodic_updates())
    logger.info("Control Center API started")

@app.get("/healthz")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "control-center",
        "connections": len(manager.active_connections)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication."""
    await manager.connect(websocket)
    
    try:
        # Send initial state
        initial_state = system_state.get_state()
        await websocket.send_json({
            "type": "state_update",
            "data": initial_state
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")
                error_type = message.get("error_type")
                intensity = message.get("intensity")
                
                logger.info(f"Received action: {action}, error_type: {error_type}, full message: {message}")
                
                # Handle action
                if action == "trigger_error":
                    if not error_type:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "error_type required"}
                        })
                        continue
                    
                    result = await handle_error_trigger(error_type, intensity)
                    
                    if result.get("success"):
                        # Broadcast full state update (includes new log and incident)
                        state = system_state.get_state()
                        await manager.broadcast({
                            "type": "state_update",
                            "data": state
                        })
                        # Also broadcast incident created for specific handling
                        await manager.broadcast({
                            "type": "incident_created",
                            "data": result.get("incident")
                        })
                    else:
                        await websocket.send_json({
                            "type": "error",
                            "data": result
                        })
                
                elif action == "normal_action":
                    result = await handle_normal_action(error_type or "default")
                    # State is already updated by handle_normal_action, just broadcast state
                    state = system_state.get_state()
                    await manager.broadcast({
                        "type": "state_update",
                        "data": state
                    })
                
                elif action == "product_action":
                    # Handle product interaction (Google.com-like)
                    try:
                        action_data_str = error_type or "{}"
                        action_data = json.loads(action_data_str) if isinstance(action_data_str, str) else action_data_str
                        product_action = action_data.get("action")
                        
                        logger.info(f"Processing product action: {product_action}")
                        
                        # Process action and generate Datadog data
                        datadog_data = process_product_action(product_action, action_data)
                        
                        # If it's an error trigger, handle it properly
                        if product_action == "trigger_error":
                            error_type_name = action_data.get("type", "high_error_rate")
                            result = await handle_error_trigger(error_type_name)
                            if result.get("success"):
                                state = system_state.get_state()
                                await manager.broadcast({
                                    "type": "state_update",
                                    "data": state
                                })
                        else:
                            # Add Datadog data to system state
                            for item in datadog_data:
                                if "message" in item:  # It's a log
                                    system_state.add_log(
                                        item.get("status", "info").upper(),
                                        item["message"]
                                    )
                            
                            # Broadcast state update
                            state = system_state.get_state()
                            await manager.broadcast({
                                "type": "state_update",
                                "data": state
                            })
                        
                        # Also send Datadog data
                        await manager.broadcast({
                            "type": "datadog_data",
                            "data": datadog_data
                        })
                    except Exception as e:
                        logger.error(f"Error processing product action: {e}", exc_info=True)
                        import traceback
                        logger.error(traceback.format_exc())
                
                elif action == "get_state":
                    state = system_state.get_state()
                    await websocket.send_json({
                        "type": "state_update",
                        "data": state
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"}
                })
            except Exception as e:
                logger.error(f"Error handling message: {e}", exc_info=True)
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": str(e)}
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("CONTROL_CENTER_PORT", "8007"))
    uvicorn.run(app, host="0.0.0.0", port=port)

