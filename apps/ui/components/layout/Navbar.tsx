'use client';

import Link from 'next/link';

export function Navbar() {
    return (
        <nav className="bg-background px-6 py-4 border-b border-border">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-6">
                    <Link href="/" className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
                        <span className="h-8 w-8 rounded bg-primary flex items-center justify-center text-primary-foreground font-bold">G</span>
                        Goliath
                    </Link>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-background text-xs font-mono text-muted-foreground select-none">
                        <div className="h-2 w-2 rounded-full animate-pulse bg-green-500"></div>
                        SYSTEM ONLINE
                    </div>
                </div>
            </div>
        </nav>
    );
}
