"use client"

import { LogEntry } from "@/types"
import { useEffect, useRef } from "react"

interface LogStreamProps {
  logs: LogEntry[]
}

export function LogStream({ logs }: LogStreamProps) {
  const scrollViewportRef = useRef<HTMLDivElement>(null)
  const shouldAutoScroll = useRef(true)

  useEffect(() => {
    // Auto-scroll to bottom when new logs arrive
    if (shouldAutoScroll.current && scrollViewportRef.current) {
      scrollViewportRef.current.scrollTop = scrollViewportRef.current.scrollHeight
    }
  }, [logs])

  // Detect if user has scrolled up (disable auto-scroll)
  const handleScroll = () => {
    if (scrollViewportRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollViewportRef.current
      // If user is near bottom (within 50px), enable auto-scroll
      shouldAutoScroll.current = scrollHeight - scrollTop - clientHeight < 50
    }
  }

  const getLevelStyles = (level: string) => {
    switch (level) {
      case 'ERROR':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          badge: 'bg-red-100 text-red-800 border-red-300',
          text: 'text-red-900'
        }
      case 'WARN':
        return {
          bg: 'bg-amber-50',
          border: 'border-amber-200',
          badge: 'bg-amber-100 text-amber-800 border-amber-300',
          text: 'text-amber-900'
        }
      case 'INFO':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          badge: 'bg-blue-100 text-blue-800 border-blue-300',
          text: 'text-blue-900'
        }
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          badge: 'bg-gray-100 text-gray-800 border-gray-300',
          text: 'text-gray-900'
        }
    }
  }

  const scrollToBottom = () => {
    if (scrollViewportRef.current) {
      scrollViewportRef.current.scrollTop = scrollViewportRef.current.scrollHeight
      shouldAutoScroll.current = true
    }
  }

  return (
    <div className="h-full flex flex-col bg-white rounded-lg border border-gray-200">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <h3 className="text-sm font-semibold text-gray-900">Live Log Stream</h3>
        {logs.length > 0 && (
          <button
            onClick={scrollToBottom}
            className="text-xs text-gray-500 hover:text-gray-700 transition-colors px-2 py-1 rounded hover:bg-gray-100"
          >
            Scroll to bottom
          </button>
        )}
      </div>
      <div className="flex-1 overflow-hidden">
        <div
          ref={scrollViewportRef}
          onScroll={handleScroll}
          className="h-full overflow-y-auto px-4 py-3 bg-gray-50"
          style={{ maxHeight: '1000px', minHeight: '500px' }}
        >
          <div className="space-y-1 font-mono text-sm">
            {logs.length === 0 ? (
              <div className="text-gray-500 text-sm py-4">
                No logs yet. Interact with the product to generate logs.
              </div>
            ) : (
              logs.map((log) => {
                const styles = getLevelStyles(log.level)
                return (
                  <div
                    key={log.id}
                    className={`${styles.bg} ${styles.border} border rounded px-3 py-2 flex items-start gap-3`}
                  >
                    <span className="text-gray-500 whitespace-nowrap text-xs shrink-0 font-normal">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </span>
                    <span className={`${styles.badge} px-2 py-0.5 rounded text-xs font-semibold shrink-0 border`}>
                      {log.level}
                    </span>
                    <span className={`flex-1 break-words min-w-0 ${styles.text} text-sm`}>
                      {log.message}
                    </span>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

