#!/usr/bin/env python

import re
import sys
from os.path import basename, splitext

EXT = ".tsv"
LABELS = ["#min", "max", "value", "exclude"]


def get_table_name(path):
    return basename(splitext(inpath)[0])


def read_txt_table(path):
    data = []

    def _parse(string):
        return re.split(r"\s{2,}", string.strip())

    with open(inpath, "r") as fh:
        line = fh.readline()
        if line[0] != "d":
            raise ValueError("Expected header line: d* (got: {})".format(line))
        for line in fh:
            line = _parse(line)
            if "–" in line[0]:
                minr, maxr = map(int, line[0].split("–"))
            else:
                minr, maxr = int(line[0]), int(line[0])
            value = line[1]
            data.append((minr, maxr, value))

    return data


if __name__ == "__main__":
    inpath = sys.argv[1]
    table = get_table_name(inpath)
    outpath = table + EXT
    data = read_txt_table(inpath)
    dice_max = max([i[1] for i in data])

    header = {
        "NAME": table,
        "DICE": dice_max
    }

    with open(outpath, "w") as fh:
        for key, val in header.items():
            print("##{}={}".format(key, val), file=fh)
        print(*LABELS, sep="\t", file=fh)
        for item in data:
            print(*item, sep="\t", file=fh)