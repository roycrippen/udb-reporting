import os
from typing import Union, Iterable, List, Dict, Optional

import yaml


def int_or_zero(s: str) -> int:
    try:
        return int(s)
    except ValueError:
        return 0


def is_between(n: Union[int, float], x: Union[int, float], y: Union[int, float]) -> bool:
    return x <= n <= y


def remove_prefix(text: str, prefix: str) -> str:
    return text[text.startswith(prefix) and len(prefix):]


def remove_postfix(text: str, post: str) -> str:
    if text.endswith(post):
        return text[:-len(post)]
    else:
        return text


def read_yaml_settings(file: str) -> Optional[Dict]:
    try:
        with open(file, "r") as read_file:
            return yaml.load(read_file, Loader=yaml.FullLoader)
    except OSError:
        return None


def rm_directory_and_files(path: str) -> bool:
    if path != '/':
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except NotImplementedError:
                    return False
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except NotImplementedError:
                    return False
    return True


def write_lines_to_file(f_name: str, xs: Iterable) -> bool:
    try:
        with open(f_name, 'w') as fs:
            fs.writelines(xs)
            return True
    except OSError:
        return False


def yml_list_from_directory(directory: str) -> List[str]:
    def read_top_name(f_name: str) -> Optional[str]:
        try:
            with open(f_name, "r") as fp:
                line = fp.readline()
                while line:
                    if line.startswith('# '):
                        return line[2:].rstrip()
                    else:
                        line = fp.readline()
                return None
        except OSError:
            return None

    def go(_dir: str, rel_dir: str, spaces: str, xs: List[str]):
        if not os.path.isdir(_dir):
            return []

        fps = [(f, os.path.isfile(_dir + f)) for f in os.listdir(_dir)]
        fps.sort(key=lambda tup: (not tup[1], tup[0]))
        for f, is_file in fps:
            fp = _dir + f
            if is_file:
                top_name = read_top_name(fp)
                if top_name is None:
                    return []
                val = f'{spaces}- {top_name}: {rel_dir + f}\n'
                xs.append(val)
            else:
                val = f'{spaces}- {f}:\n'
                xs.append(val)
                go(fp + '/', f'{rel_dir}{f}/', spaces + '    ', xs)
        return xs

    if not directory.endswith('/'):
        directory += '/'

    ls = ['nav:\n']
    go(directory, '', '', ls)
    if ls == ['nav:\n']:
        print(f'Error reading contents of "{directory}" directory.')
        return []

    pos = -1
    for i, l in enumerate(ls):
        if l.endswith('index.md\n'):
            pos = i
            break
    if pos != -1:
        ls.insert(1, ls.pop(pos))

    return ls
