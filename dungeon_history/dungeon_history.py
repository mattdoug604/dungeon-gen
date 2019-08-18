#!/usr/bin/env python

import random
import sys
from glob import glob
from os.path import dirname, join


TABLE_GLOB = glob(join(dirname(__file__), "tables", "*.tsv"))
with open(join(dirname(__file__), "tables", "order.txt"), "r") as fh:
    TABLE_ORDER = [i.strip() for i in fh.readlines()]


class Roll:
    def __init__(self, weight, value, includes=None, excludes=None):
        self.weight = float(weight)
        self.value = value
        if includes:
            self.includes = includes.split(" ")
        else:
            self.includes = includes
        if excludes:
            self.excludes = excludes.split(" ")
        else:
            self.excludes = excludes


class Table:
    def __init__(self, name, label, data, weights):
        self.name = name
        self.label = label
        self.data = data
        self.weights = weights

    @classmethod
    def load(cls, path):
        header = {}
        keys = {}
        vals = []

        def _split(string, sep="\t"):
            return string.strip().split(sep)

        with open(path, "r") as fh:
            for line in fh:
                if line.startswith("##"):
                    header.update(dict([_split(line[2:], "=")]))
                elif line.startswith("#"):
                    line = line[1:]
                    for n, i in enumerate(_split(line)):
                        keys[n] = i
                else:
                    vals.append(_split(line))

        name = header["NAME"]
        label = header["LABEL"]
        data = [Roll(**{keys[n]: x for n, x in enumerate(i)}) for i in vals]
        total = len(data)
        weights = [i.weight / total for i in data]

        return cls(name=name, label=label, data=data, weights=weights)

    def roll(self):
        self.last_roll = random.choices(population=self.data, weights=self.weights)[0]

        return self.last_roll


def main():
    tables = {}
    preroll = {}

    for path in TABLE_GLOB:
        table = Table.load(path)
        tables[table.name] = table
        preroll[table.name] = table.roll().value

    queue = TABLE_ORDER
    exclude = []
    output = []
    while queue:
        i = queue.pop(0)
        table = tables[i]
        value = table.last_roll.value
        includes = table.last_roll.includes
        excludes = table.last_roll.excludes
        value = value.format(**preroll)
        if includes:
            queue = includes + queue
        if excludes:
            queue = [i for i in queue if i not in excludes]
        output.append({table.label: value})

    for i in output:
        for key, val in i.items():
            print(f"{key}: {val}")


if __name__ == "__main__":
    main()
