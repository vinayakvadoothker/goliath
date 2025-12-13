import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

export function Navbar() {
    return (
        <nav className="bg-background px-6 py-4 border-b border-border">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-6">
                    <Link href="/" className="text-xl font-bold tracking-tight text-foreground flex items-center gap-2">
                        <img src="/logo.png" alt="Centra Logo" className="h-8 w-8" />
                        Centra
                    </Link>
                    <div className="hidden md:flex gap-6">
                        {/* Navigation moved to Sidebar */}
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-background text-xs font-mono text-muted-foreground select-none">
                        <div className="h-2 w-2 rounded-full animate-pulse bg-green-500"></div>
                        SYSTEM ONLINE
                    </div>
                    <div className="flex gap-2">
                        <Button variant="ghost" size="icon">
                            <span className="sr-only">Notifications</span>
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" /><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" /></svg>
                        </Button>
                        <Avatar className="h-8 w-8">
                            <AvatarImage src="/avatars/01.png" alt="@shadcn" />
                            <AvatarFallback>AD</AvatarFallback>
                        </Avatar>
                    </div>
                </div>
            </div>
        </nav>
    );
}
