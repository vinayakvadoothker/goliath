import { StatCard } from "@/components/dashboard/StatCard";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";

export default function StatsPage() {
    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Stats & Capabilities</h1>
                <p className="text-muted-foreground">Human capability modeling and performance tracking.</p>
            </div>

            <Tabs defaultValue="overview" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="engineers">Engineers</TabsTrigger>
                    <TabsTrigger value="model">Model Accuracy</TabsTrigger>
                </TabsList>

                <TabsContent value="overview" className="space-y-4">
                    {/* High Level Stats */}
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                        <StatCard label="Active Engineers" value="18" color="blue" />
                        <StatCard label="Model Confidence" value="89%" trend="up" trendValue="+2% this month" color="purple" />
                        <StatCard label="Tasks Assigned" value="450" unit="/mo" trend="up" trendValue="+12%" />
                        <StatCard label="Override Rate" value="4.2%" trend="down" trendValue="-1.1% (Good)" color="green" />
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <CardTitle>Skill Distribution</CardTitle>
                                <CardDescription>Aggregate capability scores across the team</CardDescription>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                {[
                                    { skill: "Kubernetes", score: 85 },
                                    { skill: "Python/Django", score: 92 },
                                    { skill: "React/Frontend", score: 65 },
                                    { skill: "Database Optimization", score: 78 },
                                ].map(s => (
                                    <div key={s.skill} className="space-y-1">
                                        <div className="flex justify-between text-sm">
                                            <span>{s.skill}</span>
                                            <span className="font-mono text-muted-foreground">{s.score}/100</span>
                                        </div>
                                        <Progress value={s.score} className="h-2" />
                                    </div>
                                ))}
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Top Contributors</CardTitle>
                                <CardDescription>Most active responders this month</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {[
                                        { name: "Sarah Engineer", role: "Sr. SRE", handled: 42, avatar: "SE" },
                                        { name: "Mike Dev", role: "Backend Lead", handled: 35, avatar: "MD" },
                                        { name: "Jane Doe", role: "DevOps", handled: 28, avatar: "JD" },
                                    ].map((p, i) => (
                                        <div key={i} className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <Avatar>
                                                    <AvatarFallback>{p.avatar}</AvatarFallback>
                                                </Avatar>
                                                <div>
                                                    <div className="font-medium text-sm">{p.name}</div>
                                                    <div className="text-xs text-muted-foreground">{p.role}</div>
                                                </div>
                                            </div>
                                            <div className="text-sm font-bold">{p.handled} Items</div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                </TabsContent>

                <TabsContent value="engineers">
                    <div className="grid md:grid-cols-3 gap-6">
                        {/* Engineer Cards */}
                        {[1, 2, 3, 4, 5, 6].map(i => (
                            <Card key={i}>
                                <CardContent className="pt-6">
                                    <div className="flex items-center gap-4 mb-4">
                                        <Avatar className="h-12 w-12">
                                            <AvatarFallback>EN</AvatarFallback>
                                        </Avatar>
                                        <div>
                                            <div className="font-bold">Engineer #{i}</div>
                                            <Badge variant="outline" className="text-xs">Frontend Squad</Badge>
                                        </div>
                                    </div>

                                    <div className="space-y-2 text-sm">
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Cognitive Load</span>
                                            <span className="text-green-500 font-medium">Low (20%)</span>
                                        </div>
                                        <div className="flex justify-between">
                                            <span className="text-muted-foreground">Focus Area</span>
                                            <span>UI/UX</span>
                                        </div>
                                    </div>

                                    <div className="mt-4 pt-4 border-t">
                                        <h4 className="text-xs font-semibold mb-2">Recent Work</h4>
                                        <div className="flex flex-wrap gap-1">
                                            <Badge variant="secondary" className="text-[10px]">WI-3920</Badge>
                                            <Badge variant="secondary" className="text-[10px]">WI-3112</Badge>
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </TabsContent>
            </Tabs>
        </div>
    );
}
