from dataclasses import dataclass

@dataclass
class RetryMessage:
    retry_id: str
    original_topic: str     # which topic the message originally failed on
    payload: str            # JSON string of the original message
    error_reason: str       # what went wrong e.g. "DB_UNAVAILABLE", "NETWORK_TIMEOUT"
    attempt_count: int      # how many times it has been tried
    max_attempts: int       # after this → goes to DLQ
    timestamp: str