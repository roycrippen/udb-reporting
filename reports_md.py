import os
import shutil
from itertools import groupby

import converters
import utils
from utils_reports import *


# markdown reports

# noinspection DuplicatedCode
def circular_file_refs(config, t: tree.UdbTree) -> bool:
    deps = get_dep_on_dict(t)
    bys = get_dep_by_dict(deps)
    circular_depends = calc_circular_dependencies(deps, bys)
    ribbons = get_ribbons_dict(t)

    ribbon_h1_left = "".join(f'|{x}' for x in sorted(t.metric_keys.values()))
    ribbon_h1_right = ribbon_h1_left[1:] + '|'
    ribbon_h2_left = '| ---:' * len(t.metric_keys) + ' '
    ribbon_h2_right = ribbon_h2_left[1:] + '|'

    header1 = f'{ribbon_h1_left}|File 1  |  Dep Cnt |     | Dep Cnt |File 2 |{ribbon_h1_right}\n'
    header2 = f'{ribbon_h2_left}|:---    |   :---:  |:---:|  :---:  |:---   |{ribbon_h2_right}\n'

    rs = ['# Direct Circular File References\n\n']
    rs.extend(t.show_metric_keys_table())
    rs.extend(['\n\n### Circular References\n\n', header1, header2])
    uniques = set()
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
            name1 = k1_s.split('/')[-1]
            rel = k1_s.replace(f'/{name1}', '')
            link1 = get_link_to_file_metrics(rel, name1)
            v1 = vs[k2]

            k2_s = t.uids[k2].path.replace('Directory Structure/', '')
            name2 = k2_s.split('/')[-1]
            rel = k2_s.replace(f'/{name2}', '')
            link2 = get_link_to_file_metrics(rel, name2)
            v2 = circular_depends[k2][k1]

            ribbon_l = ribbons[k1]
            ribbon_r = ribbons[k2]
            rs.append(f'{ribbon_l}[{k1_s}]({link1})|{v1:3}| <==> |{v2:3}|[{k2_s}]({link2}){ribbon_r}\n')

    if len(rs) == 2:
        rs.append('No tree to output.\n')

    if len(rs) > 40:
        rs.extend(t.show_metric_keys_table())

    out_dir = f'{config["out_dir_md"]}Reports/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    f_name = f'{out_dir}circular_file_refs.md'
    return utils.write_lines_to_file(f_name, rs)


# noinspection DuplicatedCode
def file_list_indented_sloc(config, t: tree.UdbTree) -> bool:
    # base_path = config['udb_source_root']
    indent = '&nbsp;' * 4

    ribbon_h1 = "".join(f'{x}|' for x in sorted(t.metric_keys.values()))
    ribbon_h2 = ' ---:|' * len(t.metric_keys) + ' '
    header1 = f'|Path {indent * 10} |{indent * 3}SLOC|{ribbon_h1}\n'
    header2 = f'|:---             |---:   |{ribbon_h2}\n'

    rs = ['# File List Indented\n\n']
    rs.extend(t.show_metric_keys_table())
    rs.extend(['\n\n### File List\n\n', header1, header2])

    for arch in t.root.walk():
        if arch.name == 'Directory Structure':
            link = '(../Metrics/application-metrics.md)'
        else:
            path = arch.path.replace('Directory Structure/', '')
            parts = path.split('/')
            tail = parts[-1]
            link = f'(../Metrics/{path}/{tail}-metrics.md)'
        ribbon = arch.metrics_ribbon
        sloc = arch.metrics['CountStmt']['val']
        rs.append(f"|{arch.level * indent}[{arch.name:30s}]{link}|{sloc:5,}{ribbon}\n")
        for ent in arch.ent_children:
            spaces = (arch.level + 1) * indent
            ent_sloc = ent.metrics['CountStmt']['val']
            rel = arch.path.replace('Directory Structure/', '')
            link = get_link_to_file_metrics(rel, ent.name)
            ribbon = ent.metrics_ribbon
            rs.append(f"|{spaces}[{ent.name:30s}]({link})|{ent_sloc:5,}{ribbon}\n")

    if len(rs) == 2:
        rs.append('No tree to output.\n')

    if len(rs) > 40:
        rs.extend(t.show_metric_keys_table())

    out_dir = f'{config["out_dir_md"]}Reports/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    f_name = f'{out_dir}file_list_indented_sloc.md'
    return utils.write_lines_to_file(f_name, rs)


def red_metrics(config, t: tree.UdbTree) -> bool:
    # base_path = config['udb_source_root']
    header1 = '|Path    |  Value|    SLOC|\n'
    header2 = '|:---             |---:   |---:    |\n'
    rs = ['# Red Metrics\n\n']
    rs.extend(converters.metric_key_range_table())

    xs = []
    for arch in t.root.walk():
        for ent in arch.ent_children:
            for k, v in ent.metrics.items():
                (val, color) = (v['val'], v['color'])
                if color == 'red':
                    # aaa = rel_path(ent.long_name, base_path)
                    rel = arch.path.replace('Directory Structure/', '')
                    link = get_link_to_file_metrics(rel, ent.name)
                    xs.append((k, f'{rel}/{ent.name}', val, ent.metrics['CountStmt']['val'], link))

    xs.sort(key=lambda tup: tup[0])
    for key, group in groupby(xs, lambda x: x[0]):
        rs.extend([f'\n## {key}\n', header1, header2])
        ts = [x for x in group]
        if key == 'RatioCommentToCode':
            ts.sort(key=lambda tup: tup[2])
        else:
            ts.sort(key=lambda tup: tup[2], reverse=True)
        for t in ts:
            rs.append(f'|[{t[1]}]({t[4]})|{t[2]:,}|{t[3]:,}|\n')

    if len(rs) > 40:
        rs.extend(converters.metric_key_range_table())

    out_dir = f'{config["out_dir_md"]}Reports/'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    f_name = f'{out_dir}red_metrics.md'
    return utils.write_lines_to_file(f_name, rs)


