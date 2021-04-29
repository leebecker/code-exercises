from dataclasses import dataclass
from io import TextIOBase
from typing import AnyStr, List, Iterator, Optional

import argparse
import json
import sys


CASE_PREFIX = "Case: "
QUESTION_PREFIX = "Question: "
ANSWER_PREFIX = "- "
CASE_TERMINAL_LINE = "###"


class ItemParseError(Exception):
    pass


@dataclass
class Item:
    case: AnyStr
    question: AnyStr
    answers: List[AnyStr]

    @classmethod
    def next_item(cls, fp: TextIOBase) -> Optional["Item"]:
        # NOTE: This version assumes a well-formed Item with strict ordering
        # starting with Case, followed by one Question and then multiple answers
        # If anything violates this, an exception is thrown

        # NOTE: Using rstrip() to eliminate carriage return, but this will also
        # take out other trailing whitespace.

        # Find first non-whitespace line
        case_line = None
        for line in fp:
            if line.strip() != "":
                case_line = line
                break
        if not case_line:
            # Reached end of file without finding non-whitespace so return None
            return None

        # Check for Case Line
        if not case_line.startswith(CASE_PREFIX):
            raise ItemParseError(f"'{CASE_PREFIX}' does not start Item")
        case = case_line[len(CASE_PREFIX):]

        # Check for Question line
        question_line = fp.readline().rstrip()
        if not question_line.startswith(QUESTION_PREFIX):
            raise ItemParseError(
                f"Unexpected input.  Was expecting '{QUESTION_PREFIX}' line.\n"
                f"Received: {question_line}"
            )
        question = question_line[len(QUESTION_PREFIX):]

        # Look for answers
        answers = []
        for line in fp:
            line = line.rstrip()
            if line.rstrip() == CASE_TERMINAL_LINE:
                break
            elif line.startswith("- "):
                answers.append(line[len(ANSWER_PREFIX):])
            else:
                raise ItemParseError(
                    f"Unexpected input.  Was expecting '{CASE_TERMINAL_LINE}'.\n"
                    f"Received: {line}"
                )
        return Item(case=case, question=question, answers=answers)

    @classmethod
    def iter_items(cls, fin: TextIOBase) -> Iterator["Item"]:
        """
        Given a text file, iterate through
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
