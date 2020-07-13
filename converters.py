from utils import is_between
from typing import Dict, Optional, List, Union, Tuple


def get_color_div(color: str, value: Optional[float]) -> str:
    low_color = color.lower()
    if value is None:
        val_str = '-'
    else:
        val_str = f'{value:,}'

    if low_color in ['red', 'yellow', 'green']:
        return f'<div title="{low_color}"> {val_str} </div>'
    else:
        return val_str


def get_metric_markdown(metrics) -> List[str]:
    header1 = '| Metric | Value |\n'
    header2 = '| :--- | ---: |\n'
    rs = [header1, header2]
    for (k, v) in sorted(list(metrics.items())):
        if v['val'] is not None:
            s = '| {} | {} |\n'
            val_str = get_color_div(v['color'], value=v['val'])
            rs.append(s.format(k, val_str))
    rs.append('\n&nbsp;\n')
    return rs


def rollup_metrics_arch(metrics: Dict, mss: List[Dict]):
    if len(mss) == 0:
        return

    sloc = 0
    min_c2c = 999
    for ms in mss:
        for (k, obj) in ms.items():
            v = obj['val']
            if v is not None:
                if k == 'CountStmt':
                    sloc += v
                elif k == 'RatioCommentToCode':
                    min_c2c = min(min_c2c, v)
                else:
                    if metrics[k]['val'] is not None:
                        metrics[k]['val'] = max(metrics[k]['val'], v)
                    else:
                        metrics[k]['val'] = v
    metrics['CountStmt']['val'] = sloc
    if min_c2c != 999:
        metrics['RatioCommentToCode']['val'] = min_c2c


def get_empty_metrics_dict() -> Dict:
    ms = ['badFix', 'CountStmt', 'MaxCyclomaticStrict', 'MaxEssential', 'MaxInheritanceTree', 'MaxNesting',
          'RatioCommentToCode', 'CountDeclClass', 'CountDeclFunction', 'PercentLackOfCohesion']

    res: Dict[(Optional[int], str)] = dict((m, {'val': None, 'color': 'white'}) for m in ms)
    res['CountStmt']['val'] = 0
    return res


def score_cyclo(val: Optional[Union[int, float]]) -> str:
    if val is None:
        return 'white'
    elif is_between(val, 0, 4):
        return 'green'
    elif is_between(val, 4, 10):
        return 'yellow'
    elif is_between(val, 10, 20):
        return 'yellow'
    elif is_between(val, 20, 50):
        return 'red'
    else:
        return 'red'


def cyclo_to_bad_fix(val: Optional[Union[int, float]]) -> Optional[int]:
    if val is None:
        return None
    elif is_between(val, 1, 10):
        return 5
    elif is_between(val, 10, 20):
        return 10
    elif is_between(val, 20, 30):
        return 20
    elif is_between(val, 30, 50):
        return 30
    elif is_between(val, 50, 50):
        return 40
    else:
        return 60


def score_bad_fix(_val: Optional[Union[int, float]]) -> str:
    val = cyclo_to_bad_fix(_val)
    if val is None:
        return 'white'
    elif is_between(val, 0, 10):
        return 'green'
    elif is_between(val, 10, 20):
        return 'green'
    elif is_between(val, 20, 30):
        return 'yellow'
    elif is_between(val, 30, 50):
        return 'yellow'
    elif is_between(val, 50, 80):
        return 'red'
    else:
        return 'red'


def score_sloc(val: Optional[Union[int, float]]) -> str:
    if val is None:
        color = 'white'
    elif is_between(val, 0, 100):
        color = 'green'
    elif is_between(val, 100, 200):
        color = 'yellow'
    elif is_between(val, 200, 500):
        color = 'red'
    else:
        color = 'red'

    return color


def score_essential(val: Optional[Union[int, float]]) -> str:
    if val is None:
        color = 'white'
    elif is_between(val, 0, 4):
        color = 'green'
    elif is_between(val, 4, 10):
        color = 'yellow'
    else:
        color = 'red'

    return color


