'use client'

import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-react'
import { useProfiles } from '@/lib/queries'

const SERVICES = ['api-service', 'payment-service', 'database-service']

export default function PeoplePage() {
  const router = useRouter()
  const [selectedService, setSelectedService] = useState(SERVICES[0])
  const [search, setSearch] = useState('')

  const { data: profilesData, isLoading } = useProfiles(selectedService)

  // Get all unique humans across all services
  const allHumans = useMemo(() => {
    // For now, just show humans from selected service
    // TODO: Aggregate across all services
    return profilesData?.humans || []
  }, [profilesData])

  const filteredHumans = useMemo(() => {
    if (!search) return allHumans
    const searchLower = search.toLowerCase()
    return allHumans.filter(
      (h) =>
        h.display_name.toLowerCase().includes(searchLower) ||
        h.human_id.toLowerCase().includes(searchLower)
    )
  }, [allHumans, search])

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12 text-muted-foreground">Loading people...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">People</h1>
        <p className="text-muted-foreground">Browse all humans and their capabilities.</p>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* People Table */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Service</TableHead>
              <TableHead>Fit Score</TableHead>
              <TableHead>Resolves</TableHead>
              <TableHead>Transfers</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredHumans.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                  No people found
                </TableCell>
              </TableRow>
            ) : (
              filteredHumans.map((human) => (
                <TableRow
                  key={human.human_id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => router.push(`/people/${human.human_id}`)}
                >
                  <TableCell className="font-medium">{human.display_name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{selectedService}</Badge>
                  </TableCell>
                  <TableCell>{(human.fit_score * 100).toFixed(1)}%</TableCell>
                  <TableCell>{human.resolves_count}</TableCell>
                  <TableCell>{human.transfers_count}</TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => router.push(`/people/${human.human_id}`)}
                    >
                      View Profile
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

