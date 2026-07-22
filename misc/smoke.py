import argparse
import datetime
import os

import hapiclient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument("--exclude-path")
    args = parser.parse_args()

    package_path = os.path.realpath(hapiclient.__file__)
    if hapiclient.__version__ != args.version:
        raise AssertionError(
            "Expected version {}, found {}".format(
                args.version, hapiclient.__version__
            )
        )

    if args.exclude_path:
        excluded_path = os.path.realpath(args.exclude_path)
        try:
            is_excluded = os.path.commonpath([package_path, excluded_path]) == excluded_path
        except ValueError:
            is_excluded = False
        if is_excluded:
            raise AssertionError("Imported package from excluded path: " + package_path)

    result = hapiclient.datetime2hapitime(datetime.datetime(2000, 1, 1))
    expected = "2000-01-01T00:00:00.000000Z"
    if result != expected:
        raise AssertionError("Expected {}, found {}".format(expected, result))

    print(hapiclient.__version__, package_path)


if __name__ == "__main__":
    main()