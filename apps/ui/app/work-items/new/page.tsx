'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useCreateWorkItem } from '@/lib/queries'
import Link from 'next/link'

export default function CreateWorkItemPage() {
  const router = useRouter()
  const createWorkItem = useCreateWorkItem()

  const [service, setService] = useState('')
  const [severity, setSeverity] = useState('')
  const [description, setDescription] = useState('')
  const [type, setType] = useState('incident')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!service || !severity || !description) return

    try {
      const result = await createWorkItem.mutateAsync({
        type,
        service,
        severity,
        description,
        origin_system: 'ui',
      })
      router.push(`/work-items/${result.id}`)
    } catch (error) {
      console.error('Failed to create work item:', error)
    }
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Create Work Item</h1>
        <p className="text-muted-foreground">Manually create a new work item.</p>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Work Item Details</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="service">Service *</Label>
              <Select value={service} onValueChange={setService}>
                <SelectTrigger id="service" className="mt-1">
                  <SelectValue placeholder="Select service" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="api-service">API Service</SelectItem>
                  <SelectItem value="payment-service">Payment Service</SelectItem>
                  <SelectItem value="database-service">Database Service</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="severity">Severity *</Label>
              <Select value={severity} onValueChange={setSeverity}>
                <SelectTrigger id="severity" className="mt-1">
                  <SelectValue placeholder="Select severity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sev1">SEV1 - Critical</SelectItem>
                  <SelectItem value="sev2">SEV2 - High</SelectItem>
                  <SelectItem value="sev3">SEV3 - Medium</SelectItem>
                  <SelectItem value="sev4">SEV4 - Low</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="type">Type</Label>
              <Select value={type} onValueChange={setType}>
                <SelectTrigger id="type" className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="incident">Incident</SelectItem>
                  <SelectItem value="task">Task</SelectItem>
                  <SelectItem value="bug">Bug</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                placeholder="Describe the work item..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={6}
                className="mt-1"
                required
              />
            </div>

            <div className="flex justify-end gap-2">
              <Link href="/work-items">
                <Button type="button" variant="outline">
                  Cancel
                </Button>
              </Link>
              <Button type="submit" disabled={!service || !severity || !description || createWorkItem.isPending}>
                {createWorkItem.isPending ? 'Creating...' : 'Create Work Item'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}

