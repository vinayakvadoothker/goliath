"""
Monitoring Service - Simulates monitoring/observability systems
Continuously logs and creates incidents when errors are detected
"""
import os
import asyncio
import random
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
monitoring_task: Optional[asyncio.Task] = None
monitoring_active = False
monitoring_stats = {
    "error_count": 0,
    "last_error_at": None,
    "started_at": None,
    "service_name": None,
    "error_probability": None,
    "log_interval": None
}

# Configuration
INGEST_URL = os.getenv("MONITORING_INGEST_URL", "http://ingest:8000")
SERVICE_NAME = os.getenv("MONITORING_SERVICE_NAME", "api-service")
ERROR_PROBABILITY = float(os.getenv("MONITORING_ERROR_PROBABILITY", "0.05"))
LOG_INTERVAL = int(os.getenv("MONITORING_LOG_INTERVAL", "5"))
AUTO_START = os.getenv("MONITORING_AUTO_START", "true").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2")

# Initialize OpenAI client if API key is provided
openai_client = None
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    logger.warning("OPENAI_API_KEY not provided. LLM preprocessing will be disabled.")

# Error type templates - more dynamic and configurable
ERROR_TYPE_TEMPLATES = [
    {
        "templates": [
            "High error rate detected: {rate} errors/sec on {endpoint}",
            "Error rate spike: {rate} errors/sec on {endpoint} endpoint",
            "Surge in errors: {rate} errors/sec detected on {endpoint}",
            "Critical error rate: {rate} errors/sec on {endpoint}"
        ],
        "severity": "sev1",
        "rate_range": (100, 1000),
        "endpoint_pool": ["/api/v1/users", "/api/v1/orders", "/api/v1/payments", "/api/v1/auth", 
                         "/api/v1/products", "/api/v1/cart", "/api/v1/checkout", "/api/v2/analytics"]
    },
    {
        "templates": [
            "Database connection timeout: {db_name} connection pool exhausted",
            "{db_name} database connection pool at capacity",
            "Database {db_name} connection timeout after {timeout}ms",
            "{db_name} connection pool exhausted: {pool_size} connections in use"
        ],
        "severity": "sev2",
        "db_pool": ["postgres", "mysql", "redis", "mongodb", "cassandra", "elasticsearch"],
        "timeout_range": (5000, 30000),
        "pool_size_range": (50, 200)
    },
    {
        "templates": [
            "Memory leak detected: {service} memory usage at {usage}%",
            "{service} memory usage critical: {usage}%",
            "Memory exhaustion: {service} at {usage}% capacity",
            "Out of memory: {service} memory usage {usage}%"
        ],
        "severity": "sev1",
        "usage_range": (85, 99)
    },
    {
        "templates": [
            "API endpoint returning 500: {endpoint} failing with {error_count} errors in last 5 minutes",
            "Endpoint {endpoint} returning 500 errors: {error_count} failures in last 5 minutes",
            "HTTP 500 errors on {endpoint}: {error_count} errors detected",
            "Server error on {endpoint}: {error_count} 500 responses"
        ],
        "severity": "sev2",
        "endpoint_pool": ["/api/v1/users", "/api/v1/orders", "/api/v1/payments", "/api/v1/inventory"],
        "error_count_range": (50, 500)
    },
    {
        "templates": [
            "Service degradation: {service} response time increased to {response_time}ms (p95)",
            "{service} latency spike: p95 response time at {response_time}ms",
            "Performance degradation: {service} p95 latency {response_time}ms",
            "{service} response time elevated: p95 at {response_time}ms"
        ],
        "severity": "sev2",
        "response_time_range": (500, 2000)
    },
    {
        "templates": [
            "Cache miss rate spike: {cache_name} miss rate at {miss_rate}%",
            "{cache_name} cache performance degraded: {miss_rate}% miss rate",
            "Cache efficiency drop: {cache_name} {miss_rate}% miss rate",
            "{cache_name} cache miss rate elevated: {miss_rate}%"
        ],
        "severity": "sev3",
        "cache_pool": ["redis", "memcached", "local-cache", "distributed-cache", "CDN-cache"],
        "miss_rate_range": (30, 80)
    },
    {
        "templates": [
            "Response time degradation: {endpoint} p99 latency at {latency}ms",
            "Latency spike on {endpoint}: p99 at {latency}ms",
            "{endpoint} p99 latency elevated: {latency}ms",
            "Slow response on {endpoint}: p99 latency {latency}ms"
        ],
        "severity": "sev3",
        "endpoint_pool": ["/api/v1/users", "/api/v1/orders", "/api/v1/payments", "/api/v1/search"],
        "latency_range": (1000, 5000)
    },
    {
        "templates": [
            "Disk I/O saturation: {disk_name} I/O wait at {io_wait}%",
            "Disk {disk_name} I/O bottleneck: {io_wait}% wait time",
            "I/O saturation on {disk_name}: {io_wait}% wait",
            "{disk_name} disk I/O at capacity: {io_wait}% wait time"
        ],
        "severity": "sev2",
        "disk_pool": ["/dev/sda1", "/dev/sdb1", "/var/log", "/tmp", "/data", "/var/lib"],
        "io_wait_range": (50, 95)
    },
    {
        "templates": [
            "CPU throttling detected: {service} CPU usage at {cpu_usage}%",
            "{service} CPU usage critical: {cpu_usage}%",
            "CPU saturation: {service} at {cpu_usage}%",
            "High CPU load: {service} CPU usage {cpu_usage}%"
        ],
        "severity": "sev2",
        "cpu_usage_range": (85, 99)
    },
    {
        "templates": [
            "Network packet loss: {interface} packet loss at {loss_rate}%",
            "Network interface {interface} packet loss: {loss_rate}%",
            "Packet loss on {interface}: {loss_rate}%",
            "{interface} network interface experiencing {loss_rate}% packet loss"
        ],
        "severity": "sev2",
        "interface_pool": ["eth0", "eth1", "ens3", "enp0s3", "wlan0", "docker0"],
        "loss_rate_range": (5, 20)
    },
    {
        "templates": [
            "Queue backlog: {queue_name} queue depth at {depth} messages",
            "Message queue {queue_name} backlog: {depth} messages",
            "Queue {queue_name} depth critical: {depth} messages",
            "{queue_name} queue saturation: {depth} messages pending"
        ],
        "severity": "sev2",
        "queue_pool": ["task-queue", "event-queue", "notification-queue", "processing-queue"],
        "depth_range": (1000, 10000)
    },
    {
        "templates": [
            "SSL certificate expiring: {domain} certificate expires in {days} days",
            "Certificate expiration warning: {domain} expires in {days} days",
            "{domain} SSL certificate expiring in {days} days",
            "Certificate renewal needed: {domain} expires in {days} days"
        ],
        "severity": "sev3",
        "domain_pool": ["api.example.com", "www.example.com", "auth.example.com", "cdn.example.com"],
        "days_range": (1, 30)
    }
]

