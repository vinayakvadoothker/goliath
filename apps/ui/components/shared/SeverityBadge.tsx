import { Badge } from "@/components/ui/badge";

interface SeverityBadgeProps {
    severity: "sev1" | "sev2" | "sev3" | "sev4";
}

export function SeverityBadge({ severity }: SeverityBadgeProps) {
    const variant =
        severity === "sev1" ? "destructive" :
            severity === "sev2" ? "warning" : // Using our custom 'warning' variant which maps to 'outcome' (Amber)
                severity === "sev3" ? "secondary" :
                    "outline";

    return (
        <Badge variant={variant} className="uppercase">
            {severity}
        </Badge>
    );
}
