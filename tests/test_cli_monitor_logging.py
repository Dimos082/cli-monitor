import subprocess
import os
import pytest

@pytest.fixture
def log_file():
    """Fixture to create and clean up a log file."""
    log_file = "test_log_output.txt"
    if os.path.exists(log_file):
        os.remove(log_file)
    yield log_file
    if os.path.exists(log_file):
        os.remove(log_file)

def test_log_creation(log_file):
    """Verify that the log file is created and contains expected content."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo Log Test",
        "--output-file", log_file,
        "--timer", "1"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(log_file)
    with open(log_file, "r") as f:
        log_content = f.read()
    assert "Log Test" in log_content

def test_log_pruning_behavior(log_file):
    """Verify that the log file is pruned when it exceeds the max size."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo Prune Test",
        "--output-file", log_file,
        "--max-log-size", "1",  # 1KB
        "--timer", "3"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(log_file)
    file_size = os.path.getsize(log_file)
    assert file_size <= 1024, "Log file should be pruned to <= 1KB"