# Normal log message templates - more varied
NORMAL_LOG_TEMPLATES = [
    "Processing {count} requests/sec",
    "Handling {count} concurrent connections",
    "Cache hit rate: {rate}%",
    "Database query latency: {latency}ms (p50)",
    "API endpoint {endpoint} serving {count} requests/min",
    "Background job processed {count} items",
    "Health check passed: all services operational",
    "Metrics collection completed: {count} metrics collected",
    "Log aggregation: {count} logs processed",
    "User authentication: {count} successful logins in last minute",
    "Session management: {count} active sessions",
    "Rate limiting: {count} requests throttled",
    "Cache warming: {count} entries preloaded",
    "Database connection pool: {count} active connections",
    "Message queue: {count} messages processed",
    "File upload: {count} files uploaded",
    "API rate: {count} requests per second",
    "Background workers: {count} jobs completed",
    "Database replication lag: {lag}ms",
    "CDN cache hit rate: {rate}%"
]


async def llm_preprocess_log(raw_log: str, service_name: str) -> str:
    """
    Use LLM to clean and normalize log text before processing.
    Returns cleaned description ready for entity extraction.
    """
    if not openai_client:
        # Fallback: basic cleaning without LLM
        cleaned = raw_log.strip()
        # Remove common log prefixes
        for prefix in ["[ERROR]", "[CRITICAL]", "ERROR:", "CRITICAL:"]:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()
        return cleaned
    
    try:
        prompt = f"""Clean and normalize this error log. Return ONLY the cleaned description, no other text.

Raw log: {raw_log}
Service: {service_name}

Rules:
- Remove noise (timestamps, log levels, file paths if not relevant)
- Normalize terminology (consistent error type names)
- Fix typos if obvious
- Extract key information (error type, affected component, severity indicators)
- Keep it concise but informative
- Return clean, structured description ready for entity extraction

Cleaned description:"""
        
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # Deterministic
            timeout=10.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM preprocessing failed: {e}. Using raw log.")
        return raw_log.strip()


