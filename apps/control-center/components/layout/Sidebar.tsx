"use client"

import { useState } from "react"
import { SystemHealth } from "@/components/dashboard/SystemHealth"
import { MetricsPanel } from "@/components/dashboard/MetricsPanel"
import { LogStream } from "@/components/dashboard/LogStream"
import { IncidentTimeline } from "@/components/dashboard/IncidentTimeline"
import { SystemState } from "@/types"

interface SidebarProps {
  state: SystemState
}

type TabType = "overview" | "metrics" | "logs" | "incidents" | "services"

export function Sidebar({ state }: SidebarProps) {
  const [activeTab, setActiveTab] = useState<TabType>("overview")

  const metrics = [
    {
      name: "Requests/sec",
      value: (state.metrics as any)?.requests_per_sec || 0,
      status: ((state.metrics as any)?.requests_per_sec || 0) > 200 ? 'warning' as const : 'healthy' as const
    },
    {
      name: "Error Rate",
      value: (state.metrics as any)?.error_rate || 0,
      unit: "/sec",
      status: ((state.metrics as any)?.error_rate || 0) > 10 ? 'error' as const : ((state.metrics as any)?.error_rate || 0) > 5 ? 'warning' as const : 'healthy' as const
    },
    {
      name: "CPU Usage",
      value: (state.metrics as any)?.cpu_usage || 0,
      unit: "%",
      status: ((state.metrics as any)?.cpu_usage || 0) > 80 ? 'error' as const : ((state.metrics as any)?.cpu_usage || 0) > 60 ? 'warning' as const : 'healthy' as const
    },
    {
      name: "Memory Usage",
      value: (state.metrics as any)?.memory_usage || 0,
      unit: "%",
      status: ((state.metrics as any)?.memory_usage || 0) > 85 ? 'error' as const : ((state.metrics as any)?.memory_usage || 0) > 70 ? 'warning' as const : 'healthy' as const
    },
    {
      name: "Avg Latency",
      value: (state.metrics as any)?.avg_latency || 0,
      unit: "ms",
      status: ((state.metrics as any)?.avg_latency || 0) > 500 ? 'error' as const : ((state.metrics as any)?.avg_latency || 0) > 200 ? 'warning' as const : 'healthy' as const
    }
  ]

  const services = [
    { name: "API Service", status: ((state.metrics as any)?.error_rate || 0) > 10 ? 'error' as const : ((state.metrics as any)?.error_rate || 0) > 5 ? 'warning' as const : 'healthy' as const },
    { name: "Database", status: 'healthy' as const },
    { name: "Cache", status: 'healthy' as const }
  ]

  return (
    <div className="flex h-full bg-white border-r border-gray-200">
      {/* Sidebar Navigation */}
      <div className="w-48 bg-gray-50 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wider">Monitoring</h2>
        </div>
        <nav className="flex-1 py-2">
          <button
            onClick={() => setActiveTab("overview")}
            className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
              activeTab === "overview"
                ? "bg-blue-50 text-blue-700 border-r-2 border-blue-600"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Overview
            </div>
          </button>
          <button
            onClick={() => setActiveTab("metrics")}
            className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
              activeTab === "metrics"
                ? "bg-blue-50 text-blue-700 border-r-2 border-blue-600"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              Metrics
            </div>
          </button>
          <button
            onClick={() => setActiveTab("logs")}
            className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
              activeTab === "logs"
                ? "bg-blue-50 text-blue-700 border-r-2 border-blue-600"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Logs
            </div>
          </button>
          <button
            onClick={() => setActiveTab("incidents")}
            className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
              activeTab === "incidents"
                ? "bg-blue-50 text-blue-700 border-r-2 border-blue-600"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              Incidents
            </div>
          </button>
          <button
            onClick={() => setActiveTab("services")}
            className={`w-full text-left px-4 py-2.5 text-sm transition-colors ${
              activeTab === "services"
                ? "bg-blue-50 text-blue-700 border-r-2 border-blue-600"
                : "text-gray-600 hover:bg-gray-100"
            }`}
          >
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
              </svg>
              Services
            </div>
          </button>
        </nav>
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 mb-1">Datadog</div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === "overview" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">System Overview</h3>
                <SystemHealth services={services} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Metrics</h3>
                <MetricsPanel metrics={metrics.slice(0, 3)} />
              </div>
            </div>
          )}
          
          {activeTab === "metrics" && (
            <div className="h-full flex flex-col">
              <MetricsPanel metrics={metrics} />
            </div>
          )}
          
          {activeTab === "logs" && (
            <div className="h-full flex flex-col">
              <LogStream logs={state.logs || []} />
            </div>
          )}
          
          {activeTab === "incidents" && (
            <div className="h-full flex flex-col">
              <IncidentTimeline incidents={state.incidents || []} />
            </div>
          )}
          
          {activeTab === "services" && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Service Health</h3>
              <SystemHealth services={services} />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

