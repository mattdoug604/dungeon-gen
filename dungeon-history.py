#!/usr/bin/env python

import random
import sys
from glob import glob
from os.path import dirname, join


TABLE_GLOB = glob(join(dirname(__file__), "tables", "*.tsv"))
with open(join(dirname(__file__), "tables", "order.txt"), "r") as fh:
    TABLE_ORDER = [i.strip() for i in fh.readlines()]


class Roll:
    def __init__(self, min_roll, max_roll, value, includes=None, excludes=None):
        self.min_roll = int(min_roll)
        self.max_roll = int(max_roll)
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
    def __init__(self, name, label, dice, data):
        self.name = name
        self.label = label
        self.dice = dice
        self.data = data

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
        dice = int(header["DICE"])
        data = [Roll(**{keys[n]:x for n, x in enumerate(i)}) for i in vals]

        return cls(name=name, label=label, dice=dice, data=data)

    def roll(self):
        num = random.randint(1, self.dice)
        obj = [i for i in self.data if i.min_roll <= num <= i.max_roll][0]
        self.last_roll = obj.value, obj.includes, obj.excludes
        return self.last_roll



tables = {}
last_roll = {}
for path in TABLE_GLOB:
    table = Table.load(path)
    tables[table.name] = table
    last_roll[table.name] = table.roll()[0]  # no recursion

queue = TABLE_ORDER
exclude = []
output = []
while queue:
    i = queue.pop(0)
    table = tables[i]
    value, includes, excludes = tables[i].last_roll
    value = value.format(**last_roll)
    if includes:
        queue = includes + queue
    if excludes:
        queue = [i for i in queue if i not in excludes]
    output.append({table.label: value})

for i in output:
    for key, val in i.items():
        print("{}: {}".format(key, val))