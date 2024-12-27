#!/usr/bin/env python3
"""
cli_monitor.py
Cross-platform tool for automating CLI commands and monitoring their outputs.

Usage:
  python cli_monitor.py --command "<command>" [options]

Run "python cli_monitor.py --help" for more details.
"""

import os, sys, time, subprocess, argparse, re, platform
from datetime import datetime

# --------------------- CLIArgumentParser Module -------------- #
class CLIArgumentParser:
    """Parses CLI arguments for the application."""
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="Execute and monitor a CLI command repeatedly.", 
            epilog="Example: python cli_monitor.py --command 'tail -f /myapp.log' --frequency 2 --max-log-size 2048 --output-file logs.txt --timer 30 --regex 'error|fail'")
        parser.add_argument("--command", help="The command to execute repeatedly (required).", required=True)
        parser.add_argument("--output-file", help="Path to the log file. If not specified, logs only appear in console.")
        parser.add_argument("--frequency", type=float, default=1.0, help="Interval (seconds) between command executions (default: 1).")
        parser.add_argument("--max-log-size", type=int, default=1024, help="Max log file size in KB (default: 1024).")
        parser.add_argument("--timer", type=float, default=0, help="Optional timer in seconds (default: 0 => indefinite).")
        parser.add_argument("--regex", help="Optional regex pattern to search for in command output. "
        "Supports advanced patterns using operators like 'or' (|) and 'and' (?=...). "
        "Counts the number of matches found in real-time output.")
        return parser.parse_args()

# --------------------- ErrorHandler Module ------------------- #
class ErrorHandler:
    """Handles errors during command execution and script-level exceptions."""
    def __init__(self): self.exception_count = 0  # Track number of exceptions

    def handle_command_error(self, command, exit_code, error_msg):  # Called when command fails
        self.exception_count += 1  # Increment count
        t = datetime.now().strftime("%d-%m-%Y %H:%M:%S")  # Timestamp
        return f"[{t}] ERROR running '{command}'. Exit Code: {exit_code}, Message: {error_msg}"

    def handle_script_error(self, script_name, exit_code, error_msg):  # Called when script fails
        t = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        return (f"[{t}] CRITICAL ERROR: {script_name} stopped unexpectedly. "
                f"Exit Code: {exit_code}, Message: {error_msg}")

# --------------------- Logger Module ------------------------- #
class LoggerModule:
    """Logs output to console and optional file, prunes file if size exceeds limit."""
    def __init__(self, output_file, max_size_kb):
        self.output_file = output_file  # Path to log file
        self.max_size_kb = max_size_kb
        self.max_size_bytes = max_size_kb * 1024

    def log(self, message):  # Logs message
        print(message)  # Always print to console
        if self.output_file:  # If file is specified, write there as well
            self._write_to_file(message + "\n")
            self._prune_log_if_needed()

    def _write_to_file(self, message):  # Writes string to log file
        try:
            with open(self.output_file, "a", encoding="utf-8") as f: f.write(message)
        except IOError as e:
            print(f"File write error: {e}")

    def _prune_log_if_needed(self):  # Checks file size and prunes if needed
        try:
            if os.path.getsize(self.output_file) > self.max_size_bytes: self._prune_oldest_entries()
        except OSError:
            pass  # File may not exist yet

    def _prune_oldest_entries(self):  # Removes oldest lines until file is within allowed size
        try:
            with open(self.output_file, "r", encoding="utf-8") as f: lines = f.readlines()
            while True:
                with open(self.output_file, "w", encoding="utf-8") as f: f.writelines(lines)
                if os.path.getsize(self.output_file) <= self.max_size_bytes: break
                if lines: lines.pop(0)  # Remove one line at a time
                else: break
        except OSError as e:
            print(f"Error pruning log file: {e}")

# --------------------- Regex Monitor Module ------------------ #
class RegexMonitor:
    """Checks each line of output for regex matches, counts them cumulatively."""
    def __init__(self, pattern):
        self.pattern = pattern  # Regex pattern
        self.match_count = 0

    def check_output(self, output_line):  # Checks an output line for regex matches
        if not self.pattern: return
        matches = re.findall(self.pattern, output_line)
        if matches: self.match_count += len(matches)

