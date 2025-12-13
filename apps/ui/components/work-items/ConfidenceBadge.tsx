import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

interface ConfidenceBadgeProps {
    confidence: number; // 0-1
}

export function ConfidenceBadge({ confidence }: ConfidenceBadgeProps) {
    const percentage = Math.round(confidence * 100);

    const colorClass =
        confidence >= 0.7 ? "bg-green-500 text-green-950 border-green-500/20" :
            confidence >= 0.4 ? "bg-yellow-500 text-yellow-950 border-yellow-500/20" :
                "bg-red-500 text-red-950 border-red-500/20";

    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger>
                    <div className={`px-2.5 py-0.5 rounded-full text-xs font-bold border ${colorClass} bg-opacity-90`}>
                        {percentage}% Confidence
                    </div>
                </TooltipTrigger>
                <TooltipContent>
                    <p>Confidence based on top1-top2 score margin</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
}
