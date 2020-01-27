### Introduction

These are Nagios checks I wrote for an application I ran in production. The name Europa was changed from the actual application name and proprietary information has been removed.

The script `check_europa_open_files.py` monitors the number of open transaction files, and `check_europa_tx_time.py` analyzes the average transaction time for the application.

The scripts conform to the [Nagios Plugin API](https://assets.nagios.com/downloads/nagioscore/docs/nagioscore/3/en/pluginapi.html), so when executed they will display a single line status message to STDOUT and issue an exit code that corresponds to the result of the check.

### Dependencies

Python and the standard library is used.  There are no build requirements nor additional Python packages needed.

I've tested on Debian 8 with Python 2.7 and 3.4.

If you wish to use Python 3 instead of 2, use your system package manager to install it and set a symlink to the particular version you install, for example:

	$ sudo apt-get install python3
 	$ sudo ln -sf /usr/bin/python3.4 /usr/bin/python

### Running

Use these with Nagios as you would any other plugin.

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
