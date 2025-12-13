import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { SeverityBadge } from "@/components/shared/SeverityBadge";
import { ConfidenceBadge } from "@/components/work-items/ConfidenceBadge";
import Link from "next/link";
import { Filter, Search, SlidersHorizontal, ArrowUpDown } from "lucide-react";

const workItems = [
    { id: "WI-3921", summary: "High latency in payments-api", service: "payments-api", severity: "sev1", status: "Open", assigned: "pager-bot", confidence: 0.98, time: "2m ago" },
    { id: "WI-3920", summary: "Error rate spiking in auth-service", service: "auth-service", severity: "sev2", status: "In Progress", assigned: "sarah-engineer", confidence: 0.85, time: "15m ago" },
    { id: "WI-3919", summary: "Disk usage warning on db-shard-04", service: "database", severity: "sev3", status: "Open", assigned: "db-admin-bot", confidence: 0.92, time: "45m ago" },
    { id: "WI-3918", summary: "Frontend assets 404ing", service: "frontend-cdn", severity: "sev2", status: "Resolved", assigned: "auto-revert", confidence: 0.99, time: "1h ago" },
    { id: "WI-3917", summary: "Customer report: Login failure", service: "auth-service", severity: "sev3", status: "Open", assigned: "triage-team", confidence: 0.45, time: "2h ago" },
];

export default function WorkItemsPage() {
    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Work Items</h1>
                    <p className="text-muted-foreground">Manage and triage incoming incidents and tasks.</p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                        <SlidersHorizontal className="mr-2 h-4 w-4" />
                        View Settings
                    </Button>
                    <Button>Create Work Item</Button>
                </div>
            </div>

            {/* Filters Bar */}
            <div className="flex flex-col gap-4 md:flex-row md:items-center bg-card p-4 rounded-lg border">
                <div className="relative flex-1">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Search work items..." className="pl-9" />
                </div>
                <div className="flex items-center gap-2">
                    <Select>
                        <SelectTrigger className="w-[180px]">
                            <div className="flex items-center gap-2">
                                <Filter className="h-3.5 w-3.5" />
                                <SelectValue placeholder="Severity" />
                            </div>
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Severities</SelectItem>
                            <SelectItem value="sev1">SEV1</SelectItem>
                            <SelectItem value="sev2">SEV2</SelectItem>
                            <SelectItem value="sev3">SEV3</SelectItem>
                        </SelectContent>
                    </Select>

                    <Select>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Statuses</SelectItem>
                            <SelectItem value="open">Open</SelectItem>
                            <SelectItem value="inprogress">In Progress</SelectItem>
                            <SelectItem value="resolved">Resolved</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* Data Table */}
            <div className="rounded-md border bg-card">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead className="w-[100px]">ID</TableHead>
                            <TableHead>Summary</TableHead>
                            <TableHead>Service</TableHead>
                            <TableHead>Severity</TableHead>
                            <TableHead>Confidence</TableHead>
                            <TableHead>Assigned To</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead className="text-right">Created</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {workItems.map((item) => (
                            <TableRow key={item.id}>
                                <TableCell className="font-mono font-medium">
                                    <Link href={`/work-items/${item.id}`} className="hover:underline text-primary">
                                        {item.id}
                                    </Link>
                                </TableCell>
                                <TableCell className="font-medium">
                                    <Link href={`/work-items/${item.id}`} className="hover:underline">
                                        {item.summary}
                                    </Link>
                                </TableCell>
                                <TableCell>
                                    <Badge variant="outline" className="font-mono text-xs text-muted-foreground">{item.service}</Badge>
                                </TableCell>
                                <TableCell>
                                    <SeverityBadge severity={item.severity as any} />
                                </TableCell>
                                <TableCell>
                                    <ConfidenceBadge confidence={item.confidence} />
                                </TableCell>
                                <TableCell>
                                    <div className="flex items-center gap-2">
                                        <div className="h-6 w-6 rounded-full bg-secondary grid place-items-center text-[10px] font-bold">
                                            {item.assigned.substring(0, 2).toUpperCase()}
                                        </div>
                                        <span className="text-sm">{item.assigned}</span>
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <Badge variant={item.status === 'Resolved' ? 'success' : 'secondary'}>
                                        {item.status}
                                    </Badge>
                                </TableCell>
                                <TableCell className="text-right text-muted-foreground text-xs">
                                    {item.time}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>

            <div className="flex items-center justify-end space-x-2 py-4">
                <Button variant="outline" size="sm" disabled>Previous</Button>
                <Button variant="outline" size="sm">Next</Button>
            </div>
        </div>
    );
}
