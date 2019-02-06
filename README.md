### Introduction

These scripts are examples of Nagios checks I have written. They were adapted from checks used on a real web applicaiton but details have been changed to protect proprietary information. The name Europa is made up, inspired by one of the moons of Jupiter.

The checks are designed to monitor the Europa web application with Nagios. `check_europa_open_files.py` is for monitoring the number of open transaction files, and `check_europa_tx_time.py`, for analyzing average transaction time from the application log.

The programs will display a single line status message to STDOUT and issue an exit code for use by Nagios that corresponds to the result of the check. The exit codes are:

| Exit Code | Status |
| --------------------- |
| 0 | OK |
| 1 | WARNING |
| 2 | CRITICAL |
| 3 | UNKNOWN |

### Dependencies

Python and the standard library is used.  There are no build requirements nor additional Python packages needed.

The programs have been tested on Debian 8 with Python 2.7 and 3.4.  They will use whichever Python version is set as the system default, usually Python 2, but either version 2 or 3 may be used. You may run `python --version` to see which version runs by default on your system.

If you wish to use Python 3 instead of 2, use your system package manager to install it and set a symlink to the particular version you install, for example:

	$ sudo apt-get install python3
 	$ sudo ln -sf /usr/bin/python3.4 /usr/bin/python

### Running

Make the scripts executable with `chmod +x check_europa*.py` and run them from any location.

Running the programs without their required arguments or with `--help` will display usage information and exit with a status of 3.

#### Check Open Files

To check open files run `check_europa_open_files.py` and specify `--warning` and `--critical` thresholds for the number of open transaction files to monitor, for example:

	$ sudo ./check_europa_open_files.py --warning 10 --critical 20
	WARNING - 17 transaction files open.

In this case a warning is displayed since the result is between 10 and 20, and an exit code of 1 is issued. You may confirm the exit code by checking the value of the variable `$?` :

	$ echo $?
	1

By default the program will check for open files in `/opt/europa/data` that are owned by the user `europa`.  You may customize this behavior by using `--data-dir` and `-u` on the command line. This would allow you to adapt the program to changes in the underlying application environment.

#### Check Transaction History

To check the transaction history, run `check_europa_tx_time.py` with values for `--warning` and `--critical` along with the`--time-period` in which to analyze.

	sudo ./check_europa_tx_time.py --warning 6 --critical 8 --time-period 180
	OK - average transaction time 5.12 secs during last 180 secs, threshold 6 secs

This shows shows an average transaction response time of 5.12 seconds during the last 3 minutes and displays a status of **OK** and an exit code of 0.

	$ echo $?
	0

The transaction history is pulled from syslog, and since it's location varies by operating system, the program attempts to detect and set the proper location based on Linux distribution. For example, `/var/log/syslog` will be used on Debian and `/var/log/messages` on CentOS systems. You can also set a custom log file location on the command line using the `--log-file` argument.