# --------------------- Command Executor Module --------------- #
class CommandExecutor:
    """Executes a shell command, returning stdout, stderr, and exit code."""
    @staticmethod
    def execute_command(command):
        try:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            stdout, stderr = proc.communicate()
            return proc.returncode, stdout, stderr
        except Exception as e:
            return -999, "", str(e)  # Indicate a fundamental error

# --------------------- Summary Module ------------------------ #
class SummaryModule:
    """Tracks script start/end times, counts, and generates a final summary."""
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.total_executions = 0
        self.script_termination_reason = "Manual or indefinite run"
        self.regex_matches = 0
        self.exceptions_encountered = 0

    def start(self): self.start_time = datetime.now()
    def stop(self): self.end_time = datetime.now()
    def increment_executions(self): self.total_executions += 1
    def increment_regex_matches(self, count): self.regex_matches += count
    def increment_exceptions(self): self.exceptions_encountered += 1
    def set_termination_reason(self, reason): self.script_termination_reason = reason

    def generate_summary(self):  # Creates a summary dictionary
        duration = str(self.end_time - self.start_time) if (self.start_time and self.end_time) else None
        return {
            "Start Time": str(self.start_time),
            "End Time": str(self.end_time),
            "Duration": duration,
            "Total Executions": self.total_executions,
            "Exceptions": self.exceptions_encountered,
            "Regex Matches": self.regex_matches,
            "Termination Reason": self.script_termination_reason
        }

# --------------------- Controller ---------------------------- #
class CliMonitorController:
    """Coordinates all modules: runs commands, logs output, monitors regex, handles errors."""
    def __init__(self, config):
        self.config = config
        self.logger = LoggerModule(config.output_file, config.max_log_size)
        self.regex_monitor = RegexMonitor(config.regex)
        self.error_handler = ErrorHandler()
        self.summary = SummaryModule()

    def run(self):
        self.summary.start()  # Mark start
        script_name = os.path.basename(sys.argv[0])
        command = self.config.command
        freq = self.config.frequency
        max_run_time = self.config.timer
        start_time = time.time()

        try:
            while True:
                if max_run_time > 0 and (time.time() - start_time) >= max_run_time:  # Timer check
                    self.summary.set_termination_reason("Timer expired")
                    break
                exit_code, stdout, stderr = CommandExecutor.execute_command(command)
                self.summary.increment_executions()
                if exit_code == -999:  # Fundamental error
                    err_log = self.error_handler.handle_command_error(command, exit_code, stderr)
                    self.logger.log(err_log)
                    self.summary.increment_exceptions()
                else:  # Normal command (may still have non-zero exit code)
                    t = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                    if stdout:
                        for line in stdout.strip().split("\n"):
                            self.logger.log(f"[{t}] (stdout) {line}")
                            before = self.regex_monitor.match_count
                            self.regex_monitor.check_output(line)
                            self.summary.increment_regex_matches(self.regex_monitor.match_count - before)
                    if stderr:
                        for err_line in stderr.strip().split("\n"):
                            self.logger.log(f"[{t}] (stderr) {err_line}")
                            before = self.regex_monitor.match_count
                            self.regex_monitor.check_output(err_line)
                            self.summary.increment_regex_matches(self.regex_monitor.match_count - before)
                    if exit_code != 0:  # Non-zero code => command error
                        err_log = self.error_handler.handle_command_error(command, exit_code, "Non-zero exit code.")
                        self.logger.log(err_log)
                        self.summary.increment_exceptions()
                time.sleep(freq)
        except KeyboardInterrupt:
            self.summary.set_termination_reason("Manual termination by user")
        except Exception as e:
            err_log = self.error_handler.handle_script_error(script_name, -1, str(e))
            self.logger.log(err_log)
            self.summary.increment_exceptions()
            self.summary.set_termination_reason("Unhandled exception in script")
        finally:
            self.summary.stop()
            final_summary = self.summary.generate_summary()
            self._print_summary(final_summary)

    def _print_summary(self, summary_dict):
        self.logger.log("----- Execution Summary -----")
        for k, v in summary_dict.items(): self.logger.log(f"{k}: {v}")
        self.logger.log("----------------------------")

# --------------------- Main Entry Point ---------------------- #
def main():
    config = CLIArgumentParser.parse_args()
    if config.frequency < 0.1 or config.frequency > 100000:
        print("Error: Frequency must be between 0.1 and 100000 seconds.")
        sys.exit(1)
    controller = CliMonitorController(config)
    controller.run()

if __name__ == "__main__":
    main()