def generate_error_message(error_type_config: Dict[str, Any], service_name: str) -> tuple[str, str]:
    """
    Generate a realistic error message with dynamic values.
    Returns: (error_message, severity)
    """
    # Pick random template from available templates
    template = random.choice(error_type_config["templates"])
    severity = error_type_config["severity"]
    
    # Fill in dynamic values based on error type configuration
    if "endpoint_pool" in error_type_config:
        endpoint = random.choice(error_type_config["endpoint_pool"])
        if "rate_range" in error_type_config:
            rate = random.randint(*error_type_config["rate_range"])
            return template.format(rate=rate, endpoint=endpoint), severity
        elif "error_count_range" in error_type_config:
            error_count = random.randint(*error_type_config["error_count_range"])
            return template.format(endpoint=endpoint, error_count=error_count), severity
        elif "latency_range" in error_type_config:
            latency = random.randint(*error_type_config["latency_range"])
            return template.format(endpoint=endpoint, latency=latency), severity
    
    if "db_pool" in error_type_config:
        db_name = random.choice(error_type_config["db_pool"])
        if "timeout_range" in error_type_config:
            timeout = random.randint(*error_type_config["timeout_range"])
            return template.format(db_name=db_name, timeout=timeout), severity
        elif "pool_size_range" in error_type_config:
            pool_size = random.randint(*error_type_config["pool_size_range"])
            return template.format(db_name=db_name, pool_size=pool_size), severity
        else:
            return template.format(db_name=db_name), severity
    
    if "usage_range" in error_type_config:
        usage = random.randint(*error_type_config["usage_range"])
        return template.format(service=service_name, usage=usage), severity
    
    if "response_time_range" in error_type_config:
        response_time = random.randint(*error_type_config["response_time_range"])
        return template.format(service=service_name, response_time=response_time), severity
    
    if "cache_pool" in error_type_config:
        cache_name = random.choice(error_type_config["cache_pool"])
        miss_rate = random.randint(*error_type_config["miss_rate_range"])
        return template.format(cache_name=cache_name, miss_rate=miss_rate), severity
    
    if "disk_pool" in error_type_config:
        disk_name = random.choice(error_type_config["disk_pool"])
        io_wait = random.randint(*error_type_config["io_wait_range"])
        return template.format(disk_name=disk_name, io_wait=io_wait), severity
    
    if "cpu_usage_range" in error_type_config:
        cpu_usage = random.randint(*error_type_config["cpu_usage_range"])
        return template.format(service=service_name, cpu_usage=cpu_usage), severity
    
    if "interface_pool" in error_type_config:
        interface = random.choice(error_type_config["interface_pool"])
        loss_rate = random.randint(*error_type_config["loss_rate_range"])
        return template.format(interface=interface, loss_rate=loss_rate), severity
    
    if "queue_pool" in error_type_config:
        queue_name = random.choice(error_type_config["queue_pool"])
        depth = random.randint(*error_type_config["depth_range"])
        return template.format(queue_name=queue_name, depth=depth), severity
    
    if "domain_pool" in error_type_config:
        domain = random.choice(error_type_config["domain_pool"])
        days = random.randint(*error_type_config["days_range"])
        return template.format(domain=domain, days=days), severity
    
    # Fallback: just format with service name
    return template.format(service=service_name), severity


def generate_normal_log_message(service_name: str) -> str:
    """Generate a normal log message with random values."""
    template = random.choice(NORMAL_LOG_TEMPLATES)
    
    # Fill in dynamic values with varied ranges
    if "{count}" in template:
        # Different count ranges based on context
        if "requests" in template.lower() or "connections" in template.lower():
            count = random.randint(10, 2000)
        elif "messages" in template.lower() or "jobs" in template.lower():
            count = random.randint(1, 500)
        elif "sessions" in template.lower() or "files" in template.lower():
            count = random.randint(1, 100)
        else:
            count = random.randint(10, 1000)
        template = template.replace("{count}", str(count))
    
    if "{rate}" in template:
        # Vary cache hit rates and similar metrics
        rate = random.randint(75, 99)
        template = template.replace("{rate}", str(rate))
    
    if "{latency}" in template or "{lag}" in template:
        # Database and query latencies
        latency = random.randint(5, 150)
        template = template.replace("{latency}", str(latency)).replace("{lag}", str(latency))
    
    if "{endpoint}" in template:
        # More varied endpoints
        endpoints = [
            "/api/v1/users", "/api/v1/orders", "/api/v1/payments", "/api/v1/products",
            "/api/v1/cart", "/api/v1/checkout", "/api/v1/inventory", "/api/v1/search",
            "/api/v2/analytics", "/api/v2/reports", "/api/v1/auth", "/api/v1/profile"
        ]
        endpoint = random.choice(endpoints)
        template = template.replace("{endpoint}", endpoint)
    
    return template


