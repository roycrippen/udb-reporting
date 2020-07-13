import os
import sys
from typing import Dict

import understand

import reports_md
import reports_text
import tree
import utils


def run_reports():
    config_files = ['udb-reporting.yml', 'base.yml', 'mkdocs.yml']
    for f in config_files:
        if not os.path.isfile(f):
            sys.exit(f'File: "{f}" not found in current directory, aborting.')

    config = utils.read_yaml_settings(config_files[0])
    if config is None:
        sys.exit(f'Could not open yaml file "{config_files[0]}, aborting.')

    print(f'config file project name: {config["project_name"]}')
    # print_dict_as_yaml(config, 'udb-reporting.yml contents:')

    print('building tree...')
    db = understand.open(config['udb_name'])
    t = tree.UdbTree(db, config['languages'])

    print('running reports...')
    run_text_reports(config, t)
    run_md_reports(config, t)

    print('done.')


def run_md_reports(config: Dict, t: tree.UdbTree):
    print(f'    writing md files to: {config["out_dir_md"]}')

    out_dir = config['out_dir_md']
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    if not utils.rm_directory_and_files(out_dir):
        sys.exit(f'Could not remove files and dirs in "{out_dir}, aborting.')

    rs = [k for d in config['md_reports'] for k, v in d.items() if v]
    for r in rs:
        if hasattr(reports_md, r):
            if not getattr(reports_md, r)(config, t):
                sys.exit(f'File error attempting to write "{r}" report, aborting.')

    if not reports_md.write_index_md(out_dir, config['project_name']):
        sys.exit('File error attempting to write "index.html", aborting.')

    if not reports_md.write_mkdocs_yaml_file(out_dir):
        sys.exit('Could not create file "mkdocs.yml", aborting.')


def run_text_reports(config: Dict, t: tree.UdbTree):
    out_dir = config['out_dir_text']
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    if not utils.rm_directory_and_files(out_dir):
        sys.exit(f'Could not remove files and dirs in "{out_dir}, aborting.')

    rs = [k for d in config['text_reports'] for k, v in d.items() if v]
    for r in rs:
        if hasattr(reports_text, r):
            xs = getattr(reports_text, r)(config, t)
            if xs is not None and len(xs) > 0:
                xs = map(lambda x: x + '\n', xs)
                f_name = '{}{}.txt'.format(out_dir, r)
                print('    writing: {}'.format(f_name))
                if not utils.write_lines_to_file(f_name, xs):
                    sys.exit(f'Could not write file "{f_name}", aborting.')
        else:
            print(f'Could not find report: {r}')


def print_dict_as_yaml(d: Dict, heading: str):
    import yaml
    ys = yaml.dump(d, default_flow_style=False).split('\n')
    print(f'\n{heading}')
    for y in ys:
        print('    {}'.format(y))
    print()


if __name__ == u'__main__':
    run_reports()
