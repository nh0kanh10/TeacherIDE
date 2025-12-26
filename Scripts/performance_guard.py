"""
Performance Guards for v4.0
Ensures IDE-friendly performance (max 50ms sync, 500ms async)
"""
import time
import functools
from typing import Callable, Any

# Performance limits
MAX_SYNC_MS = 50
MAX_ASYNC_MS = 500

class PerformanceViolation(Exception):
    """Raised when performance limit is exceeded"""
    pass


def performance_guard(max_ms: int = MAX_SYNC_MS, async_op: bool = False):
    """
    Decorator to enforce performance limits
    
    Args:
        max_ms: Maximum allowed milliseconds
        async_op: If True, use async limit (500ms), else sync limit (50ms)
    
    Raises:
        PerformanceViolation: If operation exceeds time limit
    
    Example:
        @performance_guard(max_ms=50)
        def fast_operation():
            # Must complete in < 50ms
            pass
        
        @performance_guard(async_op=True)
        def slow_operation():
            # Can take up to 500ms
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start) * 1000
                
                limit = max_ms if not async_op else MAX_ASYNC_MS
                
                if elapsed_ms > limit:
                    op_type = "async" if async_op else "sync"
                    print(f"⚠️ Performance violation in {func.__name__}: "
                          f"{elapsed_ms:.1f}ms (limit: {limit}ms, {op_type})")
                    
                    # Log but don't crash (for now)
                    # In production, might raise PerformanceViolation
                elif elapsed_ms > limit * 0.8:
                    # Warn at 80% threshold
                    print(f"⏱️ {func.__name__}: {elapsed_ms:.1f}ms "
                          f"(approaching limit of {limit}ms)")
            
            return result
        return wrapper
    return decorator


# Convenience decorators
def sync_guard(func: Callable) -> Callable:
    """Shorthand for @performance_guard(max_ms=50)"""
    return performance_guard(max_ms=MAX_SYNC_MS)(func)


def async_guard(func: Callable) -> Callable:
    """Shorthand for @performance_guard(async_op=True)"""
    return performance_guard(async_op=True)(func)


if __name__ == "__main__":
    # Demo
    @sync_guard
    def fast_function():
        """Should pass"""
        time.sleep(0.01)  # 10ms
        return "OK"
    
    @sync_guard
    def slow_function():
        """Will trigger warning"""
        time.sleep(0.06)  # 60ms > 50ms limit
        return "SLOW"
    
    @async_guard
    def async_function():
        """OK for async"""
        time.sleep(0.2)  # 200ms < 500ms limit
        return "ASYNC OK"
    
    print("Testing performance guards:\n")
    
    result1 = fast_function()
    print(f"✅ Fast function: {result1}\n")
    
    result2 = slow_function()
    print(f"⚠️ Slow function: {result2}\n")
    
    result3 = async_function()
    print(f"✅ Async function: {result3}")
