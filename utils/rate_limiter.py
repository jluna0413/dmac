"""
Rate limiting utilities for DMac.

This module provides rate limiting functionality to prevent abuse.
"""

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from utils.secure_logging import get_logger

logger = get_logger('dmac.utils.rate_limiter')


class RateLimiter:
    """Rate limiter for API endpoints."""
    
    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window.
            time_window: Time window in seconds.
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_timestamps: Dict[str, Deque[float]] = defaultdict(deque)
    
    async def check_rate_limit(self, client_id: str) -> bool:
        """Check if a client has exceeded the rate limit.
        
        Args:
            client_id: The client identifier (e.g., IP address).
            
        Returns:
            True if the client is within the rate limit, False otherwise.
        """
        current_time = time.time()
        
        # Remove timestamps outside the time window
        while (self.request_timestamps[client_id] and 
               current_time - self.request_timestamps[client_id][0] > self.time_window):
            self.request_timestamps[client_id].popleft()
        
        # Check if client has exceeded the rate limit
        if len(self.request_timestamps[client_id]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            return False
        
        # Add current timestamp
        self.request_timestamps[client_id].append(current_time)
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get the number of remaining requests for a client.
        
        Args:
            client_id: The client identifier (e.g., IP address).
            
        Returns:
            The number of remaining requests.
        """
        current_time = time.time()
        
        # Remove timestamps outside the time window
        while (self.request_timestamps[client_id] and 
               current_time - self.request_timestamps[client_id][0] > self.time_window):
            self.request_timestamps[client_id].popleft()
        
        return max(0, self.max_requests - len(self.request_timestamps[client_id]))
    
    def get_reset_time(self, client_id: str) -> Optional[float]:
        """Get the time when the rate limit will reset for a client.
        
        Args:
            client_id: The client identifier (e.g., IP address).
            
        Returns:
            The time when the rate limit will reset, or None if the client has not made any requests.
        """
        if not self.request_timestamps[client_id]:
            return None
        
        oldest_timestamp = self.request_timestamps[client_id][0]
        return oldest_timestamp + self.time_window


class TokenBucket:
    """Token bucket rate limiter.
    
    This implementation uses a token bucket algorithm, which is more flexible
    than a simple request counter. It allows for bursts of traffic while
    maintaining a long-term rate limit.
    """
    
    def __init__(self, capacity: int = 100, refill_rate: float = 1.0):
        """Initialize the token bucket.
        
        Args:
            capacity: The maximum number of tokens in the bucket.
            refill_rate: The number of tokens added to the bucket per second.
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {'tokens': capacity, 'last_refill': time.time()}
        )
    
    def _refill(self, client_id: str) -> None:
        """Refill the token bucket for a client.
        
        Args:
            client_id: The client identifier (e.g., IP address).
        """
        now = time.time()
        bucket = self.buckets[client_id]
        
        # Calculate time since last refill
        time_passed = now - bucket['last_refill']
        
        # Calculate tokens to add
        tokens_to_add = time_passed * self.refill_rate
        
        # Update bucket
        bucket['tokens'] = min(self.capacity, bucket['tokens'] + tokens_to_add)
        bucket['last_refill'] = now
    
    async def consume(self, client_id: str, tokens: int = 1) -> bool:
        """Consume tokens from the bucket.
        
        Args:
            client_id: The client identifier (e.g., IP address).
            tokens: The number of tokens to consume.
            
        Returns:
            True if tokens were consumed successfully, False otherwise.
        """
        # Refill the bucket
        self._refill(client_id)
        
        # Check if there are enough tokens
        if self.buckets[client_id]['tokens'] < tokens:
            logger.warning(f"Token bucket limit exceeded for client: {client_id}")
            return False
        
        # Consume tokens
        self.buckets[client_id]['tokens'] -= tokens
        return True
    
    def get_tokens(self, client_id: str) -> float:
        """Get the number of tokens in the bucket for a client.
        
        Args:
            client_id: The client identifier (e.g., IP address).
            
        Returns:
            The number of tokens in the bucket.
        """
        # Refill the bucket
        self._refill(client_id)
        
        return self.buckets[client_id]['tokens']


# Create singleton instances
request_rate_limiter = RateLimiter()
model_token_bucket = TokenBucket(capacity=1000, refill_rate=10.0)  # 10 tokens per second, max 1000
