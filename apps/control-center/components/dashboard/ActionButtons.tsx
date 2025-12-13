"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { wsClient } from "@/lib/websocket"
import { useState, useEffect } from "react"

const ERROR_ACTIONS = [
  { type: "high_error_rate", label: "Simulate High Load", severity: "sev1", variant: "destructive" as const },
  { type: "database_timeout", label: "Database Timeout", severity: "sev2", variant: "destructive" as const },
  { type: "memory_leak", label: "Memory Leak", severity: "sev1", variant: "destructive" as const },
  { type: "api_500_errors", label: "API 500 Errors", severity: "sev2", variant: "destructive" as const },
  { type: "service_degradation", label: "Service Degradation", severity: "sev2", variant: "destructive" as const },
  { type: "cache_miss_spike", label: "Cache Miss Spike", severity: "sev3", variant: "destructive" as const },
  { type: "disk_io_saturation", label: "Disk I/O Saturation", severity: "sev2", variant: "destructive" as const },
  { type: "cpu_throttling", label: "CPU Throttling", severity: "sev2", variant: "destructive" as const },
  { type: "network_packet_loss", label: "Network Packet Loss", severity: "sev2", variant: "destructive" as const },
  { type: "queue_backlog", label: "Queue Backlog", severity: "sev2", variant: "destructive" as const },
]

const NORMAL_ACTIONS = [
  { type: "process_request", label: "Process Request", variant: "default" as const },
  { type: "run_query", label: "Run Query", variant: "default" as const },
  { type: "cache_lookup", label: "Cache Lookup", variant: "default" as const },
]

export function ActionButtons() {
  const [loading, setLoading] = useState<string | null>(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    // Check connection status periodically
    const checkConnection = setInterval(() => {
      const ws = (wsClient as any).ws
      const isConnected = ws?.readyState === WebSocket.OPEN
      setConnected(isConnected)
      
      if (!isConnected) {
        if (!ws || ws.readyState === WebSocket.CLOSED) {
          console.log('WebSocket closed, reconnecting...')
          wsClient.connect()
        }
      }
    }, 1000)

    return () => {
      clearInterval(checkConnection)
    }
  }, [])

  const handleAction = async (actionType: string, isError: boolean) => {
    setLoading(actionType)
    
    // Wait for connection if not ready
    const waitForConnection = (maxWait = 5000): Promise<boolean> => {
      return new Promise((resolve) => {
        const startTime = Date.now()
        const check = () => {
          const ws = (wsClient as any).ws
          if (ws && ws.readyState === WebSocket.OPEN) {
            resolve(true)
          } else if (Date.now() - startTime > maxWait) {
            resolve(false)
          } else {
            setTimeout(check, 100)
          }
        }
        check()
      })
    }

    const isReady = await waitForConnection()
    if (!isReady) {
      console.error('WebSocket not connected after waiting')
      alert('WebSocket not connected. Please check if the backend is running on port 8007.')
      setLoading(null)
      return
    }

    try {
      if (isError) {
        wsClient.send("trigger_error", actionType)
      } else {
        wsClient.send("normal_action", actionType)
      }
    } catch (error) {
      console.error("Error sending action:", error)
    } finally {
      setTimeout(() => setLoading(null), 2000)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Normal Operations</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {NORMAL_ACTIONS.map((action) => (
            <Button
              key={action.type}
              variant={action.variant}
              className="w-full"
              onClick={() => handleAction(action.type, false)}
              disabled={loading === action.type}
            >
              {loading === action.type ? "Processing..." : action.label}
            </Button>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Error Triggers</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {!connected && (
            <div className="text-sm text-muted-foreground mb-2">
              {connected ? "✓ Connected" : "⏳ Connecting..."}
            </div>
          )}
          {ERROR_ACTIONS.map((action) => (
            <Button
              key={action.type}
              variant={action.variant}
              className="w-full"
              onClick={() => handleAction(action.type, true)}
              disabled={loading === action.type || !connected}
            >
              {loading === action.type ? "Triggering..." : action.label}
            </Button>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

