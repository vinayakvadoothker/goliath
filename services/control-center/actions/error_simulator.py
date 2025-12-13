"""
Error simulation logic - generates realistic error messages
"""
import random
from typing import Tuple

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
    }
]

def generate_error_message(error_type_config: dict, service_name: str = "api-service") -> Tuple[str, str, str]:
    """
    Generate a realistic error message with dynamic values.
    Returns: (error_message, severity, error_type_name)
    """
    template = random.choice(error_type_config["templates"])
    severity = error_type_config["severity"]
    error_type_name = error_type_config.get("name", "unknown")
    
    # Fill in dynamic values
    if "endpoint_pool" in error_type_config:
        endpoint = random.choice(error_type_config["endpoint_pool"])
        if "rate_range" in error_type_config:
            rate = random.randint(*error_type_config["rate_range"])
            return template.format(rate=rate, endpoint=endpoint), severity, "high_error_rate"
        elif "error_count_range" in error_type_config:
            error_count = random.randint(*error_type_config["error_count_range"])
            return template.format(endpoint=endpoint, error_count=error_count), severity, "api_500_errors"
        elif "latency_range" in error_type_config:
            latency = random.randint(*error_type_config["latency_range"])
            return template.format(endpoint=endpoint, latency=latency), severity, "response_time_degradation"
    
    if "db_pool" in error_type_config:
        db_name = random.choice(error_type_config["db_pool"])
        if "timeout_range" in error_type_config:
            timeout = random.randint(*error_type_config["timeout_range"])
            return template.format(db_name=db_name, timeout=timeout), severity, "database_timeout"
        elif "pool_size_range" in error_type_config:
            pool_size = random.randint(*error_type_config["pool_size_range"])
            return template.format(db_name=db_name, pool_size=pool_size), severity, "database_timeout"
        else:
            return template.format(db_name=db_name), severity, "database_timeout"
    
    if "usage_range" in error_type_config:
        usage = random.randint(*error_type_config["usage_range"])
        return template.format(service=service_name, usage=usage), severity, "memory_leak"
    
    if "response_time_range" in error_type_config:
        response_time = random.randint(*error_type_config["response_time_range"])
        return template.format(service=service_name, response_time=response_time), severity, "service_degradation"
    
    if "cache_pool" in error_type_config:
        cache_name = random.choice(error_type_config["cache_pool"])
        miss_rate = random.randint(*error_type_config["miss_rate_range"])
        return template.format(cache_name=cache_name, miss_rate=miss_rate), severity, "cache_miss_spike"
    
    if "disk_pool" in error_type_config:
        disk_name = random.choice(error_type_config["disk_pool"])
        io_wait = random.randint(*error_type_config["io_wait_range"])
        return template.format(disk_name=disk_name, io_wait=io_wait), severity, "disk_io_saturation"
    
    if "cpu_usage_range" in error_type_config:
        cpu_usage = random.randint(*error_type_config["cpu_usage_range"])
        return template.format(service=service_name, cpu_usage=cpu_usage), severity, "cpu_throttling"
    
    if "interface_pool" in error_type_config:
        interface = random.choice(error_type_config["interface_pool"])
        loss_rate = random.randint(*error_type_config["loss_rate_range"])
        return template.format(interface=interface, loss_rate=loss_rate), severity, "network_packet_loss"
    
    if "queue_pool" in error_type_config:
        queue_name = random.choice(error_type_config["queue_pool"])
        depth = random.randint(*error_type_config["depth_range"])
        return template.format(queue_name=queue_name, depth=depth), severity, "queue_backlog"
    
    return template.format(service=service_name), severity, "unknown"

def get_error_type_by_name(name: str) -> dict:
    """Get error type configuration by name."""
    error_type_map = {
        "high_error_rate": ERROR_TYPE_TEMPLATES[0],
        "database_timeout": ERROR_TYPE_TEMPLATES[1],
        "memory_leak": ERROR_TYPE_TEMPLATES[2],
        "api_500_errors": ERROR_TYPE_TEMPLATES[3],
        "service_degradation": ERROR_TYPE_TEMPLATES[4],
        "cache_miss_spike": ERROR_TYPE_TEMPLATES[5],
        "response_time_degradation": ERROR_TYPE_TEMPLATES[6],
        "disk_io_saturation": ERROR_TYPE_TEMPLATES[7],
        "cpu_throttling": ERROR_TYPE_TEMPLATES[8],
        "network_packet_loss": ERROR_TYPE_TEMPLATES[9],
        "queue_backlog": ERROR_TYPE_TEMPLATES[10],
    }
    return error_type_map.get(name, ERROR_TYPE_TEMPLATES[0])

