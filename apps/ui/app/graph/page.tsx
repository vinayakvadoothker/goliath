"use client";

import dynamic from 'next/dynamic';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, ZoomIn, ZoomOut, Maximize, Filter } from "lucide-react";
import { useState, useEffect, useCallback } from 'react';
import { useGraph } from '@/lib/queries';

// Dynamically import ForceGraph3D with no SSR to avoid window is not defined errors
const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), {
    ssr: false,
    loading: () => <div className="h-[600px] w-full bg-muted/20 animate-pulse grid place-items-center">Loading 3D Engine...</div>
});

export default function GraphPage() {
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
    const [containerRef, setContainerRef] = useState<HTMLDivElement | null>(null);
    const [selectedNode, setSelectedNode] = useState<any>(null);
    const [nodeTypeFilter, setNodeTypeFilter] = useState<string>('all');
    const [serviceFilter, setServiceFilter] = useState<string>('all');
    const [searchQuery, setSearchQuery] = useState<string>('');

    // Fetch graph data
    const { data: graphData, isLoading, error } = useGraph({
        node_type: nodeTypeFilter !== 'all' ? nodeTypeFilter : undefined,
        service: serviceFilter !== 'all' ? serviceFilter : undefined,
        limit: 1000,
    });

    useEffect(() => {
        if (containerRef) {
            setDimensions({
                width: containerRef.clientWidth,
                height: containerRef.clientHeight
            });
        }

        const handleResize = () => {
            if (containerRef) {
                setDimensions({
                    width: containerRef.clientWidth,
                    height: containerRef.clientHeight
                });
            }
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, [containerRef]);

    // Filter nodes based on search query
    const filteredData = graphData ? {
        nodes: graphData.nodes.filter(node => {
            if (searchQuery) {
                const query = searchQuery.toLowerCase();
                return node.name.toLowerCase().includes(query) || 
                       node.id.toLowerCase().includes(query) ||
                       (node.metadata?.service && node.metadata.service.toLowerCase().includes(query));
            }
            return true;
        }),
        links: graphData.links.filter(link => {
            // Only show links if both source and target nodes are visible
            const sourceVisible = graphData.nodes.some(n => n.id === link.source);
            const targetVisible = graphData.nodes.some(n => n.id === link.target);
            return sourceVisible && targetVisible;
        }),
    } : null;

    const handleNodeClick = useCallback((node: any) => {
        setSelectedNode(node);
    }, []);

    if (isLoading) {
        return (
            <div className="h-[calc(100vh-100px)] flex flex-col space-y-4 animate-in fade-in duration-500">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Knowledge Graph</h1>
                        <p className="text-muted-foreground">Visualize relationships between people, work, and services.</p>
                    </div>
                </div>
                <div className="flex-1 grid place-items-center">
                    <div className="text-center space-y-2">
                        <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                        <p className="text-muted-foreground">Loading graph data...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="h-[calc(100vh-100px)] flex flex-col space-y-4 animate-in fade-in duration-500">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Knowledge Graph</h1>
                        <p className="text-muted-foreground">Visualize relationships between people, work, and services.</p>
                    </div>
                </div>
                <Card className="flex-1 grid place-items-center">
                    <CardContent className="text-center space-y-2">
                        <p className="text-destructive font-semibold">Failed to load graph data</p>
                        <p className="text-muted-foreground text-sm">{error instanceof Error ? error.message : 'Unknown error'}</p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (!graphData || !filteredData) {
        return (
            <div className="h-[calc(100vh-100px)] flex flex-col space-y-4 animate-in fade-in duration-500">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight">Knowledge Graph</h1>
                        <p className="text-muted-foreground">Visualize relationships between people, work, and services.</p>
                    </div>
                </div>
                <Card className="flex-1 grid place-items-center">
                    <CardContent className="text-center">
                        <p className="text-muted-foreground">No graph data available</p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="h-[calc(100vh-100px)] flex flex-col space-y-4 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Knowledge Graph</h1>
                    <p className="text-muted-foreground">
                        {graphData.stats.total_nodes} nodes, {graphData.stats.total_edges} edges
                    </p>
                </div>
                <div className="flex gap-2">
                    <Select value={nodeTypeFilter} onValueChange={setNodeTypeFilter}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Filter by type" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Types</SelectItem>
                            <SelectItem value="human">Humans</SelectItem>
                            <SelectItem value="work_item">Work Items</SelectItem>
                            <SelectItem value="decision">Decisions</SelectItem>
                        </SelectContent>
                    </Select>
                    <Select value={serviceFilter} onValueChange={setServiceFilter}>
                        <SelectTrigger className="w-[180px]">
                            <SelectValue placeholder="Filter by service" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All Services</SelectItem>
                            <SelectItem value="api-service">API Service</SelectItem>
                            <SelectItem value="payment-service">Payment Service</SelectItem>
                            <SelectItem value="database-service">Database Service</SelectItem>
                        </SelectContent>
                    </Select>
                    <div className="relative">
                        <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search nodes..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-8 w-[200px]"
                        />
                    </div>
                </div>
            </div>

            <div className="flex flex-1 gap-4 overflow-hidden">
                {/* Graph Canvas */}
                <Card className="flex-1 overflow-hidden relative border-border" ref={setContainerRef}>
                    <div className="absolute top-4 left-4 z-10 flex flex-col gap-2 pointer-events-none">
                        <Badge className="bg-red-500 pointer-events-auto">Work Items ({graphData.stats.by_type.work_item})</Badge>
                        <Badge className="bg-green-500 pointer-events-auto">Services ({graphData.stats.by_type.service})</Badge>
                        <Badge className="bg-blue-500 pointer-events-auto">Humans ({graphData.stats.by_type.human})</Badge>
                        {graphData.stats.by_type.decision > 0 && (
                            <Badge className="bg-purple-500 pointer-events-auto">Decisions ({graphData.stats.by_type.decision})</Badge>
                        )}
                    </div>

                    <div className="absolute bottom-4 right-4 z-10 flex flex-col gap-2">
                        <Button size="icon" variant="secondary" title="Zoom In">
                            <ZoomIn className="h-4 w-4" />
                        </Button>
                        <Button size="icon" variant="secondary" title="Zoom Out">
                            <ZoomOut className="h-4 w-4" />
                        </Button>
                        <Button size="icon" variant="secondary" title="Reset View">
                            <Maximize className="h-4 w-4" />
                        </Button>
                    </div>

                    {filteredData.nodes.length === 0 ? (
                        <div className="h-full grid place-items-center">
                            <div className="text-center space-y-2">
                                <p className="text-muted-foreground">No nodes match your filters</p>
                                <Button variant="outline" onClick={() => {
                                    setNodeTypeFilter('all');
                                    setServiceFilter('all');
                                    setSearchQuery('');
                                }}>
                                    Clear Filters
                                </Button>
                            </div>
                        </div>
                    ) : (
                    <ForceGraph3D
                        width={dimensions.width}
                        height={dimensions.height}
                            graphData={filteredData}
                            nodeLabel={(node: any) => node.name || node.id}
                            nodeColor={(node: any) => node.color || '#888'}
                            nodeVal={(node: any) => node.val || 5}
                            linkColor={() => 'rgba(255,255,255,0.2)'}
                            linkWidth={1}
                            backgroundColor="rgba(0,0,0,0)"
                        showNavInfo={false}
                            onNodeClick={handleNodeClick}
                    />
                    )}
                </Card>

                {/* Node Details Sidebar */}
                <Card className="w-80 h-full overflow-y-auto hidden lg:block">
                    <CardHeader>
                        <CardTitle className="text-sm uppercase text-muted-foreground">Selected Node</CardTitle>
                    </CardHeader>
                    <CardContent>
                        {selectedNode ? (
                            <div className="space-y-4">
                                <div className="h-12 w-12 rounded-full grid place-items-center font-bold mx-auto mb-4"
                                     style={{ backgroundColor: `${selectedNode.color}20`, color: selectedNode.color }}>
                                    {selectedNode.type === 'work_item' ? 'WI' : 
                                     selectedNode.type === 'human' ? 'H' : 
                                     selectedNode.type === 'decision' ? 'D' : 'N'}
                                </div>
                                <h3 className="text-xl font-bold text-center">{selectedNode.name}</h3>
                                <div className="text-center text-sm text-muted-foreground mb-6">
                                    {selectedNode.type}
                                </div>

                                <div className="space-y-4">
                                    <div className="text-sm">
                                        <span className="font-semibold block mb-2">ID</span>
                                        <code className="text-xs bg-muted px-2 py-1 rounded">{selectedNode.id}</code>
                                    </div>

                                    {selectedNode.metadata && (
                                        <div className="text-sm space-y-2">
                                            <span className="font-semibold block">Metadata</span>
                                            {selectedNode.metadata.service && (
                                                <div>
                                                    <span className="text-muted-foreground">Service: </span>
                                                    <span>{selectedNode.metadata.service}</span>
                                                </div>
                                            )}
                                            {selectedNode.metadata.severity && (
                                                <div>
                                                    <span className="text-muted-foreground">Severity: </span>
                                                    <Badge variant="outline">{selectedNode.metadata.severity}</Badge>
                                                </div>
                                            )}
                                            {selectedNode.metadata.display_name && (
                                                <div>
                                                    <span className="text-muted-foreground">Name: </span>
                                                    <span>{selectedNode.metadata.display_name}</span>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                <div className="text-sm">
                                        <span className="font-semibold block mb-2">Connections</span>
                                        <p className="text-muted-foreground text-xs">
                                            {filteredData.links.filter(l => 
                                                l.source === selectedNode.id || l.target === selectedNode.id
                                            ).length} edges
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="text-center py-10 text-muted-foreground italic text-sm">
                                Click a node in the graph to view details.
                        </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
