#!/usr/bin/env python3

import sys
import sys
import sys
import sys
import argparse
from typeguard import typechecked
from typing import List, Optional  # Use List instead of list for Python 3.8
import deal
from pydantic import BaseModel
from annotated_types import Annotated, MinLen  # Use the Annotated from annotated-types

# Contract ensures the input is a string and output is a list of strings
# Don't need the type-checking contracts because we can use typechecked

@deal.post(lambda result: all(isinstance(x, str) for x in result))
@deal.ensure(lambda _: len(_.result) <= len(_.data))
@typechecked  # Is better than @deal.pre(lambda data: isinstance(data, str))
def process_data(data: str, keyword: str) -> List[str]:  # Add keyword as a parameter
    """Splits input into lines that contain the keyword"""
    return [line for line in data.splitlines() if keyword in line]



# Use annotated-types to add constraints
class FilterOptions(BaseModel):
    keyword: Annotated[str, MinLen(2)]  # keyword must be at least 2 characters
    limit: Optional[int] = None


def main():
    parser = argparse.ArgumentParser(description="Process and filter stdin data.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: filter
    filter_parser = subparsers.add_parser("filter", help="Filter lines with keyword.")
    filter_parser.add_argument("--keyword", required=True, help="Keyword to search")
    filter_parser.add_argument("--limit", type=int, help="Max allowed duplicates")

    args = parser.parse_args()

    if sys.stdin.isatty():
        print("Please provide piped input via stdin.", file=sys.stderr)
        sys.exit(1)

    raw_data = sys.stdin.read()

    # Ensure FilterOptions is correctly created
    options = FilterOptions(keyword=args.keyword, limit=args.limit)

    # Pass the keyword into process_data
    lines = process_data(raw_data, options.keyword)
    
    # Filter the lines based on the provided keyword
    filtered = [line for line in lines if options.keyword in line]

    # Handle the limit on duplicates if provided
    if options.limit:
        seen = {}
        output = []
        for line in filtered:
            seen[line] = seen.get(line, 0) + 1
            if seen[line] <= options.limit:
                output.append(line)
        print("\n".join(output))
    else:
        print("\n".join(filtered))



#test_process_data = deal.cases(process_data, check_types=true)
#test_process_data()

if __name__ == "__main__":
    main()