def score_nesting(val: Optional[Union[int, float]]) -> str:
    if val is None:
        color = 'white'
    elif is_between(val, 0, 2):
        color = 'green'
    elif is_between(val, 2, 5):
        color = 'yellow'
    else:
        color = 'red'

    return color


def score_cohesion(val: Optional[Union[int, float]]) -> str:
    if val is None:
        color = 'white'
    elif is_between(val, 0, 33):
        color = 'green'
    elif is_between(val, 33, 67):
        color = 'yellow'
    else:
        color = 'red'

    return color


def score_c2c(val: Optional[Union[int, float]]) -> str:
    if val is None:
        color = 'white'
    elif is_between(val, 0, 0.44):
        color = 'red'
    elif is_between(val, 0.44, 0.55):
        color = 'yellow'
    else:
        color = 'green'

    return color


def score_inheritance(val: Optional[Union[int, float]]) -> str:
    if val is None:
        color = 'white'
    elif is_between(val, 0, 3):
        color = 'green'
    elif is_between(val, 3, 6):
        color = 'yellow'
    else:
        color = 'red'

    return color


switcher = {
    'MaxCyclomaticStrict': score_cyclo,
    'MaxEssential': score_essential,
    'MaxInheritanceTree': score_inheritance,
    'MaxNesting': score_nesting,
    'RatioCommentToCode': score_c2c,
    'badFix': score_bad_fix,
    'PercentLackOfCohesion': score_cohesion
}


def fn_lookup(metric_name: str, val: Optional[Union[int, float]]) -> str:
    fn = switcher.get(metric_name, None)
    if fn:
        return fn(val)
    else:
        return 'grey'


def score_metrics(metrics: Dict):
    for k, metric in metrics.items():
        metric['color'] = fn_lookup(k, metric['val'])


def color_div(color: str, range_str: str) -> str:
    return f'<div title="{color.lower()}">  {range_str}  </div>'


def metric_key_range_str(metric: str) -> Tuple[str, str, str]:
    if metric == 'MaxCyclomaticStrict':
        return color_div('Green', '0 - 4'), color_div('Yellow', '4 - 20'), color_div('Red', '> 20')
    elif metric == 'badFix':
        return color_div('Green', '0 - 20'), color_div('Yellow', '20 - 50'), color_div('Red', '> 50')
    elif metric == 'MaxEssential':
        return color_div('Green', '0 - 4'), color_div('Yellow', '4 - 10'), color_div('Red', '> 10')
    elif metric == 'MaxNesting':
        return color_div('Green', '0 - 2'), color_div('Yellow', '2 - 5'), color_div('Red', '> 5')
    elif metric == 'PercentLackOfCohesion':
        return color_div('Green', '0 - 33'), color_div('Yellow', '33 - 67'), color_div('Red', '> 67')
    elif metric == 'RatioCommentToCode':
        return color_div('Green', '> 0.55'), color_div('Yellow', '0.44 - 0.55'), color_div('Red', '0 - 0.44')
    elif metric == 'MaxInheritanceTree':
        return color_div('Green', '0 - 3'), color_div('Yellow', '3 - 6'), color_div('Red', '> 6')
    else:
        return '-', '-', '-'


def metric_key_range_table() -> List[str]:
    metrics = [
        'MaxCyclomaticStrict',
        'badFix',
        'MaxEssential',
        'MaxNesting',
        'PercentLackOfCohesion',
        'RatioCommentToCode',
        'MaxInheritanceTree',
    ]
    h1 = '| Metric | Green Range | Yellow Range| Red Range|\n'
    h2 = '|        |:---:    |:---:    |:---:    |\n'
    rs = ['\n\n###Metric Keys\n\n', h1, h2]
    for metric in metrics:
        grn_str, yel_str, red_str = metric_key_range_str(metric)
        rs.append(f'{metric}|{grn_str}|{yel_str}|{red_str}|\n')
    return rs