# noinspection DuplicatedCode
def metrics(config, t: tree.UdbTree) -> bool:
    def write(_dir, _file, _ms) -> bool:
        if not os.path.exists(_dir):
            os.makedirs(_dir)
        return utils.write_lines_to_file(_file, _ms)

    out_dir = f'{config["out_dir_md"]}Metrics'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    base_path = config['udb_source_root']
    deps = get_dep_on_dict(t)
    bys = get_dep_by_dict(deps)
    header_depends_on = '\n|Depends ON    |  Count|\n'
    header_depends_by = '\n|Depends BY    |  Count|\n'
    header_data = '|:---             |---:   |\n'

    for arch in t.root.walk():
        # write directory level md files
        path = utils.remove_prefix(arch.path, 'Directory Structure')
        if arch == t.root:
            new_out_dir = out_dir
            f_name = f'{out_dir}/application-metrics.md'
            rs = ['# Application Metrics\n']
        else:
            new_out_dir = f'{out_dir}{path}'
            f_name = f'{new_out_dir}/{arch.name}-metrics.md'
            rs = [f'# {arch.name} Metrics\n']
        rs.extend(converters.get_metric_markdown(arch.metrics))
        if not write(new_out_dir, f_name, rs):
            return False

        # write file level md files
        if len(arch.ent_children) == 0:
            continue

        pos = f_name.rfind('/')
        t_str = f_name[:pos]
        f_name = t_str + '/zzz-file-metrics.md'
        rs = ['# File Metrics and Dependencies\n\n']
        for ent in arch.ent_children:
            # metrics
            full_name = rel_path(ent.long_name, base_path)
            rs.append(f'## {ent.name}\n')
            rs.append(f'full path ==> {full_name}\n\n')
            rs.extend(converters.get_metric_markdown(ent.metrics))

            # dependencies
            # dep_ons = list(ent.deps.items())
            dep_ons = [(t.uids[k].path, v) for k, v in ent.deps.items()]
            if len(dep_ons) > 0:
                rs.extend([header_depends_on, header_data])
                dep_ons.sort(key=lambda r: r[0])
                for dep in dep_ons:
                    # rel = rel_path(dep[0], base_path)
                    rel = dep[0].replace('Directory Structure/', '')
                    link = get_link_within_file_metrics(path, rel, rel.split('/')[-1])
                    rs.append(f'|[{rel}]({link})|{dep[1]:6}|\n')
                rs.append('\n&nbsp;\n')

            dep_bys = [(t.uids[k].path, v) for k, v in bys[ent.uid].items()]
            if len(dep_bys) > 0:
                rs.extend([header_depends_by, header_data])
                dep_bys.sort(key=lambda r: r[0])
                for d_by in dep_bys:
                    # rel = rel_path(d_by[0], base_path)
                    rel = d_by[0].replace('Directory Structure/', '')
                    link = get_link_within_file_metrics(path, rel, rel.split('/')[-1])
                    rs.append(f'|[{rel}]({link})|{d_by[1]:6}|\n')
                rs.append('\n&nbsp;\n')
            rs.append('\n\n')

        if not write(new_out_dir, f_name, rs):
            return False

    return True


def write_index_md(path, project) -> bool:
    rs = [
        '# Usage\n',
        f'Reporting for {project}\n',
        'Static site generated by Mkdocs from custom Python scripts and a Scitools Understand database\n'
        '### Reports\n',
        '* Direct Circular File References\n',
        '    1. File 1 depends on File 2 Count times\n',
        '    2. File 2 depends on File 1 Count times\n',
        '* File List Indented\n',
        '    1. Indented source file listing\n',
        '    2. Includes cumulative SLOC count\n',
        '* Red Metrics\n',
        '    1. Listing by metric type for files that contain at least one red metric\n',
        '    2. for item(s) within the file\n',
        '### Searches\n',
        '* Searches do not work when opening site/index.html file directly from web browser\n',
        '* Searches worked when opening site/index.html file from web server\n',
        '    1. In terminal window move to ```site``` directory\n',
        '    2. Start web server at command prompt: ```python3 -m http.server```\n',
        '    3. Open ```http://127.0.0.1:8000/index.html``` in web browser\n',
        '### Metrics\n',
        '* Summarized and scored metrics\n',
        '* Rolled up for all directories below current\n',
    ]
    rs.extend(converters.metric_key_range_table())
    f_name = f'{path}/index.md'
    return utils.write_lines_to_file(f_name, rs)


def write_mkdocs_yaml_file(docs_directory) -> bool:
    yml_directory = utils.remove_postfix(docs_directory, 'docs/')
    base_file = yml_directory + 'base.yml'
    mkdocs_file = yml_directory + 'mkdocs.yml'
    if os.path.isfile(base_file):
        shutil.copyfile(base_file, mkdocs_file)
    else:
        print(f'Could not find base.yml file in {yml_directory}.')
        return False

    try:
        with open(mkdocs_file, 'a') as file:
            ls = utils.yml_list_from_directory(docs_directory)
            if len(ls) > 0:
                file.writelines(ls)
                return True
            else:
                print('Call to "utils.yml_list_from_directory" failed.')
                return False
    except OSError:
        print(f'Could open file {mkdocs_file}.')
        return False
