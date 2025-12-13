"use client";

import dynamic from 'next/dynamic';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Search, ZoomIn, ZoomOut, Maximize, Filter } from "lucide-react";
import { useState, useEffect } from 'react';

// Dynamically import ForceGraph3D with no SSR to avoid window is not defined errors
const ForceGraph3D = dynamic(() => import('react-force-graph-3d'), {
    ssr: false,
    loading: () => <div className="h-[600px] w-full bg-muted/20 animate-pulse grid place-items-center">Loading 3D Engine...</div>
});

// Mock Graph Data
const gData = {
    nodes: [
        { id: 'WI-3921', group: 'work_item', val: 10, color: '#ef4444', name: 'Latency Spike' },
        { id: 'pager-bot', group: 'human', val: 8, color: '#3b82f6', name: 'Pager Bot' },
        { id: 'payments-api', group: 'service', val: 15, color: '#10b981', name: 'Payments API' },
        { id: 'database', group: 'service', val: 12, color: '#10b981', name: 'Primary DB' },
        { id: 'WI-3402', group: 'work_item', val: 7, color: '#ef4444', name: 'Old DB Issue' },
        { id: 'sarah-engineer', group: 'human', val: 8, color: '#3b82f6', name: 'Sarah (On-Call)' },
    ],
    links: [
        { source: 'WI-3921', target: 'payments-api' },
        { source: 'WI-3921', target: 'database' },
        { source: 'WI-3921', target: 'pager-bot' },
        { source: 'payments-api', target: 'database' },
        { source: 'WI-3402', target: 'database' },
        { source: 'sarah-engineer', target: 'payments-api' },
    ]
};

export default function GraphPage() {
    const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
    const [containerRef, setContainerRef] = useState<HTMLDivElement | null>(null);

    useEffect(() => {
        if (containerRef) {
            setDimensions({
                width: containerRef.clientWidth,
                height: containerRef.clientHeight
            });
        }

        // Resize observer could be added here
    }, [containerRef]);

    return (
        <div className="h-[calc(100vh-100px)] flex flex-col space-y-4 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Knowledge Graph</h1>
                    <p className="text-muted-foreground">Visualize relationships between people, work, and services.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline"><Filter className="mr-2 h-4 w-4" /> Filter Nodes</Button>
                    <Button><Search className="mr-2 h-4 w-4" /> Search Entity</Button>
                </div>
            </div>

            <div className="flex flex-1 gap-4 overflow-hidden">
                {/* Graph Canvas */}
                <Card className="flex-1 overflow-hidden relative border-border" ref={setContainerRef}>
                    <div className="absolute top-4 left-4 z-10 flex flex-col gap-2 pointer-events-none">
                        <Badge className="bg-red-500 pointer-events-auto">Work Items</Badge>
                        <Badge className="bg-green-500 pointer-events-auto">Services</Badge>
                        <Badge className="bg-blue-500 pointer-events-auto">Humans</Badge>
                    </div>

                    <div className="absolute bottom-4 right-4 z-10 flex flex-col gap-2">
                        <Button size="icon" variant="secondary"><ZoomIn className="h-4 w-4" /></Button>
                        <Button size="icon" variant="secondary"><ZoomOut className="h-4 w-4" /></Button>
                        <Button size="icon" variant="secondary"><Maximize className="h-4 w-4" /></Button>
                    </div>

                    <ForceGraph3D
                        width={dimensions.width}
                        height={dimensions.height}
                        graphData={gData}
                        nodeLabel="name"
                        nodeColor="color"
                        backgroundColor="rgba(0,0,0,0)" // Transparent to use Card bg
                        showNavInfo={false}
                    />
                </Card>

                {/* Node Details Sidebar */}
                <Card className="w-80 h-full overflow-y-auto hidden lg:block">
                    <CardHeader>
                        <CardTitle className="text-sm uppercase text-muted-foreground">Selected Node</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-center py-10 text-muted-foreground italic text-sm">
                            Click a node in the graph to view details.
                        </div>

                        {/* Mock Active State */}
                        <div className="hidden">
                            <div className="h-12 w-12 rounded-full bg-red-500/20 text-red-500 grid place-items-center font-bold mx-auto mb-4">WI</div>
                            <h3 className="text-xl font-bold text-center">WI-3921</h3>
                            <div className="text-center text-sm text-muted-foreground mb-6">Latency Spike</div>

                            <div className="space-y-4">
                                <div className="text-sm">
                                    <span className="font-semibold block">Connections</span>
                                    <ul className="list-disc pl-4 text-muted-foreground">
                                        <li>Payments API</li>
                                        <li>Pager Bot</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
