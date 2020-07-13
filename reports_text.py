from itertools import groupby

from utils_reports import *


# text reports

def file_list_indented_sloc_text(_config, t: tree.UdbTree):
    indent = '    '

    head = 'File List Indented'
    rs = [head, '=' * len(head)]

    for arch in t.root.walk():
        sloc = arch.metrics['CountStmt']['val']
        rs.append(f"{arch.level * indent}{arch.name:30s} [sloc: {sloc:5,}]")
        for ent in arch.ent_children:
            spaces = (arch.level + 1) * indent
            ent_sloc = ent.metrics['CountStmt']['val']
            rs.append(f"{spaces}{ent.name:30s} [sloc: {ent_sloc:5,}]")

    if len(rs) == 2:
        rs.append('No tree to output.')
    return rs


def red_metrics_text(config, t: tree.UdbTree):
    base_path = config['udb_source_root']
    header = 'Red Metrics by Type'
    rs = [header, '=' * len(header)]

    xs = []
    for arch in t.root.walk():
        for ent in arch.ent_children:
            for k, v in ent.metrics.items():
                (val, color) = (v['val'], v['color'])
                if color == 'red':
                    rel = rel_path(ent.long_name, base_path)
                    xs.append((k, rel, val, ent.metrics['CountStmt']['val']))

    path_len = 10 + max(len(x[1]) for x in xs)
    header1 = f'{"Path":{path_len}s}Value     SLOC'
    header2 = '=' * len(header1)

    xs.sort(key=lambda tup: tup[0])
    for key, group in groupby(xs, lambda x: x[0]):
        rs.extend([f'\n{key}', header1, header2])
        ts = [x for x in group]
        if key == 'RatioCommentToCode':
            ts.sort(key=lambda tup: tup[2])
        else:
            ts.sort(key=lambda tup: tup[2], reverse=True)
        for t in ts:
            rs.append(f'{t[1]:{path_len}s}{t[2]:6}{t[3]:8,}')

    if len(rs) == 2:
        rs.append('None.')
    return rs


# noinspection DuplicatedCode
def circular_file_refs_text(_config, t: tree.UdbTree):
    deps = get_dep_on_dict(t)
    bys = get_dep_by_dict(deps)
    circular_depends = calc_circular_dependencies(deps, bys)

    uniques = set()
    ts = []
    for k1, vs in circular_depends.items():
        for k2 in vs.keys():
            # ensure no duplicates
            ls = [k1, k2]
            ls.sort()
            composite_key = f'{ls[0]}-{ls[1]}'
            if composite_key in uniques:
                continue

            uniques.add(composite_key)
            k1_s = t.uids[k1].path.replace('Directory Structure/', '')
            v1 = vs[k2]

            k2_s = t.uids[k2].path.replace('Directory Structure/', '')
            v2 = circular_depends[k2][k1]
            ts.append((k1_s, v1, v2, k2_s))

    if len(ts) == 0:
        return ['Direct Circular File References\n\n', 'No circular references to output.\n']

    path_len = 5 + max(max(len(x[0]), len(x[3])) for x in ts)
    header = f'{"File 1":{path_len}} Dep Cnt          Dep Cnt    {"File 2":{path_len}}'
    rs = ['Direct Circular File References\n\n', header, '=' * len(header)]
    for k1, v1, v2, k2 in ts:
        rs.append(f'{k1:{path_len}}{v1:8,}    <===>{v2:8,}    {k2:{path_len}}')

    if len(rs) == 2:
        rs.append('No tree to output.\n')

    return rs
