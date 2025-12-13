"use client"

import { useEffect, useState } from "react"
import { ProductInterface } from "@/components/product/ProductInterface"
import { Sidebar } from "@/components/layout/Sidebar"
import { wsClient } from "@/lib/websocket"
import { SystemState } from "@/types"

export default function Home() {
  const [state, setState] = useState<SystemState>({
    metrics: [],
    logs: [],
    incidents: [],
    latest_decision: undefined
  })

  useEffect(() => {
    // Connect WebSocket
    wsClient.connect()

    // Listen for state updates
    const handleStateUpdate = (data: any) => {
      console.log("State update received:", data)
      // Ensure logs is always an array
      const updatedState: SystemState = {
        metrics: data.metrics || {},
        logs: Array.isArray(data.logs) ? data.logs : [],
        incidents: Array.isArray(data.incidents) ? data.incidents : [],
        latest_decision: data.latest_decision
      }
      setState(updatedState)
    }

    wsClient.on("state_update", handleStateUpdate)

    // Wait for WebSocket to be ready before requesting state
    const checkAndRequestState = () => {
      const ws = (wsClient as any).ws
      if (ws && ws.readyState === WebSocket.OPEN) {
        console.log("WebSocket ready, requesting state")
        wsClient.send("get_state")
      } else {
        console.log("WebSocket not ready yet, retrying...")
        setTimeout(checkAndRequestState, 500)
      }
    }

    // Start checking after a short delay
    const timeout = setTimeout(checkAndRequestState, 1000)

    return () => {
      clearTimeout(timeout)
      wsClient.off("state_update", handleStateUpdate)
      // Don't disconnect - let it stay connected
    }
  }, [])


  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white p-4">
        <div>
          <h1 className="text-xl font-normal text-gray-800" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>Goliath Platform</h1>
          <p className="text-xs text-gray-500 mt-0.5" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>Intelligent incident routing with Datadog monitoring</p>
        </div>
      </div>

      {/* Main Content: Product + Monitoring Split */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Left: Product Interface (Google.com-like) */}
        <div className="flex-1 border-r border-gray-200 overflow-y-auto bg-white">
          <ProductInterface />
        </div>

        {/* Right: Monitoring Sidebar */}
        <div className="w-[600px] overflow-hidden bg-white">
          <Sidebar state={state} />
        </div>
      </div>
    </main>
  )
}
