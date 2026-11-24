import math 

def scale(metrics, state):
    """How many workers to run from this tick."""
    tick = metrics["tick"]
    queue_depth = metrics["queue_depth"]
    current = metrics["workers"]

    min_workers = CONFIG["min"]
    max_workers = CONFIG["max"]
    target = CONFIG["target_per_worker"]
    cooldown = CONFIG["cooldown"]

    # 1. Compute desired workers from queue depth, rounded up and clamped to [min, max].
    raw_desired = math.ceil(queue_depth / target) if queue_depth > 0 else min_workers
    desired = max(min_workers, min(max_workers, raw_desired))

    # 2. Scale up immediately to desired and record the tick of the scale-up.
    if desired > current:
        state["last_up"] = tick
        return desired

    # 3 & 4. Scale down only if no scale-up has occurred yet or cooldown has elapsed,
    # removing at most one worker per tick.
    if desired < current:
        last_up = state.get("last_up")
        cooldown_ready = last_up is None or (tick - last_up) >= cooldown
        if cooldown_ready:
            return max(desired, current - 1)

    # Hold current worker count if desired == current or still in cooldown.
    return current
