"use client";

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { LayoutDashboard, CheckSquare, Network, BarChart2, Plus, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
    collapsed: boolean;
    setCollapsed: (collapsed: boolean) => void;
}

export function Sidebar({ collapsed, setCollapsed }: SidebarProps) {
    return (
        <aside className={cn(
            "bg-card hidden lg:flex flex-col flex-shrink-0 transition-all duration-300 relative border-r border-border",
            collapsed ? "w-[60px]" : "w-64",
            "p-2"
        )}>
            <Button
                variant="ghost"
                size="icon"
                className="absolute -right-3 top-6 h-6 w-6 rounded-full border border-border bg-background z-20 hover:bg-muted"
                onClick={() => setCollapsed(!collapsed)}
            >
                {collapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
            </Button>

            <div className="flex-1 space-y-6 pt-4">
                <div>
                    {!collapsed && (
                        <h3 className="mb-2 px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider animate-in fade-in">
                            Navigation
                        </h3>
                    )}
                    <div className="space-y-1">
                        <Link href="/" className={cn("w-full", collapsed ? "flex justify-center" : "block")}>
                            <Button variant="ghost" size={collapsed ? "icon" : "default"} className={cn("gap-2", collapsed ? "" : "w-full justify-start")}>
                                <LayoutDashboard className="h-4 w-4" />
                                {!collapsed && <span>Dashboard</span>}
                            </Button>
                        </Link>
                        <Link href="/work-items" className={cn("w-full", collapsed ? "flex justify-center" : "block")}>
                            <Button variant="ghost" size={collapsed ? "icon" : "default"} className={cn("gap-2", collapsed ? "" : "w-full justify-start")}>
                                <CheckSquare className="h-4 w-4" />
                                {!collapsed && <span>Work Items</span>}
                            </Button>
                        </Link>
                        <Link href="/graph" className={cn("w-full", collapsed ? "flex justify-center" : "block")}>
                            <Button variant="ghost" size={collapsed ? "icon" : "default"} className={cn("gap-2", collapsed ? "" : "w-full justify-start")}>
                                <Network className="h-4 w-4" />
                                {!collapsed && <span>Graph</span>}
                            </Button>
                        </Link>
                        <Link href="/stats" className={cn("w-full", collapsed ? "flex justify-center" : "block")}>
                            <Button variant="ghost" size={collapsed ? "icon" : "default"} className={cn("gap-2", collapsed ? "" : "w-full justify-start")}>
                                <BarChart2 className="h-4 w-4" />
                                {!collapsed && <span>Stats</span>}
                            </Button>
                        </Link>
                    </div>
                </div>

                <div>
                    {!collapsed && (
                        <h3 className="mb-2 px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider animate-in fade-in">
                            Quick Actions
                        </h3>
                    )}
                    <Link href="/work-items/new" className={cn("w-full", collapsed ? "flex justify-center" : "block")}>
                        <Button className={cn("gap-2", collapsed ? "" : "w-full justify-start")} size={collapsed ? "icon" : "default"}>
                            <Plus className="h-4 w-4" />
                            {!collapsed && "New Item"}
                        </Button>
                    </Link>
                </div>
            </div>
        </aside>
    );
}
