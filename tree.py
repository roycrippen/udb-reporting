import sys
from typing import List, Dict, Optional

import understand as u

import converters


class EntNode:
    def __init__(self, udb_ent: u.Ent, parent_path: str):
        self.uid: int = udb_ent.id()
        self.name: str = udb_ent.name()
        self.long_name: str = udb_ent.longname()
        self.kind: str = udb_ent.kind().name()
        self.kind_long_name: str = udb_ent.kind().longname()
        self.language: str = udb_ent.language()
        self.path: str = '{}/{}'.format(parent_path, self.name)
        self.metrics: Dict = converters.get_empty_metrics_dict()
        self.set_metrics(udb_ent)
        if self.kind not in ['File', 'Module File']:
            sys.exit('entity is not a file kind {}'.format(self.name))
        self.deps = {}
        for k, vs in udb_ent.depends().items():
            self.deps[k.id()] = len(vs)
        self.metrics_ribbon = []

    def set_metrics(self, udb_ent: u.Ent):
        # lookup udb metrics
        metrics = udb_ent.metric(list(self.metrics.keys()))
        metrics = dict((k, v) for k, v in metrics.items() if v is not None)
        for k, v in metrics.items():
            if type(v) == str:
                self.metrics[k]['val'] = float(v)
            else:
                self.metrics[k]['val'] = v

        # set badFix
        if 'MaxCyclomaticStrict' in self.metrics.keys() and self.metrics['MaxCyclomaticStrict']['val'] not in [None, 0]:
            self.metrics['badFix']['val'] = self.metrics['MaxCyclomaticStrict']['val']

        # remove unnecessary metrics
        remove_set = set()
        if self.metrics['CountStmt']['val'] == 0:
            remove_set.add('RatioCommentToCode')

        ls = ['CountStmt']
        remove_set = remove_set.union(k for k, v in self.metrics.items() if v['val'] == 0 and k not in ls)
        remove_set = remove_set.union(set(k for (k, v) in self.metrics.items() if v['val'] is None))
        for m in remove_set:
            del self.metrics[m]

        # score the remaining metrics
        converters.score_metrics(self.metrics)


class ArchNode:
    def __init__(self, u_item: u.Arch, parent_path: str):
        self.name: str = u_item.name()
        self.arch_children: List[ArchNode] = []
        self.ent_children: List[EntNode] = []
        self.level: int = 0
        self.path: str = f'{parent_path}/{self.name}'
        self.metrics: Dict[str, Dict[Optional[float], str]] = converters.get_empty_metrics_dict()
        self.metrics_ribbon = []

    def walk(self):
        yield self
        for child in self.arch_children:
            yield from child.walk()

    def bottom_walk(self):
        for child in self.arch_children:
            yield from child.bottom_walk()
        yield self

    def rollup_metrics(self, level: int = 0):
        mss = []
        for arch in self.arch_children:
            arch.rollup_metrics(level=(level + 1))
            mss.append(arch.metrics)

        for ent in self.ent_children:
            mss.append(ent.metrics)

        converters.rollup_metrics_arch(self.metrics, mss)
        converters.score_metrics(self.metrics)


class UdbTree:
    db: u.Db = None
    metric_keys: Dict[str, str] = {}
    uids: Dict[int, EntNode] = {}
    languages: List[str] = ["Ada", "C++", "C#", "Fortran", "Java", "Jovial", "Pascal", "Plm", "Python", "VHDL", "Web"]

    def __init__(self, db: u.Db, languages: List[str], arch_type='Directory Structure'):
        root_archs = db.root_archs()
        for arch in root_archs:
            if len(root_archs) == 1 or arch_type == arch.name():
                self.db = db
                self.languages = languages
                root_arch = arch
                self.root = ArchNode(root_arch, '')
                self._build_tree(root_arch)

    def _build_tree(self, arch: u.Arch):
        def go(p: ArchNode, udb_arch: u.Arch):
            def keep_node() -> bool:
                ent_children_cnt = len([v for v in udb_arch_child.ents() if v.language() in self.languages])
                arch_children_cnt = len(udb_arch_child.children())
                return (ent_children_cnt + arch_children_cnt) != 0

            for udb_arch_child in udb_arch.children():
                if keep_node():
                    node = ArchNode(udb_arch_child, udb_arch.longname())
                    node.level = p.level + 1
                    go(node, udb_arch_child)
                    for ent in udb_arch_child.ents():
                        e = EntNode(ent, node.path)
                        node.ent_children.append(e)
                    p.arch_children.append(node)
                else:
                    print(f'   -> not adding node: {udb_arch_child.longname()}')

        go(self.root, arch)
        self._filter_languages()
        self._rollup_metrics()
        self._populate_metric_key_dict()
        self._populate_metric_ribbons()
        self._populate_uid_dict()

    def _filter_languages(self):
        for arch in self.root.walk():
            arch.ent_children = [ent for ent in arch.ent_children if ent.language in self.languages]

    def _rollup_metrics(self):
        if hasattr(self, 'root'):
            self.root.rollup_metrics()
        else:
            print('oh no, invalid tree structure')

    def _populate_uid_dict(self):
        for arch in self.root.walk():
            for ent in arch.ent_children:
                self.uids[ent.uid] = ent

    def _populate_metric_key_dict(self):
        def process_metrics(ms: Dict[str, Dict[float, str]]):
            for k, v in ms.items():
                metric_set.add(k)

        metric_set = set()
        for arch in self.root.walk():
            process_metrics(arch.metrics)
            for ent in arch.ent_children:
                process_metrics(ent.metrics)
        xs = sorted(list(metric_set))
        letters = [chr(x) for x in range(ord('A'), ord('A') + len(xs))]
        for (x, letter) in zip(xs, letters):
            self.metric_keys[x] = letter

    def _populate_metric_ribbons(self):
        def get_ribbon(metric):
            ribbon = []
            for k, v in xs:
                if k in metric:
                    div = converters.get_color_div(metric[k]['color'], metric[k]['val'])
                else:
                    div = '-'
                ribbon.append(f'|{div}')
            ribbon.append('|')
            return ''.join(ribbon)

        xs = sorted(self.metric_keys.items())
        for arch in self.root.walk():
            arch.metrics_ribbon = get_ribbon(arch.metrics)
            for ent in arch.ent_children:
                ent.metrics_ribbon = get_ribbon(ent.metrics)
        pass

    def show_metric_keys_table(self):
        h1 = '| Letter | Metric | Green Range | Yellow Range| Red Range|\n'
        h2 = '|:---    |        |:---:    |:---:    |:---:    |\n'
        rs = ['\n\n\n###Metric Keys\n\n', h1, h2]
        for k, v in sorted(list(self.metric_keys.items()), key=lambda tup: tup[1]):
            grn_str, yel_str, red_str = converters.metric_key_range_str(k)
            rs.append(f'|{v}|{k}|{grn_str}|{yel_str}|{red_str}|\n')
        return rs
