import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label"; // Wait, I didn't create Label yet manually. I installed @radix-ui/react-label. I need to create the wrapper.
import { useState } from "react";

// Inline Label for now or create it? Better to use standard label HTML or create Label component quickly.
// I'll create Label component in the same step or inline.
// Let's rely on standard label class or create a simple Label component here if needed.
// Actually standard shadcn Label uses @radix-ui/react-label.
// I'll just use a styled label element here for speed.

interface OverrideModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: any) => void;
    currentAssignee: string;
}

export function OverrideModal({ isOpen, onClose, onSubmit, currentAssignee }: OverrideModalProps) {
    const [reason, setReason] = useState("");
    const [newAssignee, setNewAssignee] = useState("");

    const handleSubmit = () => {
        onSubmit({ reason, newAssignee });
        onClose();
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Override Decision</DialogTitle>
                    <DialogDescription>
                        Manually assign this work item. This action will be logged and used for training.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="grid gap-2">
                        <label htmlFor="assignee" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            New Assignee
                        </label>
                        <Select onValueChange={setNewAssignee} value={newAssignee}>
                            <SelectTrigger id="assignee">
                                <SelectValue placeholder="Select person..." />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="sarah-engineer">Sarah Engineering (On-Call)</SelectItem>
                                <SelectItem value="mike-dev">Mike Developer</SelectItem>
                                <SelectItem value="jane-sre">Jane SRE</SelectItem>
                                <SelectItem value={currentAssignee} disabled>{currentAssignee} (Current)</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="grid gap-2">
                        <label htmlFor="reason" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                            Reason for Override
                        </label>
                        <Textarea
                            id="reason"
                            placeholder="Why is the AI suggestion incorrect? Be specific."
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
                        />
                    </div>
                </div>
                <DialogFooter>
                    <Button variant="outline" onClick={onClose}>Cancel</Button>
                    <Button onClick={handleSubmit} disabled={!reason || !newAssignee}>Confirm Override</Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
