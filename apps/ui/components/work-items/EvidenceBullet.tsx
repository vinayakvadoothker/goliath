import { CheckCircle, Clock, Activity, TrendingUp, AlertTriangle } from "lucide-react";

interface EvidenceBulletProps {
    type: 'recent_resolution' | 'on_call' | 'low_load' | 'similar_incident' | 'fit_score';
    text: string;
    timeWindow?: string;
    source?: string;
}

export function EvidenceBullet({ type, text, timeWindow, source }: EvidenceBulletProps) {
    const iconMap = {
        recent_resolution: CheckCircle,
        on_call: Clock,
        low_load: Activity,
        similar_incident: AlertTriangle,
        fit_score: TrendingUp,
    };

    const Icon = iconMap[type] || Activity;

    return (
        <div className="flex items-start gap-3 p-2 rounded-md hover:bg-muted/50 transition-colors">
            <div className="mt-0.5 text-blue-500">
                <Icon className="h-4 w-4" />
            </div>
            <div className="flex-1">
                <p className="text-sm text-foreground">
                    {text}
                    {timeWindow && <span className="ml-1 px-1.5 py-0.5 rounded bg-muted text-muted-foreground text-xs">{timeWindow}</span>}
                </p>
                {source && <p className="text-xs text-muted-foreground mt-0.5">Source: {source}</p>}
            </div>
        </div>
    );
}
