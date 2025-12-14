"use client";

import { useState } from 'react';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { usePathname } from 'next/navigation';

interface MainLayoutProps {
    children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
    const [collapsed, setCollapsed] = useState(false);
    const pathname = usePathname();
    const isPublicPage = pathname === '/' || 
        pathname?.startsWith('/landing') || 
        pathname?.startsWith('/login') ||
        pathname?.startsWith('/sign-in') ||
        pathname?.startsWith('/sign-up') ||
        pathname?.startsWith('/signin');

    if (isPublicPage) {
        return <>{children}</>;
    }

    return (
        <div className="min-h-screen font-sans bg-background text-foreground transition-colors duration-500">
            <Navbar />
            <div className="flex h-[calc(100vh-65px)]">
                <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
                <main className="flex-1 overflow-auto bg-background transition-all duration-300">
                    <div className="container mx-auto max-w-7xl p-6">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
