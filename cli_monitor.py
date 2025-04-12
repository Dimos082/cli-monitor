#!/usr/bin/env python3

import os, sys, time, subprocess, argparse, re, platform
from datetime import datetime
# Source: https://github.com/Dimos082/cli-monitor
__version__ = "1.0.1"
# Constants:
MIN_FREQUENCY = 0.1          # Minimum allowed frequency (seconds)
MAX_FREQUENCY = 100000       # Maximum allowed frequency (seconds)
EXECUTION_ERROR_CODE = -999  # Indicates an error in CommandExecutor

class CLIArgumentParser:
    """Parses command-line arguments."""
    @staticmethod
    def parse_args():
        class CustomFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
            pass

        p = argparse.ArgumentParser(
            description="CLI command executor with optional regex-based triggers.",
            formatter_class=CustomFormatter,
            epilog="""
        Exit Codes:
            0  Success
            1  General error
            2  Regex validation error
        """
        )
        p.add_argument("-v", "--version", action="version", version=f"CLI Monitor {__version__}")
        p.add_argument("--output-file", help="Log file path; console only if omitted.")
        p.add_argument("--frequency", type=float, default=1.0, help="Seconds between each execution.")
        p.add_argument("--max-log-size", type=int, default=1024, help="Max log file size in KB.")
        p.add_argument("--timer", type=float, default=0, help="Stop after N seconds (0 => infinite).")
        p.add_argument("--regex", help="Regex pattern to watch for in output.")
        p.add_argument("--command", nargs="+", metavar=("CMD", "ARGS"), required=True,
                       help="Main command to run.\nExample: --command ls -la /")
        p.add_argument("--regex-execute", metavar=("CMD"), default=[],
                       help="Command to execute when regex matches.\nExample: --regex-execute echo 'Match found'")
        
        args = p.parse_args()
        

        if args.max_log_size <= 0: # Validation logic
            p.error("--max-log-size must be greater than 0 KB")
        if "--max-log-size" in sys.argv and not args.output_file:
            print("Warning: --max-log-size is ignored since --output-file is not set.", file=sys.stderr)
        if not (MIN_FREQUENCY <= args.frequency <= MAX_FREQUENCY):
            p.error(f"Frequency must be between {MIN_FREQUENCY} and {MAX_FREQUENCY}.")
        return args

class ErrorHandler:
    """Logs command/script errors and increments exception counts."""
    def __init__(self):
        self.exception_count = 0

    def handle_command_error(self, cmd, code, msg):
        """Handles command execution errors."""
        self.exception_count += 1
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{t}] ERROR running '{cmd}': code={code}, msg={msg}"

    def handle_script_error(self, script, code, msg):
        """Handles script-level errors."""
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"[{t}] CRITICAL ERROR: {script} stopped. code={code}, msg={msg}"
        print(error_message, file=sys.stderr)
        sys.exit(1)  # Exit with a non-zero code

    def handle_regex_error(self, error):
        """Handles regex validation errors."""
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"[{t}] CRITICAL ERROR: {error}"
        print(error_message, file=sys.stderr)
        sys.exit(2)  # Exit with a specific code for regex errors

class LoggerModule:
    """Logs to console and optional file; prunes if file exceeds size limit."""
    def __init__(self, file_path, max_kb):
        self.file_path = file_path
        self.max_bytes = max_kb * 1024

    def log(self, msg):
        """Logs a message to console and file."""
        print(msg)  # Always print to console
        if self.file_path:
            try:
                with open(self.file_path, "a", encoding="utf-8") as f:
                    f.write(msg + "\n")
                if os.path.getsize(self.file_path) > self.max_bytes: 
                    self._prune() # Check file size and prune if needed
            except IOError as e:
                print(f"File write error: {e}")

    def _prune(self):
        """Removes oldest lines until file is under max_bytes."""
        with open(self.file_path, "r", encoding="utf-8") as f: 
            lines = f.readlines()
        while lines:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            if os.path.getsize(self.file_path) <= self.max_bytes:
                break
            lines.pop(0)  # Remove one line at a time from the top

class CommandExecutor:
    """Executes shell commands and returns (exit_code, stdout, stderr)."""
    @staticmethod
    def execute_command(cmd):
        try:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            out, err = p.communicate()
            return p.returncode, out, err
        except Exception as e:
            return EXECUTION_ERROR_CODE, "", str(e) # Return a special error code indicating an error

class SummaryModule:
    """Tracks counters/times and produces a final summary dictionary."""
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.total_executions = 0
        self.regex_matches = 0
        self.exceptions_encountered = 0
        self.triggered_command_success = 0
        self.triggered_command_fail = 0
        self.termination = "Manual or indefinite run"

    def start(self):
        """Starts the summary timer."""
        self.start_time = datetime.now()

    def stop(self):
        """Stops the summary timer."""
        self.end_time = datetime.now()

    def generate_summary(self):
        """Generates a summary dictionary."""
        dur = str(self.end_time - self.start_time) if self.start_time and self.end_time else None
        return {
            "Start Time": str(self.start_time),
            "End Time": str(self.end_time),
            "Duration": dur,
            "Total Executions": self.total_executions,
            "Exceptions": self.exceptions_encountered,
            "Regex Matches": self.regex_matches,
            "Number of successful commands executed upon regex match": self.triggered_command_success,
            "Number of failed executed commands upon regex match": self.triggered_command_fail,
            "Termination Reason": self.termination
        }

