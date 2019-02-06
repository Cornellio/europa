#!/usr/bin/env python

import os
import sys


def run_check(options):
    """
    Compare number of open files against given values for warning and critical
    states, then print status to STDOUT and issue approprite exit code for Nagios.
    """

    open_file_count = len_lsof(options)

    if open_file_count < options['warning']:
        state = "OK -"
        exit_code = 0

    elif open_file_count > options['warning'] and \
    open_file_count <= options["critical"]:
        state = "WARNING -"
        exit_code = 1

    elif open_file_count > options['critical']:
        state = "CRITICAL -"
        exit_code = 2

    else:
        state = "UNKNOWN -"
        exit_code = 3
        print(state + " Cannot determine open file count")
        sys.exit(exit_code)

    description = " %s transaction files open."
    print(state + description % (open_file_count))
    sys.exit(exit_code)


def len_lsof(options):
    """ Return number of open transaction files in given directory. """

    lsof_cmd = "/usr/bin/lsof +d " + options['data_dir'] + " -u " + \
                options['app_user'] + " -a | /usr/bin/awk '{print $9}' | \
                /bin/egrep 'data/.*\.yaml'"

    return len(os.popen(lsof_cmd).readlines())


def parse_options(defaults):
    """
    Parse command-line arguments and set defaults.
    """
    args = sys.argv[1:]

    critical_value = args[args.index("--critical")+1]
    warning_value = args[args.index("--warning")+1]

    if "--data-dir" in args:
        data_dir = args[args.index("--data-dir")+1]
    else:
        data_dir = defaults['data_dir']

    if "-u" in args:
        app_user = args[args.index("-u")+1]
    else:
        app_user = defaults['app_user']

    if "--help" in args or "-h" in args or len(args) < 1:
        show_usage()

    return {'warning': int(warning_value),
            'critical': int(critical_value),
            'data_dir': data_dir,
            'app_user': app_user}


def show_usage():
    """ Show usage information. Called when invalid command line arguments
    are supplied or when the user runs the program with --help."""

    msg = "Usage: %s --warning <value> --critical <value> [options] \
          \n\nCheck number of open transaction files. \
          \n\n  Optional arguments: \
          \n    --data-dir    directory in which to check open files. \
          \n    -u            check open files owned by user. \
          \n    -h            print this help."
    print(msg % sys.argv[0])
    sys.exit(3)


def main():

    defaults = {
        'data_dir': '/opt/europa/data',
        'app_user': 'europa'
    }

    try:
        options = parse_options(defaults)
    except ValueError:
        show_usage()

    run_check(options)


if __name__ == '__main__':
    main()
