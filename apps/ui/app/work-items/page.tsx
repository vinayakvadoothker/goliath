'use client'

import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { WorkItemsTable } from '@/components/work-items/WorkItemsTable'
import { WorkItemsFilters } from '@/components/work-items/WorkItemsFilters'
import { WorkItemsPagination } from '@/components/work-items/WorkItemsPagination'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { useWorkItems } from '@/lib/queries'
import type { WorkItem } from '@/lib/types'

export default function WorkItemsPage() {
  const router = useRouter()
  const [filters, setFilters] = useState<{ service?: string; severity?: string; search?: string }>({})
  const [offset, setOffset] = useState(0)
  const limit = 50

  const { data, isLoading, error } = useWorkItems({
    ...filters,
    limit,
    offset,
  })

  // Client-side search filter
  const filteredWorkItems = useMemo(() => {
    if (!data?.work_items || !filters.search) return data?.work_items || []
    const searchLower = filters.search.toLowerCase()
    return data.work_items.filter((wi: WorkItem) =>
      wi.description.toLowerCase().includes(searchLower) ||
      wi.id.toLowerCase().includes(searchLower) ||
      wi.service.toLowerCase().includes(searchLower)
    )
  }, [data?.work_items, filters.search])

  const handleRowClick = (id: string) => {
    router.push(`/work-items/${id}`)
  }

  const handlePageChange = (newOffset: number) => {
    setOffset(newOffset)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <div className="text-red-500 mb-2">Error loading work items</div>
          <div className="text-sm text-muted-foreground">{String(error)}</div>
        </div>
      </div>
    )
  }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Work Items</h1>
          <p className="text-muted-foreground">Browse and manage all work items.</p>
                </div>
        <Link href="/work-items/new">
          <Button>Create New</Button>
                                    </Link>
            </div>

      <WorkItemsFilters onFilterChange={(newFilters) => {
        setFilters(newFilters)
        setOffset(0) // Reset to first page on filter change
      }} />

      {isLoading ? (
        <div className="text-center py-12 text-muted-foreground">Loading work items...</div>
      ) : (
        <>
          <WorkItemsTable workItems={filteredWorkItems} onRowClick={handleRowClick} />
          {data && (
            <WorkItemsPagination
              total={filters.search ? filteredWorkItems.length : data.total}
              limit={limit}
              offset={offset}
              onPageChange={handlePageChange}
            />
          )}
        </>
      )}
            </div>
  )
}
