import { cn } from "@/lib/utils";

function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "animate-pulse-soft rounded-lg bg-muted/70 shadow-inner shadow-black/5",
        className,
      )}
    />
  );
}

export { Skeleton };
