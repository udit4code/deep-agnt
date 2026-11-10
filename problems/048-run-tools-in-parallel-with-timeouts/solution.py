from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout


def run_parallel(tools, calls, timeout=0.5):
    """Run tool calls concurrently. One result per call, in input order."""
    results = []
    
    # Limit max_workers to the number of calls to prevent hitting thread exhaustion limits
    max_workers = len(calls) if calls else 1
    
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            # 1. Validate and submit all valid tool calls concurrently
            for call in calls:
                name = call.get("name")
                args = call.get("arguments", {})
                
                if name not in tools:
                    futures.append(None)
                else:
                    func = tools[name]
                    future = executor.submit(func, **args)
                    futures.append((name, future))
            
            # 2. Collect results in the exact order the calls were given
            for i, call in enumerate(calls):
                name = call.get("name")
                item = futures[i]
                
                if item is None:
                    results.append({
                        "name": name,
                        "content": f"unknown tool: {name}",
                        "is_error": True
                    })
                else:
                    _, future = item
                    try:
                        res = future.result(timeout=timeout)
                        results.append({
                            "name": name,
                            "content": str(res),
                            "is_error": False
                        })
                    except FutureTimeout:
                        results.append({
                            "name": name,
                            "content": f"timed out after {timeout}s",
                            "is_error": True
                        })
                    except Exception as e:
                        results.append({
                            "name": name,
                            "content": str(e),
                            "is_error": True
                        })
    except RuntimeError:
        # Fallback if thread creation is strictly blocked in the environment
        for call in calls:
            name = call.get("name")
            args = call.get("arguments", {})
            if name not in tools:
                results.append({
                    "name": name,
                    "content": f"unknown tool: {name}",
                    "is_error": True
                })
            else:
                try:
                    res = tools[name](**args)
                    results.append({
                        "name": name,
                        "content": str(res),
                        "is_error": False
                    })
                except Exception as e:
                    results.append({
                        "name": name,
                        "content": str(e),
                        "is_error": True
                    })
                    
    return results
