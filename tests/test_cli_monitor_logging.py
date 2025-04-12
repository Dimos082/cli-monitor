import subprocess
import os
import pytest

@pytest.fixture
def log_file():
    """Fixture to create and clean up a log file."""
    log_path = "test_log_output.txt"
    if os.path.exists(log_path):
        os.remove(log_path)
    yield log_path
    if os.path.exists(log_path):
        os.remove(log_path)

@pytest.mark.parametrize("message", ["Log Test", "Another Log Line"])
def test_log_creation_and_content(log_file, message):
    """Verify that log file is created and contains expected output."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", f"echo {message}",
        "--output-file", log_file,
        "--timer", "1"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(log_file)
    with open(log_file, "r") as f:
        content = f.read()
    assert message in content

@pytest.mark.parametrize("max_size", [1, 2])  # KB
def test_log_pruning_behavior(log_file, max_size):
    """Check log pruning under small max-log-size."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo Prune Test Line",
        "--output-file", log_file,
        "--max-log-size", str(max_size),
        "--timer", "3"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert os.path.exists(log_file)
    assert os.path.getsize(log_file) <= max_size * 1024