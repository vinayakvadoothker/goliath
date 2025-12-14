'use client'

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
import { formatDistanceToNow } from 'date-fns'
import type { WorkItem } from '@/lib/types'
import Link from 'next/link'

interface WorkItemsTableProps {
  workItems: WorkItem[]
  onRowClick?: (id: string) => void
}

export function WorkItemsTable({ workItems, onRowClick }: WorkItemsTableProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'sev1':
        return 'bg-red-500/20 text-red-400 border-red-500/20'
      case 'sev2':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/20'
      case 'sev3':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/20'
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/20'
    }
  }

  const getStatusBadge = (workItem: WorkItem) => {
    if (workItem.jira_issue_key) {
      return <Badge variant="outline" className="bg-green-500/20 text-green-400">Resolved</Badge>
    }
    return <Badge variant="outline" className="bg-blue-500/20 text-blue-400">Open</Badge>
  }

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Service</TableHead>
            <TableHead>Severity</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {workItems.length === 0 ? (
            <TableRow>
              <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                No work items found
              </TableCell>
            </TableRow>
          ) : (
            workItems.map((item) => (
              <TableRow
                key={item.id}
                className="cursor-pointer hover:bg-muted/50"
                onClick={() => onRowClick?.(item.id)}
              >
                <TableCell className="font-mono text-sm">{item.id}</TableCell>
                <TableCell>{item.service}</TableCell>
                <TableCell>
                  <Badge variant="outline" className={getSeverityColor(item.severity)}>
                    {item.severity.toUpperCase()}
                  </Badge>
                </TableCell>
                <TableCell className="text-sm">
                  {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                </TableCell>
                <TableCell>{getStatusBadge(item)}</TableCell>
                <TableCell onClick={(e) => e.stopPropagation()}>
                  <Link href={`/work-items/${item.id}`}>
                    <Button variant="ghost" size="sm">
                      View
                    </Button>
                  </Link>
                </TableCell>
              </TableRow>
            ))
          )}
        </TableBody>
      </Table>
    </div>
  )
}

