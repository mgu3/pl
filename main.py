import csv
import re
from pprint import pprint

INFILE = "/Users/guthrie/Downloads/new PL layout.csv"
SPLIT_FILE = "splits.csv"

# Dates starting from col 2
DATE_LIST = [
    "Jan-2021",
    "Feb-2021",
    "Mar-2021",
    "Apr-2021",
    "May-2021",
    "Jun-2021",
    "Jul-2021",
    "Aug-2021",
    "Sep-2021",
    "Oct-2021",
    "Nov-2021",
    "Dec-2021",
]

# Some numbers should be negative but are positive in the spreadsheet
REVERSE_LIST = [
    "Direct Costs to run above Bridge Streams",
    "Overheads",
]

PROFIT_CENTRES = {
    "el": "East Lindfield",
    "wi": "The Willis",
    "rb": "Real Bridge",
    "iv": "Investments",
    "nr": "North Ryde",
    "le": "Lessons",
}


def _get_int(string):
    try:
        return int(string)
    except ValueError:
        return 0


def _as_number(string):

    # delete any commas
    string = string.replace(",", "")

    # find matching numbers
    match = re.findall("\d+\.\d+", string)

    # if we found one then use it
    number = float(match[0]) if match else 0.0

    # Negative numbers are show as (555)
    if string.find("(") >= 0:
        number = -number

    return number


def is_empty_row(row):
    """Check if there is nothing in this list"""
    return all(item == "" for item in row)


def reformat_blocks(blocks, splits_dic):
    """ reformat a block of code from excel. block is a list of lines"""

    print("Main Heading, Line Item, Month, Value, ", end="")
    for profit_centre in PROFIT_CENTRES:
        print(f"{PROFIT_CENTRES[profit_centre]}, ", end="")
    print()

    for block in blocks:
        multiplier = -1 if block in REVERSE_LIST else 1

        for row in blocks[block]:

            title = row[0]

            # Skip Accounts row
            if title.find("Account Name") >= 0:
                continue

            for i, item in enumerate(row[1:]):
                date_part = DATE_LIST[i]
                number_part = _as_number(item) * multiplier

                splits_list = splits_dic[block][title]

                print(f"{block}, {title}, {date_part}, {number_part}, ", end="")

                for profit_centre in PROFIT_CENTRES:

                    if number_part != 0 and splits_list[profit_centre] != 0:
                        this_split = number_part * splits_list[profit_centre] / 100.0
                    else:
                        this_split = 0
                    print(f"{this_split:.2f}, ", end="")

                print()

                if i == 11:
                    break


def read_blocks():
    """ Read Excel file and reformat """
    with open(INFILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        block = []
        blocks = {}
        heading = None
        for row in csv_reader:

            # If we get a blank row then we are finished this block
            if is_empty_row(row):
                blocks[heading] = block
                block = []
                continue

            # If we get an empty row apart from first column then first column is the heading
            if is_empty_row(row[1:]):
                heading = row[0]

                continue

            # Normal row
            block.append(row)

        return blocks


def splits():
    """ read splits from reference file"""

    splits_dic = {}

    with open(SPLIT_FILE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")

        # Skip header
        next(csv_reader, None)

        for row in csv_reader:
            if row[0] == "":
                continue

            main_heading, line_item, el, wi, rb, iv, nr, le = row[:8]

            if main_heading not in splits_dic:
                splits_dic[main_heading] = {}

            if line_item not in splits_dic[main_heading]:
                splits_dic[main_heading][line_item] = {}

            splits_dic[main_heading][line_item]["el"] = _get_int(el)
            splits_dic[main_heading][line_item]["wi"] = _get_int(wi)
            splits_dic[main_heading][line_item]["rb"] = _get_int(rb)
            splits_dic[main_heading][line_item]["iv"] = _get_int(iv)
            splits_dic[main_heading][line_item]["nr"] = _get_int(nr)
            splits_dic[main_heading][line_item]["le"] = _get_int(le)

    return splits_dic


def main():

    splits_dic = splits()
    blocks = read_blocks()
    reformat_blocks(blocks, splits_dic)


if __name__ == '__main__':
    main()
