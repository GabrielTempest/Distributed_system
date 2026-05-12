"""
Verify acks=all, manual commit, and error classification configs are correct.
"""
from datetime import datetime, timezone, timedelta
from services.error_handler.error_classifier import SensorErrorClassifier

def test_producer_acks_all():
    """Verify producer config has acks=all in source code"""
    # Inspect kafka_client.py to verify acks=all is set
    with open("common/kafka_client.py", "r") as f:
        source = f.read()
        assert '"acks": "all"' in source, "Producer config must include \"acks\": \"all\""
    print("Producer: acks=all is configured")

def test_consumer_auto_commit():
    """Verify default consumer uses auto-commit (for non-error-handler services)"""
    # Inspect kafka_client.py to verify auto-commit is enabled
    with open("common/kafka_client.py", "r") as f:
        source = f.read()
        assert '"enable.auto.commit": True' in source, "Consumer config must have enable.auto.commit: True"
    print("Consumer (anomaly_detector/alert_service/database_writer): auto-commit enabled")

def test_error_handler_manual_commit():
    """Verify error_handler consumer has manual commit disabled"""
    # Inspect consumer_config.py to verify manual commit
    with open("services/error_handler/consumer_config.py", "r") as f:
        source = f.read()
        assert "'enable.auto.commit': False" in source, "Error handler consumer must have enable.auto.commit: False"
    # Verify consumer_loop.py calls commit explicitly
    with open("services/error_handler/consumer_loop.py", "r") as f:
        source = f.read()
        assert "consumer.commit" in source, "consumer_loop.py must call consumer.commit()"
    print("Consumer (error_handler): manual commit configured (enable.auto.commit=False)")


def test_error_classification():
    """Verify error classifier detects all three error types"""
    classifier = SensorErrorClassifier()
    
    # Test bad_data: null value
    bad_null = {"sensor_id": "s1", "area_id": "a1", "value": None, "timestamp": datetime.now(timezone.utc).isoformat()}
    assert classifier.classify(bad_null) == "bad_data", "Failed to detect null value as bad_data"
    print("Bad data (null value) detected")
    
    # Test bad_data: out of range
    bad_range = {"sensor_id": "s1", "area_id": "a1", "value": 150, "timestamp": datetime.now(timezone.utc).isoformat()}
    assert classifier.classify(bad_range) == "bad_data", "Failed to detect out-of-range value as bad_data"
    print("Bad data (out of range) detected")
    
    # Test offline: old timestamp
    old_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    offline = {"sensor_id": "s1", "area_id": "a1", "value": 50, "timestamp": old_time}
    assert classifier.classify(offline) == "offline", "Failed to detect old timestamp as offline"
    print("Offline (old timestamp > 5 min) detected")
    
    # Test network: missing required fields
    network = {"sensor_id": "s1", "area_id": "a1"}  # missing value and timestamp
    assert classifier.classify(network) == "network", "Failed to detect missing fields as network"
    print("Network (missing fields) detected")
    
    # Test good reading
    good = {"sensor_id": "s1", "area_id": "a1", "value": 50, "timestamp": datetime.now(timezone.utc).isoformat()}
    assert classifier.classify(good) is None, "Failed: good reading should return None"
    print("Good reading passes classification")

if __name__ == "__main__":
    print("\n=== Config Verification Tests ===\n")
    try:
        test_producer_acks_all()
        test_consumer_auto_commit()
        test_error_handler_manual_commit()
        test_error_classification()
        print("\n All configs verified correctly!")
    except AssertionError as e:
        print(f"\n✗ Verification failed: {e}")
        exit(1)