async def create_work_item_via_ingest(
    service: str,
    severity: str,
    description: str,
    raw_log: str
) -> Optional[Dict[str, Any]]:
    """Create a work item by calling the Ingest service."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "service": service,
                "severity": severity,
                "description": description,
                "type": "incident",
                "raw_log": raw_log
            }
            
            response = await client.post(
                f"{INGEST_URL}/ingest/demo",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WorkItem created successfully: {result.get('work_item_id', 'unknown')}")
            return result
    except httpx.HTTPStatusError as e:
        logger.error(f"Ingest service returned error: {e.response.status_code} - {e.response.text}")
        return None
    except httpx.RequestError as e:
        logger.error(f"Failed to connect to Ingest service: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error creating work item: {e}")
        return None


async def monitoring_loop():
    """Main monitoring loop that continuously logs and detects errors."""
    global monitoring_stats
    
    logger.info(f"Monitoring loop started for service: {SERVICE_NAME}")
    monitoring_stats["started_at"] = datetime.now().isoformat()
    monitoring_stats["service_name"] = SERVICE_NAME
    monitoring_stats["error_probability"] = ERROR_PROBABILITY
    monitoring_stats["log_interval"] = LOG_INTERVAL
    
    while monitoring_active:
        try:
            # Generate normal log message
            log_level = random.choice(["INFO", "WARN", "DEBUG"])
            log_message = generate_normal_log_message(SERVICE_NAME)
            logger.info(f"[{log_level}] {log_message}")
            
            # Check for error (based on probability)
            if random.random() < ERROR_PROBABILITY:
                # Select random error type configuration
                error_type_config = random.choice(ERROR_TYPE_TEMPLATES)
                raw_error_message, severity = generate_error_message(error_type_config, SERVICE_NAME)
                
                logger.error(f"[ERROR] {raw_error_message}")
                
                # Preprocess with LLM
                cleaned_description = await llm_preprocess_log(raw_error_message, SERVICE_NAME)
                
                # Create work item via Ingest
                result = await create_work_item_via_ingest(
                    service=SERVICE_NAME,
                    severity=severity,
                    description=cleaned_description,
                    raw_log=raw_error_message
                )
                
                if result:
                    monitoring_stats["error_count"] += 1
                    monitoring_stats["last_error_at"] = datetime.now().isoformat()
                    logger.info(f"Incident created: {result.get('work_item_id', 'unknown')} (severity: {severity})")
                else:
                    logger.warning("Failed to create work item via Ingest service")
            
            # Wait before next log cycle
            await asyncio.sleep(LOG_INTERVAL)
            
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
            break
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}", exc_info=True)
            # Continue monitoring even if there's an error
            await asyncio.sleep(LOG_INTERVAL)
    
    logger.info("Monitoring loop stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global monitoring_task, monitoring_active
    
    # Startup
    if AUTO_START:
        logger.info("Auto-starting monitoring loop...")
        monitoring_active = True
        monitoring_task = asyncio.create_task(monitoring_loop())
    
    yield
    
    # Shutdown
    logger.info("Shutting down monitoring service...")
    monitoring_active = False
    if monitoring_task:
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
    logger.info("Monitoring service shut down")


app = FastAPI(
    title="Monitoring Service",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/healthz")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "monitoring",
        "monitoring_active": monitoring_active,
        "uptime_seconds": (
            (datetime.now() - datetime.fromisoformat(monitoring_stats["started_at"])).total_seconds()
            if monitoring_stats.get("started_at")
            else 0
        )
    }


@app.post("/monitoring/start")
async def start_monitoring():
    """Start monitoring loop"""
    global monitoring_task, monitoring_active
    
    if monitoring_active:
        return {
            "status": "already_running",
            "message": "Monitoring is already running"
        }
    
    monitoring_active = True
    monitoring_task = asyncio.create_task(monitoring_loop())
    
    return {
        "status": "started",
        "service_name": SERVICE_NAME,
        "error_probability": ERROR_PROBABILITY,
        "log_interval": LOG_INTERVAL,
        "message": "Monitoring loop started"
    }


@app.post("/monitoring/stop")
async def stop_monitoring():
    """Stop monitoring loop"""
    global monitoring_task, monitoring_active
    
    if not monitoring_active:
        return {
            "status": "already_stopped",
            "message": "Monitoring is not running"
        }
    
    monitoring_active = False
    if monitoring_task:
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
        monitoring_task = None
    
    return {
        "status": "stopped",
        "message": "Monitoring loop stopped"
    }


@app.get("/monitoring/status")
async def get_monitoring_status():
    """Get current monitoring status"""
    return {
        "status": "running" if monitoring_active else "stopped",
        "service_name": monitoring_stats.get("service_name", SERVICE_NAME),
        "error_count": monitoring_stats.get("error_count", 0),
        "last_error_at": monitoring_stats.get("last_error_at"),
        "started_at": monitoring_stats.get("started_at"),
        "error_probability": monitoring_stats.get("error_probability", ERROR_PROBABILITY),
        "log_interval": monitoring_stats.get("log_interval", LOG_INTERVAL)
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("MONITORING_SERVICE_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
