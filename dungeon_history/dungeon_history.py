#!/usr/bin/env python
import random
from glob import glob
from os.path import basename, dirname, join, splitext

TABLE_DATA_DIR = join(dirname(__file__), "data")
TABLE_ORDER_FILE = join(dirname(__file__), "data", "order.txt")

DEFAULT_COLUMNS = ["value", "weight", "excludes", "includes", "source"]


class Roll:
    def __init__(self, value, weight=None, includes=None, excludes=None, source=None, **kwargs):
        self.value = value
        self.weight = float(weight) if weight is not None else 0.0
        self.includes = includes.split(" ") if includes is not None else []
        self.excludes = excludes.split(" ") if excludes is not None else []
        self.source = source if source is not None else ""


class TableLoader:
    @classmethod
    def load(cls, data_dir=TABLE_DATA_DIR, order_file=TABLE_ORDER_FILE):
        table_paths = cls._glob(data_dir)
        tables_unsorted = [Table.load_tsv(path) for path in table_paths]
        tables_sorted = cls._sort(tables_unsorted)
        return {table.name: table for table in tables_sorted}

    @classmethod
    def _glob(cls, data_dir, ext=".tsv"):
        return glob(join(data_dir, f"*{ext}"))

    @classmethod
    def _sort(cls, tables):
        return sorted(tables, key=lambda table: table.name)


class Table:
    def __init__(self, name, label, data, weights):
        self.name = name
        self.label = label
        self.data = data
        self.weights = weights
        self.last_roll = None

    @classmethod
    def load_tsv(cls, path, label=None, name=None):
        def default_name():
            return splitext(basename(path))[0]

        def default_label():
            return " ".join([i.capitalize() for i in default_name().split("_")])

        header, columns, rows = cls._parse_tsv(path)
        columns = columns or {n: i for n, i in enumerate(DEFAULT_COLUMNS)}
        name = name or header.get("NAME") or default_name()
        label = label or header.get("LABEL") or default_label()
        data = []
        for row in rows:
            kwargs = {columns[n]: x if x != "" else None for n, x in enumerate(row)}
            data.append(Roll(**kwargs))
        total = len(data)
        weights = [i.weight / total for i in data]

        return cls(name=name, label=label, data=data, weights=weights)

    @classmethod
    def _parse_tsv(cls, path):
        header = {}
        columns = {}
        rows = []

        def split(line, sep="\t"):
            return line.strip().split(sep)

        with open(path, "r") as fh:
            for line in fh:
                if line.startswith("##"):
                    header.update(dict([split(line[2:], "=")]))
                elif line.startswith("#"):
                    line = line[1:]
                    for n, i in enumerate(split(line)):
                        columns[n] = i
                else:
                    rows.append(split(line))

        return header, columns, rows

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
        output.append((table.label, value))

    left_spacing = max((len(i[0]) for i in output)) + 2
    for key, val in output:
        key_str = f"{key}: "
        print(f"{key_str:{left_spacing}}{val}")


if __name__ == "__main__":
    main()
