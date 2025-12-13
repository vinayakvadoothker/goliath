import { Card, CardContent } from "@/components/ui/card";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";

interface StatCardProps {
    label: string;
    value: string | number;
    trend?: "up" | "down";
    trendValue?: string;
    color?: "blue" | "green" | "red" | "purple" | "default";
    unit?: string;
}

export function StatCard({ label, value, trend, trendValue, color = "default", unit }: StatCardProps) {
    const colorMap = {
        default: "text-foreground",
        blue: "text-blue-500",
        green: "text-green-500",
        red: "text-red-500",
        purple: "text-purple-500",
    };

    return (
        <Card>
            <CardContent className="p-6">
                <div className="text-sm font-medium text-muted-foreground">{label}</div>
                <div className="mt-2 flex items-baseline gap-2">
                    <span className={`text-2xl font-bold ${colorMap[color]}`}>
                        {value}
                    </span>
                    {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
                </div>
                {trendValue && (
                    <div className={`mt-1 flex items-center text-xs ${trend === "up" ? "text-green-500" : "text-red-500"}`}>
                        {trend === "up" ? <ArrowUpRight className="mr-1 h-3 w-3" /> : <ArrowDownRight className="mr-1 h-3 w-3" />}
                        {trendValue}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
