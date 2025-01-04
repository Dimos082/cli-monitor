# CLI Monitor 🖥️ 

> **CLI Monitor** is a *cross-platform* Python tool that repeatedly runs a command, captures its output, optionally logs it, and can even trigger a secondary command whenever a regex pattern is matched.

*Because repetitive tasks shouldn't be boring...*

**Unittests status for Win/Lin/Mac environments:** [![Python Multi-OS Tests](https://github.com/Dimos082/cli-monitor/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Dimos082/cli-monitor/actions/workflows/test.yml) 

<details>
  <summary>📖 Table of Contents</summary>

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Example Commands](#example-commands)
- [Arguments Overview](#arguments-overview)
- [Contributing](#contributing)
- [License](#license)
</details>

## Overview

CLI Monitor is designed to help automate command execution, log outputs, and monitor for specific patterns using **regex**. If a match is found, the tool can execute an additional command. It handles logging, error reporting, and summary generation with ease.

## Features

- **Flexible Command Execution**: Run any CLI command at a chosen frequency.
- **Pattern Matching with Regex**: Detect specific output patterns and trigger follow-up actions.
- **Smart Log Management**: Automatically rotate logs to prevent excessive file sizes.
- **Auto-Stop Timer**: Set a duration for execution or let it run indefinitely.
- **Cross-Platform Compatibility**: Works on Windows, Linux, and macOS with Python 3.


## ▶️ Quick Start

1. **Download** [cli_monitor.py](https://raw.githubusercontent.com/Dimos082/cli-monitor/refs/heads/main/cli_monitor.py).
2. **Run with an argument**:
   ```bash
   python cli_monitor.py --command "echo Hello"
   ```
3. **Stop** it at any time (e.g., Ctrl + C) or specify a timer with `--timer`.
4. **Check** the summary in terminal (or in log file if `--output-file` specified) after. Example:
```bash
----- Execution Summary -----
Start Time: 2025-01-04 22:43:24.021834
End Time: 2025-01-04 22:43:25.574156
Duration: 0:00:01.552322
Total Executions: 2
Exceptions: 0
Regex Matches: 0
Number of successful commands executed upon regex match: 0
Number of failed executed commands upon regex match: 0  
Termination Reason: Manual termination by user
```

[🔼 Back to top](#cli-monitor-️)

## 🎛️ Example Commands

### Process Monitoring (babysit/watchdog mode)

```bash
python cli_monitor.py \
  --command "pgrep my_app || echo NOT_FOUND" \
  --frequency 10 \
  --regex "NOT_FOUND" \
  --regex-execute "bash /path/to/start_my_app.sh"
```

This command checks every 10 seconds if `my_app` is running. If not, it triggers a script to restart it.

### Repeating Echo

```bash
python cli_monitor.py --command "echo Hello" --frequency 3
```

Prints "Hello" every 3 seconds.

###  Log File Management

```bash
python cli_monitor.py --command "ls -la" --output-file "/tmp/mylog.txt" --max-log-size 50
```

Keeps logs within 50 KB by trimming older entries.

### Detecting Errors in Logs

```bash
python cli_monitor.py --command "cat /var/log/syslog" \
  --regex "error|fail" \
  --regex-execute "echo 'An issue was detected!'" \
  --timer 10
```

Runs for 10 seconds, searching for "error" or "fail" and executing an alert command when found.

[🔼 Back to top](#cli-monitor-️)

## 💬 Arguments Overview

| Argument         | Required? | Default | Description |
|-----------------|:---------:|--------:|-------------|
| `--command`      | Yes       | None    | The main command to run repeatedly. |
| `--output-file`  | No        | None    | Full path to a log file. If omitted, logs appear in the console only. |
| `--frequency`    | No        | 1.0     | Time interval in seconds between each execution (Min: 0.1; Max: 100000). |
| `--max-log-size` | No        | 1024    | Max log file size in KB. If exceeded, the script prunes oldest lines. |
| `--timer`       | No        | 0       | Stops automatically after N seconds. 0 means run indefinitely. |
| `--regex`       | No        | None    | A regex pattern to find in the command output. |
| `--regex-execute` | No       | None    | A command to run once per iteration if the regex pattern is matched. |

[🔼 Back to top](#cli-monitor-️)

## 🛠️ Contributing

We welcome contributions to make CLI Monitor even better! If you have an idea for an improvement or new [test cases](https://github.com/Dimos082/cli-monitor/tree/main/tests), feel free to:

- **Fork the repository**
- **Create a new feature branch**:
  `git checkout -b feature/NewFeature`
- **Make your changes and commit**:
  `git commit -m "Added NewFeature`
- **Push your changes**: `git push origin feature/NewFeature`
- **Open a pull request**  🐈‍⬛

If you find a bug or have a feature request, check out [open issues](https://github.com/Dimos082/cli-monitor/issues) or create a new one. Your feedback is valuable!

If you find [cli_monitor.py](https://raw.githubusercontent.com/Dimos082/cli-monitor/refs/heads/main/cli_monitor.py) useful, consider giving it a ⭐ on GitHub!


## 📜 License

This project is licensed under the Apache 2.0 - see the [LICENSE](https://github.com/Dimos082/cli-monitor?tab=Apache-2.0-1-ov-file) file for details.

[🔼 Back to top](#cli-monitor-️) 