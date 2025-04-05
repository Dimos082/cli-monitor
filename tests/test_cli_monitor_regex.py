import subprocess

def test_regex_trigger():
    """Should detect 'ERROR' and run the triggered command."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo ERROR OCCURRED",
        "--regex", "ERROR",
        "--regex-execute", "echo 'Trigger ran!'",
        "--timer", "2"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert "ERROR OCCURRED" in result.stdout      # Main command output
    assert "Trigger ran!" in result.stdout        # Triggered command output

def test_no_regex_no_trigger():
    """No triggered command should run if no regex is provided."""
    cmd = [
        "python", "cli_monitor.py",
        "--command", "echo Hello Again",
        "--timer", "2"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    assert "Hello Again" in result.stdout
    # Ensure we DON'T see "Trigger ran!"
    assert "Trigger ran!" not in result.stdout
