from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests=5, time_window=5):
        # max_requests per time_window seconds
        self.max_requests = max_requests
        self.time_window = time_window  # in seconds
        self.request_history = defaultdict(list)
        
    def is_rate_limited(self, user_id):
        current_time = time.time()
        # Remove old requests
        self.request_history[user_id] = [
            timestamp for timestamp in self.request_history[user_id]
            if current_time - timestamp < self.time_window
        ]
        
        # Check if user has exceeded the limit
        if len(self.request_history[user_id]) >= self.max_requests:
            return True
        
        # Add current request
        self.request_history[user_id].append(current_time)
        return False