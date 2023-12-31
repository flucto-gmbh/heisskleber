import argparse


class KeyValue(argparse.Action):
    def __call__(self, parser, args, values, option_string=None) -> None:
        try:
            params = dict(x.split("=") for x in values)
        except ValueError as ex:
            raise argparse.ArgumentError(
                self,
                f'Could not parse argument "{values}" as k1=v1 k2=v2 ... format: {ex}',
            ) from ex
        setattr(args, self.dest, params)


def get_cmdline(args=None) -> dict:
    """
    get commandline arguments and return a dictionary of
    the provided arguments.

    available commandline arguments are:
        --verbose: flag to toggle debugging output
        --print-stdout: flag to toggle all data printed to stdout
        --param key1=value1 key2=value2: allows to pass service specific
            parameters
    """
    arp = argparse.ArgumentParser()
    arp.add_argument("--verbose", action="store_true", help="debug output flag")
    arp.add_argument(
        "--print-stdout",
        action="store_true",
        help="toggles output of all data to stdout",
    )
    arp.add_argument(
        "--params",
        nargs="*",
        action=KeyValue,
    )
    args = arp.parse_args(args)
    config = {}
    if args.verbose:
        config["verbose"] = args.verbose
    if args.print_stdout:
        config["print_stdout"] = args.print_stdout
    if args.params:
        config |= args.params
    return config
