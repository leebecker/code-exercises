from dataclasses import dataclass, field
from io import TextIOBase
from typing import AnyStr, List, Iterator, Optional

import argparse
import json
import sys


CASE_PREFIX = "Case: "
QUESTION_PREFIX = "Question: "
ANSWER_PREFIX = "- "
ITEM_TERMINAL_LINE = "###"


@dataclass
class Item:

    case: AnyStr = None
    question: AnyStr = None
    answers: List[AnyStr] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not (self.case or self.question or self.answers)

    @classmethod
    def next_item(cls, fp: TextIOBase) -> Optional["Item"]:
        """
        Given an TextIO stream, read in the next Item
        """

        # create empty item
        item = Item()

        # For simplicity we read until we find an Item terminator.
        # Any properties get overwritten or appended
        for line in fp:
            # NOTE: Using rstrip() to eliminate carriage return, but this will
            # also take out other trailing whitespace.
            line = line.rstrip()
            if line == ITEM_TERMINAL_LINE:
                break
            elif line.startswith(CASE_PREFIX):
                item.case = line[len(CASE_PREFIX):]
            elif line.startswith(QUESTION_PREFIX):
                item.question = line[len(QUESTION_PREFIX):]
            elif line.startswith(ANSWER_PREFIX):
                item.answers.append(line[len(ANSWER_PREFIX):])

        if item.is_empty:
            # if no properties set on the item, return None
            return None
        else:
            return item

    @classmethod
    def iter_items(cls, fin: TextIOBase) -> Iterator["Item"]:
        """
        Given a text stream, iterate through
        """
        while True:
            item = cls.next_item(fin)
            if item:
                yield item
            else:
                return

    def to_dict(self):
        return self.__dict__


def main():
    parser = argparse.ArgumentParser(
        description="Reads in file, parses out Items and dumps JSON array of Items")
    parser.add_argument(
        "--file_in",
        help="path to input text file.  If unspecified will read from STDIN",
        default=None)
    parser.add_argument(
        "--file_out",
        help="path to output text file.  If unspecified will write to STDOUT",
        default=None)
    args = parser.parse_args()

    if args.file_in:
        with open(args.file_in, 'r') as fin:
            items = [_.to_dict() for _ in Item.iter_items(fin)]
    else:
        items = [_.to_dict() for _ in Item.iter_items(sys.stdin)]

    if args.file_out:
        with open(args.file_out, 'w') as fout:
            json.dump(items, fout)
    else:
        json.dump(items, sys.stdout)


if __name__ == "__main__":
    main()
