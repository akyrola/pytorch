from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import sys
import torch
from torch._C import parse_schema


def check_bc(new_schema_dict):
    existing_schemas = torch._C._jit_get_all_schemas()
    for existing_schema in existing_schemas:
        print("processing existing schema: ", str(existing_schema))
        new_schemas = new_schema_dict.get(existing_schema.name, [])
        found = False
        for new_schema in new_schemas:
            if new_schema.is_backward_compatible_with(existing_schema):
                found = True
                break
        if not found:
            print('Can NOT find backward compatible schemas after changes '
                  'for schema {} from the following candidates:\n[\n{}\n]'
                  .format(
                      str(existing_schema),
                      "\n\t".join(str(s) for s in new_schemas)))
            print('The PR is introducing backward incompatible changes to the '
                  'operator library. Please contact PyTorch team to confirm '
                  'whether this change is wanted or not.')
            # TODO Print out more details about why candidates don't match.
            return False
    print('Found backward compatible schemas for all existing schemas')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '--new-schemas',
        help='filename to load new schemas',
        type=str,
        default='schemas.txt')
    args = parser.parse_args()
    new_schema_dict = dict()
    with open(args.new_schemas, 'r') as f:
        line = f.readline()
        while line:
            s = parse_schema(line.strip())
            line = f.readline()
            slist = new_schema_dict.get(s.name, [])
            slist.append(s)
            new_schema_dict[s.name] = slist

    if not check_bc(new_schema_dict):
        sys.exit(1)
