#!/usr/bin/env python

from datetime import datetime
import sys
import platform
import re


def parse_log(syslog, options):
    """
    Parse syslog for europa transactions and build a list of dicts that
    each contain time, transaction num, and status. Returns a list of
    transactions that ocurred within the given time period.
    """

    transactions = []
    for line in syslog:
        # TODO: pass this in as option var log_entry_format
        if re.search('europa.+: tx [0-9]+ (started|completed)', line):
            line = line.split()
            time, tx, status = ' '.join(line[0:3]), line[6], line[7]

            transaction = {
                "tx_time": time,
                "tx_number": tx,
                "tx_status": status
            }
            transactions.append(transaction)

    tail_n = tail_index(transactions, options['time_period'])
    if tail_n:
        return [transaction for transaction in transactions[-tail_n:]]


def avg_response_time(transactions, options):
    """
    Compute the time in seconds for each transaction to complete
    and return the average.
    """

    completed_tx_count = 0.0
    total_response_time = 0.0

    for item in transactions:
        if item['tx_status'] == 'started':
            active_tx = item['tx_number']
            active_tx_started = item['tx_time']

            for item in transactions:
                if active_tx in item.values() and item['tx_status'] == 'completed':
                    completed_tx_count += 1
                    active_tx_completed = item['tx_time']
                    total_response_time += response_time(active_tx_started, active_tx_completed)

    if completed_tx_count:
        return total_response_time / completed_tx_count
    else:
        # avoid division by zero error if no completed tx within time period
        time = None
        run_check(options, time, state="unknown")


def run_check(options, res_time, state):
    """
    Check average transaction time against given values for warning and critical
    states, print status to STDOUT and issue appropriate exit code for Nagios.
    """

    if state == 'unknown':
        exit_code = 3
        print(state.upper() + " - No transaction data in given time period")
        sys.exit(exit_code)

    elif res_time < options['warning']:
        threshhold = options['warning']
        state = "OK -"
        exit_code = 0

    elif res_time > options["warning"] and res_time <= options["critical"]:
        threshhold = options['warning']
        state = "WARNING -"
        exit_code = 1

    elif res_time > options["critical"]:
        threshhold = options['critical']
        state = "CRITICAL -"
        exit_code = 2

    description = " average transaction time %0.2f secs during last %s secs, threshhold %s secs"
    print(state.upper() + description % (res_time, options['time_period'], threshhold))
    sys.exit(exit_code)


def tail_index(transactions, time_period):
    """
    Loop over transactions in reverse and return index value of record at the
    edge of time_period. This is used establish the time window to analyze.
    """

    now = datetime.strptime(datetime.now().strftime('%b %d %H:%M:%S'), '%b %d %H:%M:%S')

    for i, item in enumerate(transactions[::-1]):
        tx_time = datetime.strptime(item['tx_time'], '%b %d %H:%M:%S')
        if abs(now - tx_time).seconds >= time_period:
            return i


def response_time(started, completed):
    """
    Return the difference in seconds between started and completed times.
    """
    time1 = datetime.strptime(started, '%b %d %H:%M:%S')
    time2 = datetime.strptime(completed, '%b %d %H:%M:%S')
    return abs(time2 - time1).seconds


def parse_options(defaults):
    """ Parse command-line arguments and set defaults. Return dict of options. """

    args = sys.argv[1:]

    warning_value = args[args.index("--warning")+1]
    critical_value = args[args.index("--critical")+1]
    time_period = args[args.index("--time-period")+1]

    if "--help" in args or "-h" in args or len(args) < 1:
        show_usage()

    # get syslog path from user input or OS detection
    if "--log-file" in args:
        log_file = args[args.index("--log-file")+1]

    elif platform.linux_distribution()[0] == 'debian':
        log_file = defaults['syslog']['debian']

    elif platform.linux_distribution()[0] == 'ubuntu':
        log_file = defaults['syslog']['ubuntu']

    elif platform.linux_distribution()[0] == 'centos':
        log_file = defaults['syslog']['centos']

    elif platform.linux_distribution()[0] == 'redhat':
        log_file = defaults['syslog']['redhat']

    elif platform.linux_distribution()[0] == 'fedora':
        log_file = defaults['syslog']['fedora']

    else:
        log_file = defaults['syslog']['other']

    return {'warning': int(warning_value),
            'critical': int(critical_value),
            'time_period': int(time_period),
            'log_file': log_file}


def show_usage():
    """ Show usage information. Called when invalid command line arguments
    are supplied or when the user runs the program with --help."""

    msg = "Usage: %s --warning <value> --critical <value> --time-period <value> [options] \
           \n\nCheck average transaction time in seconds. \
            \n\n  Optional arguments: \
            \n    --log-file    log to retreive transactions from. The default is syslog. \
            \n    -h            print this help."
    print(msg % sys.argv[0])
    sys.exit(3)


def main():

    defaults = {
        'syslog':{
            'debian': '/var/log/syslog',
            'ubuntu': '/var/log/syslog',
            'centos': '/var/log/messages',
            'redhat': '/var/log/messages',
            'fedora': '/var/log/messages',
            'other': '/var/log/syslog'
        }
    }

    try:
        options = parse_options(defaults)
    except ValueError:
        show_usage()

    try:
        with open(options['log_file']) as f:
            log_data = parse_log(f, options)
    except FileExistsError:
        print("error loading transaction data")
        sys.exit(3)

    if log_data:
        time = avg_response_time(log_data, options)
        run_check(options, time, state=None)
    else:
        time = None
        run_check(options, time, state="unknown")


if __name__ == '__main__':
    main()
