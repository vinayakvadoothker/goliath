"use client"

import { Incident } from "@/types"
import { useState } from "react"

interface IncidentTimelineProps {
  incidents: Incident[]
}

export function IncidentTimeline({ incidents }: IncidentTimelineProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const getSeverityStyles = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'sev1':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          badge: 'bg-red-500 text-white',
          text: 'text-red-700'
        }
      case 'sev2':
        return {
          bg: 'bg-orange-50',
          border: 'border-orange-200',
          badge: 'bg-orange-500 text-white',
          text: 'text-orange-700'
        }
      case 'sev3':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          badge: 'bg-yellow-500 text-white',
          text: 'text-yellow-700'
        }
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          badge: 'bg-gray-500 text-white',
          text: 'text-gray-700'
        }
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'routing':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'assigned':
        return 'bg-purple-100 text-purple-800 border-purple-300'
      case 'resolved':
        return 'bg-green-100 text-green-800 border-green-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  return (
    <div className="space-y-3">
      {incidents.length === 0 ? (
        <div className="text-center py-8 text-gray-500 text-sm">
          No active incidents
        </div>
      ) : (
        incidents.map((incident) => {
          const severityStyles = getSeverityStyles(incident.severity)
          const isExpanded = expandedId === incident.id
          
          return (
            <div
              key={incident.id}
              className={`${severityStyles.bg} ${severityStyles.border} border rounded-lg overflow-hidden transition-all hover:shadow-md`}
            >
              <button
                onClick={() => setExpandedId(isExpanded ? null : incident.id)}
                className="w-full px-4 py-3 flex items-center justify-between hover:bg-opacity-50 transition-colors"
              >
                <div className="flex items-center gap-3 flex-1">
                  <span className={`${severityStyles.badge} px-2.5 py-1 rounded text-xs font-bold uppercase`}>
                    {incident.severity}
                  </span>
                  <span className="text-sm font-semibold text-gray-900">
                    {incident.error_type}
                  </span>
                  <span className={`${getStatusBadge(incident.status)} px-2 py-0.5 rounded text-xs font-medium border`}>
                    {incident.status}
                  </span>
                </div>
                <svg
                  className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              
              {isExpanded && (
                <div className="px-4 pb-4 pt-2 border-t border-gray-200 space-y-2">
                  <div className="text-sm">
                    <span className="font-medium text-gray-700">Error: </span>
                    <span className="text-gray-900">{incident.error_message}</span>
                  </div>
                  {incident.assignee && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700">Assigned to: </span>
                      <span className="text-gray-900">{incident.assignee}</span>
                    </div>
                  )}
                  {incident.jira_key && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700">Jira Issue: </span>
                      <span className="text-blue-600 hover:underline">{incident.jira_key}</span>
                    </div>
                  )}
                  <div className="text-xs text-gray-500 pt-1">
                    Created: {new Date(incident.created_at).toLocaleString()}
                  </div>
                </div>
              )}
            </div>
          )
        })
      )}
    </div>
  )
}

