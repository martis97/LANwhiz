import os
import json
import re
import datetime
from statistics import mean


class GaugeTimes():
    """ Class which contains methods for log sorting and dashboard metrics'
    computation.
    """

    def __init__(self):
        # self.home_path = "//scsc.local/Fileroot/UnixHomes/devopsapps" # Windows
        self.home_path = "/home/devopsapps" # Unix
        self.logs_path = f"{self.home_path}/jenkins_run_logs/jenkins-swci"
        self.dashboard_home = f"{self.home_path}/public_html/CI/dashboard"
        self.gauge_data_json = f"{self.dashboard_home}/json_data/gauge-data.json"
        self.sanity_jobs_in_progress = 0
        self.verify_jobs_in_progress = 0
        self.avg_time = lambda runs: round((mean(runs) / 60))

    def get_last_n_sorted_logs(
        self,
        build_type,
        n,
        staging=False,
        full_logs_only=False
    ):
        """ Gets all logs given their type, sorts them and returns the
        last n.

        Args:
            build_type: (str) type of logs to obtain. Expected either "sanity"
                or "verify"

            n: (int) Number of logs required

            staging: (bool, default is False) Specify whether to use
                j-swci-dev (development, or staging) or jenkins-swci
                (main, or production)

            full_logs_only: (bool, default is False) Specify whether logs
                from replacement runs are not required.
        """

        has_finished = r"^[\d]{10}\sFINISH:\s(verify|sanity)\srun$"
        build_failed = r"^[\d]{10}\sRESULT:\sStandard\sBuild.+RESULT=FAIL$"
        stylecheck_failed = r"^[\d]{10}\sRESULT:\sstylecheck\sRESULT=FAIL$"

        logs_path = self.logs_path.replace(
            "jenkins-swci", "j-swci-dev"
        ) if staging else self.logs_path

        build_log_dir = f"{logs_path}/ci.dev.{build_type}"
        build_log_files = os.listdir(build_log_dir)
        log_ids = sorted([int(log.split(".")[0]) for log in build_log_files])
        sorted_log_names = [f"{log_id}.log" for log_id in log_ids]
        logs_to_remove = []
        complete_logs = 0

        for log_file in reversed(sorted_log_names):
            log_valid = True
            with open(f"{build_log_dir}/{log_file}", "r") as log:
                log_as_string = log.read()
                lines = [line for line in log_as_string.split("\n") if line]
                if not re.match(has_finished, lines[-1]):
                    if build_type == "sanity":
                        self.sanity_jobs_in_progress += 1
                    elif build_type == "verify":
                        self.verify_jobs_in_progress += 1
                    logs_to_remove.append(log_file)
                    continue
                if build_type == "sanity":
                    for line in lines:
                        # Remove any failed logs
                        if re.match(stylecheck_failed, line
                        ) or re.match(build_failed, line):
                            logs_to_remove.append(log_file)
                            log_valid = False
                            break
                    if "START: Test" not in log_as_string \
                        or "FINISH: Test" not in log_as_string:
                        if log_file not in logs_to_remove:
                            logs_to_remove.append(log_file)
                            log_valid = False
                elif build_type == "verify":
                    for line in lines:
                        if re.match(stylecheck_failed, line):
                            logs_to_remove.append(log_file)
                            log_valid = False
                            break

                if full_logs_only:
                    # Replacement run logs typically have less than 20 lines
                    if len(lines) < 20 and log_file not in logs_to_remove:
                        logs_to_remove.append(log_file)
                        log_valid = False

                if log_valid:
                    complete_logs += 1

                # Stop iteration if desired amount of logs is detected
                if complete_logs >= n:
                    break

        # Remove the incomplete/failed logs
        for log in logs_to_remove:
            sorted_log_names.remove(log)

        return sorted_log_names[-n:]

    def get_average_build_times(self, build_type):
        """ Gets the last 10 log files from Sanity builds, collects the
        start and end timestamps and returns the average duration.

        Args:
            build_type: Type of build to get an average of.
                Choices are 'verify' and 'sanity'

        Returns:
            avg_full_run_duration: Average time it took for full jobs to
                run in minutes.
            avg_replace_run_duration: Average time it took for full jobs to
                run in minutes.
        """

        log_durations = []
        build_log_dir = f"{self.logs_path}/ci.dev.{build_type}"
        sorted_logs = self.get_last_n_sorted_logs(build_type, 10)

        # Get the run time of each log
        for log_file in sorted_logs:
            with open(f"{build_log_dir}/{log_file}", "r") as log:
                lines = log.readlines()
                start_epoch = int(lines[0].split(" ")[0])
                finish_epoch = int(lines[-1].split(" ")[0])
                log_durations.append(finish_epoch - start_epoch)

        full_runs = []
        replace_runs = []

        # Anything under 600secs (10mins) is considered as a Replacement run
        for i in log_durations:
            if i < 600:
                replace_runs.append(i)
            else:
                full_runs.append(i)

        # If no replace runs found, add a zero for round() to not
        # throw an exception
        if not replace_runs:
            replace_runs.append(0)

        return self.avg_time(full_runs), self.avg_time(replace_runs)

    def get_chamber_wait_time(self):
        """ Gets test chamber wait time from Sanity logs """

        sanity_logs = self.get_last_n_sorted_logs(
            "sanity",
            5,
            full_logs_only=True
        )
        log_durations = []

        # Getting test durations from 5 complete log files
        for log_file in sanity_logs:
            with open(
                f"{self.logs_path}/ci.dev.sanity/{log_file}", "r"
            ) as log:
                lines = log.readlines()
                for line in lines:
                    if "START: Test" in line:
                        start_epoch = int(line.split(" ")[0])
                    elif "FINISH: Test" in line:
                        finish_epoch = int(line.split(" ")[0])
                log_durations.append(finish_epoch - start_epoch)

        chamber_wait = self.avg_time(log_durations) - 20

        return chamber_wait if chamber_wait > 0 else 0

    def get_grid_wait_time(self):
        """ Returns the maximum Qsub wait time of last 5 logs """
        
        # Specify to use j-swci-dev, change to False once Qsub time
        # is defined in jenkins-swci Verify logs.
        staging = False

        verify_logs = self.get_last_n_sorted_logs(
            "verify",
            10,
            staging=staging
        )

        logs = self.logs_path.replace(
            "jenkins-swci", "j-swci-dev"
        ) if staging else self.logs_path

        grid_wait_times = []
        for log_file in verify_logs:
            with open(f"{logs}/ci.dev.verify/{log_file}", "r") as log:
                lines = log.readlines()
                for line in lines:
                    if "Qsub wait time" in line:
                        grid_wait_times.append(int(line.split(" ")[-2]))

        grid_wait_mins = round((max(grid_wait_times)) / 60)

        return grid_wait_mins if grid_wait_mins > 0 else 0

    def write_data_to_log(self, data):
        """ Output the metrics to a log file

        Args:
            data: (dict) Gauge metrics used for output.
        """

        gauge_logs_dir = f"{self.dashboard_home}/gauge_data_logs"
        gauge_logs = os.listdir(gauge_logs_dir)

        if len(gauge_logs) >= 20:
            for log in gauge_logs:
                os.remove(f"{gauge_logs_dir}/{log}")
            new_log_name = 1

        elif gauge_logs:
            log_ids = sorted([int(log.split(".")[0]) for log in gauge_logs])
            new_log_name = log_ids[-1] + 1

        else:
            new_log_name = 1

        with open(f"{gauge_logs_dir}/{new_log_name}.log", "w") as log:
            log.write(f"{datetime.datetime.now()}\n")
            log.write(f"Sanity (full): {data['sanity']['full']}min(s)\n")
            log.write(f"Sanity (replace): {data['sanity']['replace']}min(s)\n")
            log.write(f"Verify (full): {data['verify']['full']}min(s)\n")
            log.write(f"Verify (replace): {data['verify']['replace']}min(s)\n")
            log.write(f"Chamber wait time: {data['chamber_wait']}min(s)")
            log.write(f"Grid wait time: {data['grid_wait']}sec(s)")

    def main(self):
        """ Main function to get required metrics and write the data to JSON """

        runs = {
            "sanity" : {},
            "verify" : {},
            "chamber_wait" : 0,
            "grid_wait" : 0
        }

        for build_type in ("verify", "sanity"):
            runs[build_type]["full"], runs[build_type]["replace"] = \
                self.get_average_build_times(build_type)
            print(
                f"Average {build_type.title()} time (Full Runs): "
                f"{runs[build_type]['full']}mins."
            )
            print(
                f"Average {build_type.title()} time (Replace Runs):"
                f"{runs[build_type]['replace']}mins."
            )

        runs["chamber_wait"] = self.get_chamber_wait_time()
        print(f"Average Chamber Wait time: {runs['chamber_wait']}mins.")
    
        grid_wait = self.get_grid_wait_time()
        print(f"Grid wait time: {grid_wait}secs.")
        runs["grid_wait"] = grid_wait

        with open(self.gauge_data_json, "w") as runs_json:
            json.dump(runs, runs_json, indent=4)

        self.write_data_to_log(runs)


if __name__ == "__main__":
    GaugeTimes().main()
