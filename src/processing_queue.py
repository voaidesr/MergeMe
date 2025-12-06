from dataclasses import dataclass, field
from typing import DefaultDict, Dict, List, Mapping, Optional
from collections import defaultdict

from inventory import CLASS_KEYS, InventoryManager


@dataclass
class ProcessingEntry:
    hours_remaining: int
    amount: int


@dataclass
class KitProcessingQueue:
    """
    Tracks kits in processing per airport/class and releases them into inventory when done.
    """
    queue: Dict[str, Dict[str, List[ProcessingEntry]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(list))
    )

    def add_batch(
        self,
        airport_code: str,
        amounts: Mapping[str, int],
        processing_times: Mapping[str, int],
    ) -> None:
        """
        Enqueue arriving kits by class with their processing time (in hours).
        processing_times keys match CLASS_KEYS.
        """
        airport_queue = self.queue[airport_code]
        for kit_class in CLASS_KEYS:
            amt = amounts.get(kit_class, 0)
            if amt <= 0:
                continue
            hours = processing_times.get(kit_class)
            if hours is None:
                continue
            airport_queue[kit_class].append(ProcessingEntry(hours_remaining=int(hours), amount=int(amt)))

    def tick(self, hours: int = 1) -> Dict[str, Dict[str, int]]:
        """
        Advance time and return kits that finished processing this tick.
        """
        ready: Dict[str, Dict[str, int]] = {}
        to_delete_airports: List[str] = []

        for airport_code, per_class in self.queue.items():
            finished_here: Dict[str, int] = {}
            to_delete_classes: List[str] = []
            for kit_class, entries in per_class.items():
                remaining_entries: List[ProcessingEntry] = []
                for entry in entries:
                    entry.hours_remaining -= hours
                    if entry.hours_remaining <= 0:
                        finished_here[kit_class] = finished_here.get(kit_class, 0) + entry.amount
                    else:
                        remaining_entries.append(entry)
                if remaining_entries:
                    per_class[kit_class] = remaining_entries
                else:
                    to_delete_classes.append(kit_class)

            for cls in to_delete_classes:
                per_class.pop(cls, None)

            if finished_here:
                ready[airport_code] = finished_here
            if not per_class:
                to_delete_airports.append(airport_code)

        for airport_code in to_delete_airports:
            self.queue.pop(airport_code, None)

        return ready

    def apply_tick(
        self, inventory_manager: InventoryManager, hours: int = 1
    ) -> Dict[str, Dict[str, int]]:
        """
        Advance time, apply finished kits to inventory, and return violations (if any).
        """
        finished = self.tick(hours=hours)
        if not finished:
            return {}
        violations = inventory_manager.apply_movements(
            {airport: {cls: amt for cls, amt in per_class.items()} for airport, per_class in finished.items()}
        )
        return violations