class RegexMonitor:
    """Checks lines for regex; triggers optional extra command once per iteration with matches."""
    def __init__(self, pattern, trigger_cmd, logger, summary):
        self.pattern = pattern
        self.trigger_cmd = trigger_cmd
        self.logger = logger
        self.summary = summary
        self.match_count = 0
        self._triggered = False  # Ensures only one triggered command per iteration
 
        if self.pattern:  # Validate regex pattern
            try:
                re.compile(self.pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")

    def start_new_iteration(self):
        """Resets the triggered-command status for the next iteration."""
        self._triggered = False

    def check_output(self, line):
        """Checks output line for regex matches and triggers command if needed."""
        if not self.pattern:
            return
        matches = re.findall(self.pattern, line)
        if matches:
            self.match_count += len(matches)
            if self.trigger_cmd and not self._triggered:
                self._triggered = True
                t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.logger.log(f"[{t}] (INFO) Regex matched; running '{self.trigger_cmd}'")
                c, so, se = CommandExecutor.execute_command(self.trigger_cmd)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for s in (so or "").strip().split("\n"):
                    if s: self.logger.log(f"[{now}] (regex-execute stdout) {s}")
                for s in (se or "").strip().split("\n"):
                    if s: self.logger.log(f"[{now}] (regex-execute stderr) {s}")
                if c == 0:
                    self.summary.triggered_command_success += 1
                    self.logger.log(f"[{now}] (INFO) Trigger '{self.trigger_cmd}' succeeded.")
                else:
                    self.summary.triggered_command_fail += 1
                    self.logger.log(f"[{now}] (ERROR) Trigger '{self.trigger_cmd}' failed (code={c}).")

class CliMonitorController:
    """Main controller that orchestrates all modules."""
    def __init__(self, cfg):
        self.cfg = cfg
        self.logger = LoggerModule(cfg.output_file, cfg.max_log_size)
        self.error_handler = ErrorHandler()
        self.summary = SummaryModule()
        try:
            self.monitor = RegexMonitor(cfg.regex, cfg.regex_execute, self.logger, self.summary)
        except ValueError as e:
            self.error_handler.handle_regex_error(e)
        except KeyboardInterrupt:
            self.summary.termination = "Manual termination by user"
            self.logger.log("INFO: Execution manually terminated by the user.")

    def run(self):
        """Runs the CLI monitor."""
        self.summary.start()
        start_time = time.time()
        cmd = self.cfg.command
        freq = self.cfg.frequency
        try:
            while True:
                if self.cfg.timer > 0 and (time.time() - start_time) >= self.cfg.timer:
                    self.summary.termination = "Timer expired"
                    break
                code, out, err = CommandExecutor.execute_command(cmd)
                self.summary.total_executions += 1
                if code == EXECUTION_ERROR_CODE:
                    e_msg = self.error_handler.handle_command_error(cmd, code, err)
                    self.logger.log(e_msg)
                    self.summary.exceptions_encountered += 1
                else:
                    self._process_output(out, err, cmd, code)
                time.sleep(freq)
        except KeyboardInterrupt:
            self.summary.termination = "Manual termination by user"
        except Exception as e:
            self.error_handler.handle_script_error(os.path.basename(sys.argv[0]), -1, str(e))
        finally:
            self._finalize_summary()

    def _process_output(self, out, err, cmd, code):
        """Processes the command output and handles regex matching."""
        self.monitor.start_new_iteration()
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if out:
            for line in out.strip().split("\n"):
                self.logger.log(f"[{t}] (stdout) {line}")
                before = self.monitor.match_count
                self.monitor.check_output(line)
                inc = self.monitor.match_count - before
                if inc > 0: self.summary.regex_matches += inc
        if err:
            for e_line in err.strip().split("\n"):
                self.logger.log(f"[{t}] (stderr) {e_line}")
                before = self.monitor.match_count
                self.monitor.check_output(e_line)
                inc = self.monitor.match_count - before
                if inc > 0: self.summary.regex_matches += inc
        if code != 0:
            e_msg = self.error_handler.handle_command_error(cmd, code, "Non-zero exit.")
            self.logger.log(e_msg)
            self.summary.exceptions_encountered += 1

    def _finalize_summary(self):
        """Finalizes and logs the summary."""
        self.summary.stop()
        s = self.summary.generate_summary()
        self.logger.log("----- Execution Summary -----")
        for k, v in s.items():
            self.logger.log(f"{k}: {v}")
        self.logger.log("----------------------------")

def main():
    cfg = CLIArgumentParser.parse_args()
    controller = CliMonitorController(cfg)
    controller.run()

if __name__ == "__main__":
    main()