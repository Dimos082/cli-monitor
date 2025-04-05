import subprocess

def test_echo_command():
    """Verify 'echo Hello' runs without errors and prints 'Hello'."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo Hello",
        "--timer", "2"  # short run
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Hello" in result.stdout

def test_invalid_frequency():
    """Frequency outside allowed range should cause an error exit."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo Hello",
        "--frequency", "999999999"  # way too large
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Expecting a non-zero exit code due to frequency validation
    assert result.returncode != 0
    assert "Error: Frequency must be between" in result.stdout
