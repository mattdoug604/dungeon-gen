#!/usr/bin/env python

import random
import sys
from collections import OrderedDict
from glob import glob
from os.path import basename, dirname, join, splitext


TABLE_DATA_DIR = join(dirname(__file__), "data")
TABLE_ORDER_FILE = join(dirname(__file__), "data", "order.txt")


class Roll:
    def __init__(self, weight, value, includes=None, excludes=None, source=None):
        self.value = value or ""
        self.source = source or ""
        if weight:
            self.weight = float(weight)
        else:
            self.weight = 1.0
        if includes:
            self.includes = includes.split(" ")
        else:
            self.includes = includes
        if excludes:
            self.excludes = excludes.split(" ")
        else:
            self.excludes = excludes


class TableLoader:
    @classmethod
    def load(cls, data_dir=TABLE_DATA_DIR, order_file=TABLE_ORDER_FILE):
        table_paths = cls._glob(data_dir)
        tables_unsorted = [Table.load(path) for path in table_paths]
        tables_sorted = cls._sort(tables_unsorted)
        return {table.name: table for table in tables_sorted}

    @classmethod
    def _glob(cls, data_dir, ext=".tsv"):
        return glob(join(data_dir, f"*{ext}"))

    @classmethod
    def _sort(cls, tables):
        return sorted(tables, key=lambda table: table.name)


class Table:

    default_keys = {0: "weight", 1: "value", 2: "excludes", 3: "includes", 4: "source"}

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

        def capitalize(string):
            return " ".join([i.capitalize() for i in string.split("_")])

        def default_name():
            return splitext(basename(path))[0]

        def split_tsv(string, sep="\t"):
            return string.strip().split(sep)

        with open(path, "r") as fh:
            for line in fh:
                if line.startswith("##"):
                    header.update(dict([split_tsv(line[2:], "=")]))
                elif line.startswith("#"):
                    line = line[1:]
                    for n, i in enumerate(split_tsv(line)):
                        keys[n] = i
                else:
                    vals.append(split_tsv(line))

        name = header.get("NAME", default_name())
        label = header.get("LABEL", capitalize(name))
        keys = keys or cls.default_keys
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

    tables = TableLoader.load()
    preroll = {name: table.roll().value for name, table in tables.items()}

    if TABLE_ORDER_FILE:
        with open(TABLE_ORDER_FILE, "r") as fh:
            queue = [i.strip() for i in fh.readlines()]
    else:
        queue = sorted(table.name for table in tables)

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
