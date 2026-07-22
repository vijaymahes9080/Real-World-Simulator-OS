import heapq
from typing import Any, Dict, List, Callable, Optional, Tuple
from pydantic import BaseModel, Field

class Event(BaseModel):
    id: str
    time: float
    event_type: str
    target_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 10  # Lower values processed first if times are equal

    # Define comparison operators for heapq priority queue sorting
    def __lt__(self, other: "Event") -> bool:
        if self.time == other.time:
            return self.priority < other.priority
        return self.time < other.time

class DESQueue(BaseModel):
    id: str
    capacity: int = -1  # -1 for infinite
    items: List[str] = Field(default_factory=list)  # Entity IDs waiting in queue
    service_times: List[float] = Field(default_factory=list)
    utilization_history: List[Tuple[float, float]] = Field(default_factory=list)  # (time, level)

class DESSimulationState(BaseModel):
    current_time: float = 0.0
    variables: Dict[str, Any] = Field(default_factory=dict)
    queues: Dict[str, DESQueue] = Field(default_factory=dict)
    processed_events_count: int = 0
    history: List[Dict[str, Any]] = Field(default_factory=list)

class DESEngine:
    def __init__(self):
        self.event_queue: List[Event] = []
        self.handlers: Dict[str, Callable[[Event, DESSimulationState], List[Event]]] = {}

    def register_handler(self, event_type: str, handler: Callable[[Event, DESSimulationState], List[Event]]):
        """
        Registers a function to handle a specific event type.
        The handler returns a list of new events to schedule.
        """
        self.handlers[event_type] = handler

    def schedule_event(self, event: Event):
        heapq.heappush(self.event_queue, event)

    def initialize_simulation(self, initial_events: List[Event], initial_variables: Dict[str, Any]) -> DESSimulationState:
        self.event_queue = []
        for evt in initial_events:
            self.schedule_event(evt)
        return DESSimulationState(
            current_time=0.0,
            variables=initial_variables,
            queues={},
            processed_events_count=0,
            history=[]
        )

    def step(self, state: DESSimulationState) -> Tuple[DESSimulationState, Optional[Event]]:
        """
        Processes the next event in the queue.
        Returns the updated state and the processed event (or None if queue is empty).
        """
        if not self.event_queue:
            return state, None

        # Pop next event
        event = heapq.heappop(self.event_queue)
        
        # Advance time to event time
        state.current_time = event.time
        state.processed_events_count += 1

        # Retrieve handler
        handler = self.handlers.get(event.event_type)
        if handler:
            try:
                # Execute handler and get newly generated events
                new_events = handler(event, state)
                for new_evt in new_events:
                    self.schedule_event(new_evt)
            except Exception as e:
                # Log event processing failure in history
                state.history.append({
                    "time": state.current_time,
                    "event_id": event.id,
                    "event_type": event.event_type,
                    "error": str(e),
                    "status": "failed"
                })
                return state, event
        
        # Log successful event
        state.history.append({
            "time": state.current_time,
            "event_id": event.id,
            "event_type": event.event_type,
            "target": event.target_id,
            "payload": event.payload,
            "status": "success",
            "queue_sizes": {q_id: len(q.items) for q_id, q in state.queues.items()}
        })

        return state, event

    def run_until(self, state: DESSimulationState, max_time: float, max_events: int = 100000) -> DESSimulationState:
        """
        Runs the simulation loop until current_time exceeds max_time or the queue runs out.
        """
        events_run = 0
        while self.event_queue and state.current_time < max_time and events_run < max_events:
            state, _ = self.step(state)
            events_run += 1
        return state
