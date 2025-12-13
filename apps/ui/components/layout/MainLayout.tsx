"use client";

import { useState } from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { cn } from '@/lib/utils';

interface MainLayoutProps {
    children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <div className="min-h-screen font-sans bg-background text-foreground transition-colors duration-500">
            <Navbar />
            <div className="flex h-[calc(100vh-65px)]">
                <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
                <main className={cn(
                    "flex-1 overflow-auto bg-[#0a0a0a] transition-all duration-300",
                    collapsed ? "ml-[60px]" : "ml-0" // Sidebar handles its own width, we just need to ensure flow is correct. Actually flex will handle it.
                )}>
                    <div className="container mx-auto max-w-7xl p-6">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
