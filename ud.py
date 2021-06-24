# -*- coding: utf-8 -*-

import pprint
import json
import sys
from pathlib import Path

cwd = Path().absolute()

def read_umap(filename):
    root = {
        'Filename': str(filename),
        'Children': []
    }
    current = root # point to the current item
    flat_items = []

    with open(filename, encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            line = line.replace('\"', '')
            tokens = line.split()
            # print(tokens)
            if tokens[0] == 'Begin':
                inline_attributes = tokens[2:]
                new_child = True
                for att in inline_attributes:
                    (k, v) = att.split('=')
                    if k == 'Name':
                        # referencing existing item
                        for child in current['Children']:
                            if 'Name' in child and child['Name'] == v:
                                current = child
                                new_child = False
                                break
                if new_child:
                    typ = tokens[1]
                    parent = current
                    current = {
                        'Type': typ,
                        'Host': parent, 
                        'Children': []
                    }
                    flat_items.append(current)
                    parent['Children'].append(current)
                inline_attributes = tokens[2:]
                for att in inline_attributes:
                    (k, v) = att.split('=')
                    current[k] = v
            elif tokens[0] == 'End':
                current = current['Host']
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
        del item['Host']

    return root

def export_json(root):
    jsonStr = json.dumps(root, ensure_ascii=False, indent=2).encode('utf8')
    json_file = str(root['Filename']) + '.json'
    with open(json_file, 'w', encoding='utf-8') as fp:
        fp.write(jsonStr.decode())
        print("Written to %s" % json_file)

def get_node_name(node):
    if node['Type'] == 'Actor': return node['ActorLabel']
    if 'Name' in node: return node['Name']
    return ''

ingore_list = [
    'Type', 'Name', 'Children', 'Parent', 'ParameterStateId', 'AssetImportData', 'UCSSerializationIndex',
    'CreationMethod',
    'bNetAddressable',
    'DefaultSceneRoot',
    'FolderPath',
    'RootComponent',
    'StaticMeshDerivedDataKey',
    'AttachParent',
    'CreationMethod',
    'StaticMeshImportVersion',
    'ActorLabel',
]

def process_node(node, markdown, level = 1):
    if node['Type'] == 'Brush': return
    # if level > 4: return
    markdown.write('%s %s\n' % ('#' * level, get_node_name(node)))
    clazz = node['Class']
    if 'Landscape' in clazz or 'Occluder' in clazz:
        markdown.write('- Class: %s\n' % (clazz))
        return
    elif 'HierarchicalInstancedStaticMeshComponent' in clazz:
        for attr in node:
            if attr in ingore_list: continue
            if 'SortedInstances' in attr or 'InstanceReorderTable' in attr: continue
            markdown.write('- %s: %s\n' % (attr, node[attr]))
    else:
        for attr in node:
            if attr in ingore_list: continue
            markdown.write('- %s: %s\n' % (attr, node[attr]))
    for child in node['Children']:
        process_node(child, markdown, level + 1)

def generate_report(root):
    markdeep_head = """
    <meta charset="utf-8" emacsmode="-*- markdown -*-">
    <link rel="stylesheet" href="https://taptap.github.io/render-doctor/src/company-api.css?"">
    <script src="https://casual-effects.com/markdeep/markdeep.min.js?" charset="utf-8"></script>
    <style>
    .md h1 {
        color: #ff6600;  
    }
    </style>

    """
    html_file = str(root['Filename']) + '.html'
    with open(html_file, 'w', encoding='utf-8') as markdown:
        markdown.write(markdeep_head)
        markdown.write("**umap-doctor %s**\n\n" % (root['Filename']))

        level_0 = root['Children'][0]['Children'][0]
        for child in level_0['Children']:
            process_node(child, markdown)
        print("Written to %s" % html_file)

if __name__ == '__main__':
    umap_txt = cwd / 'sample/third.txt'
    if len(sys.argv) > 1:
        umap_txt = sys.argv[1]    
    root = read_umap(umap_txt)
    export_json(root)
    generate_report(root)

