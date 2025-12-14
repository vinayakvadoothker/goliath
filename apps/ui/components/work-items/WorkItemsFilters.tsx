'use client'

import { useState } from 'react'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'

interface WorkItemsFiltersProps {
  onFilterChange: (filters: { service?: string; severity?: string; search?: string }) => void
}

export function WorkItemsFilters({ onFilterChange }: WorkItemsFiltersProps) {
  const [service, setService] = useState<string>('')
  const [severity, setSeverity] = useState<string>('')
  const [search, setSearch] = useState<string>('')

  const handleServiceChange = (value: string) => {
    setService(value)
    onFilterChange({ service: value === 'all' ? undefined : value, severity, search })
  }

  const handleSeverityChange = (value: string) => {
    setSeverity(value)
    onFilterChange({ service, severity: value === 'all' ? undefined : value, search })
  }

  const handleSearchChange = (value: string) => {
    setSearch(value)
    onFilterChange({ service, severity, search: value })
  }

  return (
    <div className="flex gap-4 p-4 bg-muted/50 rounded-lg border">
      <Select value={service || 'all'} onValueChange={handleServiceChange}>
        <SelectTrigger className="w-48">
          <SelectValue placeholder="All Services" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Services</SelectItem>
          <SelectItem value="api-service">API Service</SelectItem>
          <SelectItem value="payment-service">Payment Service</SelectItem>
          <SelectItem value="database-service">Database Service</SelectItem>
        </SelectContent>
      </Select>

      <Select value={severity || 'all'} onValueChange={handleSeverityChange}>
        <SelectTrigger className="w-48">
          <SelectValue placeholder="All Severities" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="all">All Severities</SelectItem>
          <SelectItem value="sev1">SEV1</SelectItem>
          <SelectItem value="sev2">SEV2</SelectItem>
          <SelectItem value="sev3">SEV3</SelectItem>
          <SelectItem value="sev4">SEV4</SelectItem>
        </SelectContent>
      </Select>

      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search by description..."
          value={search}
          onChange={(e) => handleSearchChange(e.target.value)}
          className="pl-10"
        />
      </div>
    </div>
  )
}

