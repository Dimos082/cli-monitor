# CLI Monitor

> **CLI Monitor** is a *cross-platform* Python tool that repeatedly runs a command, captures its output, optionally logs it, and can even trigger a secondary command whenever a regex pattern is matched.

*Because repetitive tasks shouldn't be boring...*

## Overview

This tool runs a command at a specified frequency, logs its output (optionally to a file), and keeps an eye out for user-defined **regex** patterns. If a match is found, it can run a second “trigger” command — all while gracefully handling errors, rotating logs, and providing a final summary upon completion.

## Highlights

- **Simple CLI**: Provide arguments like `--command`, `--frequency`, and `--regex` to get started.
- **Regex Matching & Trigger**: Automatically react to patterns in the output and run an extra command once per iteration.
- **Log Rotation**: Prune the oldest lines of a log file once it exceeds a specified size.
- **Auto-Stop Timer**: Use `--timer` to halt execution after N seconds (or run indefinitely).
- **Cross-Platform**: Works on Windows, Linux, macOS — wherever Python 3 is available.

## Quick Start

1. **Download** [cli_monitor.py](https://raw.githubusercontent.com/Dimos082/cli-monitor/refs/heads/main/cli_monitor.py).
2. **Run**:
   ```bash
   python cli_monitor.py --command "echo Hello"
      ```
3. **Stop** it whenever you want (e.g., Ctrl + C), or use --timer.

## Example Commands
#### Echo Forever

```bash
python cli_monitor.py --command "echo Hello" --frequency 3
```
Repeats every 3s. Press Ctrl + C to stop.

#### Log & Prune

```bash
python cli_monitor.py --command "ls -la" --output-file "/tmp/mylog.txt" --max-log-size 50
```
Keeps your file under 50 KB by pruning oldest lines.

#### Regex Execution

```bash
python cli_monitor.py --command "cat /var/log/syslog" \
  --regex "error|fail" \
  --regex-execute "echo 'We have an error!'" \
  --timer 10
  ```
Stops after 10s, and runs an extra command if it sees “error” or “fail.”

## Wanna Help?
- Fork this project
- Make your changes
- Submit a pull request
- All feedback is welcome!

*Happy monitoring!*