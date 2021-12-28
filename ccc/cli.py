from __future__ import annotations
from pathlib import Path
from queue import Queue
import argparse
import os

from .datastructures import Config
from .display import formatResult
from .datastructures import *
from .process import DirWalker, fileProcessWorker, fileSummarize


def parse_args():
    parser = argparse.ArgumentParser(description="Cool code counter")
    parser.add_argument("path", type=Path, help="Files or directories", nargs="?")
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Verbose output",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    entryPoint = Path(os.getcwd()) if not args.path else args.path
    Config.verbose = args.verbose
    assert entryPoint.exists(), "Dir does not exists: " + str(entryPoint)

    fileListQueue: FileJobQueue = Queue()
    fileSummaryQueue: FileSummaryQueue = Queue()

    dw = DirWalker(fileListQueue)
    dw.start(entryPoint)

    fileProcessWorker(fileListQueue, fileSummaryQueue)

    summaries = fileSummarize(fileSummaryQueue)
    formatResult(summaries)


if __name__ == "__main__":
    main()
