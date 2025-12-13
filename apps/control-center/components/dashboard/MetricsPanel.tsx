"use client"

interface Metric {
  name: string
  value: number
  unit?: string
  status: 'healthy' | 'warning' | 'error'
}

interface MetricsPanelProps {
  metrics: Metric[]
}

export function MetricsPanel({ metrics }: MetricsPanelProps) {
  const getStatusColors = (status: string) => {
    switch (status) {
      case 'healthy':
        return {
          bg: 'bg-emerald-50',
          border: 'border-emerald-200',
          text: 'text-emerald-700',
          value: 'text-emerald-600',
          progress: 'bg-emerald-500'
        }
      case 'warning':
        return {
          bg: 'bg-amber-50',
          border: 'border-amber-200',
          text: 'text-amber-700',
          value: 'text-amber-600',
          progress: 'bg-amber-500'
        }
      case 'error':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          text: 'text-red-700',
          value: 'text-red-600',
          progress: 'bg-red-500'
        }
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-200',
          text: 'text-gray-700',
          value: 'text-gray-600',
          progress: 'bg-gray-500'
        }
    }
  }

  const formatValue = (value: number, unit?: string) => {
    if (unit === '%') {
      return `${value.toFixed(1)}%`
    }
    return `${value.toFixed(0)}${unit || ''}`
  }

  return (
    <div className="space-y-3">
      {metrics.map((metric) => {
        const colors = getStatusColors(metric.status)
        return (
          <div
            key={metric.name}
            className={`${colors.bg} ${colors.border} border rounded-lg p-4 transition-all hover:shadow-sm`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className={`text-sm font-medium ${colors.text}`}>
                {metric.name}
              </span>
              <span className={`text-lg font-semibold ${colors.value}`}>
                {formatValue(metric.value, metric.unit)}
              </span>
            </div>
            {metric.unit === '%' && (
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full ${colors.progress} rounded-full transition-all duration-300`}
                  style={{ width: `${Math.min(metric.value, 100)}%` }}
                />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

