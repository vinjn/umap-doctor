# -*- coding: utf-8 -*-

import pprint
import json
import sys
import pathlib

cwd = pathlib.Path().absolute()

def process_umap(file_name):
    root = {
        'children': []
    }
    current = root # point to the current item
    flat_items = []

    with open(file_name, encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            line = line.replace('\"', '')
            tokens = line.split()
            # print(tokens)
            if tokens[0] == 'Begin':
                typ = tokens[1]
                parent = current
                current = {
                    'type': typ,
                    'parent': parent, 
                    'children': []
                }
                inline_attributes = tokens[2:]
                for att in inline_attributes:
                    (k, v) = att.split('=')
                    current[k] = v
                flat_items.append(current)
                parent['children'].append(current)
            elif tokens[0] == 'End':
                current = current['parent']
            else:
                # case: non-inline attribute
                splits = line.split('=')
                if len(splits) == 2:
                    k = splits[0]
                    v = splits[1]
                    if 'INVTEXT' in v:
                        a = 0
                    current[k] = v

    for item in flat_items:
        del item['parent']

    jsonStr = json.dumps(root, ensure_ascii=False, indent=2).encode('utf8')
    json_file = str(file_name) + '.json'
    with open(json_file, 'w', encoding='utf-8') as fp:
        fp.write(jsonStr.decode())
        print("Written to %s" % json_file)

if __name__ == '__main__':
    umap_txt = cwd / 'third.txt'
    if len(sys.argv) > 1:
        umap_txt = sys.argv[1]    
    process_umap(umap_txt)
