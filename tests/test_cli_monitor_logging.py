import subprocess
import os
import pytest

@pytest.fixture
def log_file():
    log_file = "test_log_output.txt"
    # Remove log file if it exists
    if os.path.exists(log_file):
        os.remove(log_file)
    yield log_file
    # Clean up log file
    if os.path.exists(log_file):
        os.remove(log_file)

def test_log_pruning(log_file):
    """Check that log file pruning occurs once it exceeds max size."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo TestLogLine",
        "--output-file", log_file,
        "--max-log-size", "1",  # 1KB to force quick pruning
        "--timer", "3"          # run a few iterations
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    # We expect the log file to exist, but be under or ~1KB
    assert os.path.exists(log_file)
    file_size = os.path.getsize(log_file)
    assert file_size <= 1024, "Log file should be pruned to <= 1KB"