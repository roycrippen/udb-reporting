from typing import Dict

import tree


def get_dep_on_dict(t: tree.UdbTree) -> Dict:
    deps = {}
    for arch in t.root.walk():
        for ent in arch.ent_children:
            deps[ent.uid] = ent.deps
    return deps


def get_dep_by_dict(deps: Dict) -> Dict:
    def get_bys(k):
        xs = {}
        for k1 in deps.keys():
            for k2, v in deps[k1].items():
                if k2 == k:
                    xs[k1] = v
        return xs

    bys = {}
    for uid, _deps in deps.items():
        bys[uid] = get_bys(uid)

    return bys


def get_ribbons_dict(t: tree.UdbTree) -> Dict:
    ribbons = {}
    for arch in t.root.walk():
        for ent in arch.ent_children:
            ribbons[ent.uid] = ent.metrics_ribbon
    return ribbons


def calc_circular_dependencies(deps: Dict, bys: Dict) -> Dict:
    circular_depends = {}
    for k1, vs in deps.items():
        for k2, v in bys[k1].items():
            if k2 in deps[k1].keys():
                if k1 in circular_depends.keys():
                    circular_depends[k1][k2] = deps[k1][k2]
                else:
                    circular_depends[k1] = {k2: deps[k1][k2]}
                if k2 in circular_depends.keys():
                    circular_depends[k2][k1] = v
                else:
                    circular_depends[k2] = {k1: v}

    return circular_depends


def rel_path(full: str, _dir: str) -> str:
    if full.startswith(_dir):
        return full[len(_dir):]
    else:
        return full


def get_link_to_file_metrics(dir_path: str, f_name: str) -> str:
    link_name = f_name.replace('.', '').lower()
    link = f'../Metrics/{dir_path}/zzz-file-metrics.md#{link_name}'
    return link


def get_link_within_file_metrics(ent_path: str, ref_path: str, f_name: str) -> str:
    if ref_path.find('/') > -1:
        pos = ref_path.find(f'/{f_name}')
    else:
        pos = 0

    link_name = f_name.replace('.', '').lower()
    backups = '../' * (len(ent_path.split('/')) - 1)
    link = f'{backups}{ref_path[:pos]}/zzz-file-metrics.md#{link_name}'
    return link
