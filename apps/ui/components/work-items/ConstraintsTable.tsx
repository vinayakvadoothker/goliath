'use client'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { CheckCircle2, XCircle } from 'lucide-react'
import type { ConstraintResult } from '@/lib/types'

interface ConstraintsTableProps {
  constraints: ConstraintResult[]
}

export function ConstraintsTable({ constraints }: ConstraintsTableProps) {
  if (constraints.length === 0) {
    return (
      <div className="text-sm text-muted-foreground">No constraints checked</div>
    )
  }

  return (
    <div>
      <h4 className="text-sm font-semibold mb-2">Constraints Checked</h4>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Constraint</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Reason</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {constraints.map((constraint, idx) => (
              <TableRow key={idx}>
                <TableCell className="font-mono text-sm">{constraint.name}</TableCell>
                <TableCell>
                  {constraint.passed ? (
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-500" />
                  )}
                </TableCell>
                <TableCell className="text-sm text-muted-foreground">
                  {constraint.reason || 'N/A'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

