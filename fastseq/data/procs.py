# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_data.procs.ipynb (unless otherwise specified).

__all__ = ['CatProc', 'DateProc']

# Cell
from .external import *
from .load import *
from .core import *
from ..core import *
from fastcore.all import *
from fastcore.imports import *
from fastai2.basics import *
from fastai2.data.transforms import *
from fastai2.tabular.core import *
from typing import List
import orjson

# Cell
class CatProc():
    def __init__(self, path, num_of_workers = None, vocab = None, o2i = None):
        store_attr(self, 'path,num_of_workers,vocab,o2i')
        self.init()

    def init(self, hard = False):
        if (self.vocab is None and self.o2i is None) or hard:
            self.vocab, self.o2i = make_vocab(self.path)
        self.meta = get_meta(self.path)
        self.f = CatMultiTfm(vocab = self.vocab, o2i = self.o2i)
        print(self.vocab)

    def __call__(self, files:List[Path]):
        self.init(True)
        if self.num_of_workers >1:
            return multithread_f(self._setup, files, self.num_of_workers)
        else:
            r = []
            for f in files:
                r.append(self._setup(f))
            return r

    def _setup(self, f:Path):
        ts = get_ts_datapoint(f)
        tsm = json2TSMulti(ts, 0, self.meta['col_names']['ts_con_names'][0], ts['_length']-1, 1, self.meta)
        tsm = self.f(tsm)

#         assert len(tsm[2]) == len(ts['ts_cat']), f"{ts['ts_cat'].keys()} == {tsm[2].shape}"

        for i, cat in enumerate(ts['ts_cat']):
            test_eq(len(tsm[2][i]), len(ts['ts_cat'][cat]))
            ts['ts_cat'][cat] = [o.item() for o in tsm[2][i]]
        for i, cat in enumerate(ts['cat']):
            ts['cat'][cat] = tsm[3][i].item()
        open(f,'wb').write(orjson.dumps(dict(ts)))
        return f


# Cell
from fastai2.tabular import *

# Cell
def _fix_meta(ts:dict, path:Path):
    o = {}
    for k,v in ts.items():
        if k[0] is not '_':
            try:
                o.update({col:python_type(o) for col, o in v.items()})
            except:
                print(k,v)
                assert False
    length, classes, col_names, names = reconize_cols(o)
    make_meta_file(path, classes = classes, col_names = col_names)

class DateProc:
    def __init__(
        self,
        path: Path,
        field_name: str,
        num_of_workers=None,
        con_cols=["Year", "Day", "Dayofweek", "Dayofyear", "Elapsed"],
        cat_cols=["Year", "Day", "Dayofweek",'Is_month_end',
                  'Is_month_start', 'Is_quarter_end', 'Is_quarter_start', 'Is_year_end', 'Is_year_start',],
    ):
        self.path = path
        self.meta = get_meta(path)
        self.num_of_workers = num_of_workers
        self.field_name = field_name
        self.con_cols = con_cols
        self.cat_cols = cat_cols

    def __call__(self, files: List[Path]):
        print(files)
        _, ts = self._setup(files[0],with_ts=True)
        _fix_meta(ts, self.path)
        self.meta = get_meta(self.path)

        if self.num_of_workers > 1:
            return multithread_f(self._setup, files, self.num_of_workers)

        r = []
        for i,f in enumerate(files):
            r.append(self._setup(f))
        return r

    def _setup(self, f: Path, with_ts=False):
        ts = get_ts_datapoint(f)
        df = pd.DataFrame(ts["ts_cat"])
        if self.cat_cols[-1] in df.columns:
            return f
        df = add_datepart(df, self.field_name)

        ts["ts_cat"].update({k: list(v.astype(str)) for k, v in dict(df).items() if k in self.cat_cols})
        df[self.con_cols] = (df[self.con_cols] - df[self.con_cols].mean()) / (df[
            self.con_cols
        ].std() + 1e-7)
        ts["ts_con"].update( {
            k: list(v) for k, v in dict(df).items() if k in self.con_cols
        })
        open(f, "wb").write(orjson.dumps(dict(ts)))
        if with_ts:
            return f, ts
        return f
