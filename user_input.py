import sys

from booklet import make_booklet, test_booklet


def decode_args():
    return {arg.split("=")[0]: arg.split("=")[1] for arg in sys.argv[1:]}


def handle_args(args):
    try:
        mode = args["-mode"]
        if mode not in ["make", "test", "help"]:
            raise ValueError
    except ValueError:
        mode = "help"
        print("Available modes: make, test or help\n")
    except KeyError:
        mode = "help"

    try:
        input_file = args["-file"]
    except KeyError:
        print("Missing file name argument\n")
        input_file = ""
        mode = "help"

    try:
        input_sheets_per_signature = int(args["-s"])
        sheets_per_signature = max(input_sheets_per_signature, 1)
    except KeyError:
        sheets_per_signature = 1
    except ValueError:
        print("Number of sheets per signature should be a number\n")
        mode = "help"

    return input_file, mode, sheets_per_signature


def handle_modes(input_file, mode, sheets_per_signature):
    if mode == "make":
        make_booklet(
            input_file,
            sheets_per_signature
        )
    elif mode == "test":
        test_booklet(
            input_file
        )
    elif mode == "help":
        print(f"-mode=<'make'|'test'>\n"
              f"  make: produce booklet\n"
              f"  test: check number of signatures based on sheets per signature\n"
              f"\n"
              f"-file=<path>\n"
              f"  path to the file\n"
              f"\n"
              f"-s=<number>\n"
              f"  number of sheets per signature")
