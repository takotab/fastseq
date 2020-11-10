#!/usr/bin/env python
# coding: utf-8

# In[1]:
# default_exp data.procs

# In[1]:
# hide
import sys

sys.path.append("..")
import pandas as pd

# In[2]:


# hide
from nbdev.showdoc import *


# # Data.Procs

# ### CatProc

# In[3]:


# export
from fastseq.data.external import *
from fastseq.data.load import *
from fastseq.data.core import *
from fastseq.core import *
from fastcore.all import *
from fastcore.imports import *
from fastai2.basics import *
from fastai2.data.transforms import *
from fastai2.tabular.core import *
from typing import List
import orjson


# In[4]:


# export
class CatProc:
    def __init__(self, path, num_of_workers=None, vocab=None, o2i=None):
        if vocab is None and o2i is None:
            vocab, o2i = make_vocab(path)
        self.meta = get_meta(path)
        self.f = CatMultiTfm(vocab=vocab, o2i=o2i)
        self.num_of_workers = num_of_workers

    def __call__(self, files: List[Path]):
        return multithread_f(self._setup, files, self.num_of_workers)

    #         r = []
    #         for f in files:
    #             r.append(self._setup(f))
    #         return r

    def _setup(self, f: Path):
        ts = get_ts_datapoint(f)
        tsm = json2TSMulti(
            ts,
            0,
            self.meta["col_names"]["ts_con_names"][0],
            ts["_length"] - 1,
            1,
            self.meta,
        )
        tsm = self.f(tsm)
        for i, cat in enumerate(ts["ts_cat"]):
            test_eq(len(tsm[2][i]), len(ts["ts_cat"][cat]))
            ts["ts_cat"][cat] = [o.item() for o in tsm[2][i]]
        for i, cat in enumerate(ts["cat"]):
            ts["cat"][cat] = tsm[3][i].item()
        open(f, "wb").write(orjson.dumps(dict(ts)))
        return f


# In[6]:


get_ipython().run_cell_magic(
    "time",
    "",
    "path = Path('../data/test_data')\nhorizon,lookback = 7, 14\ndel_create([2000]*10, path = path)\n\nfs = get_files(path, extensions='.json', folders = False)\n\nproc = CatProc(path, num_of_workers = 1)\nr = proc(fs)",
)


# In[7]:


for f in fs:
    ts = get_ts_datapoint(f)
    for cat in set(unpack_list([v for k, v in ts["ts_cat"].items()])):
        test_eq(type(cat), int)

    for cat in set(unpack_list([v for k, v in ts["cat"].items()])):
        test_eq(type(cat), int)


# In[8]:


get_ipython().run_cell_magic(
    "time",
    "",
    "# hide\npath = Path('../data/test_data')\nhorizon,lookback = 7, 14\ndel_create([2000]*10, path = path)\n\nfs = get_files(path, extensions='.json', folders = False)\n\nproc = CatProc(path, num_of_workers = 8)\nr = proc(fs)",
)


# ### DateFeatures

# In[5]:


# export
from fastai2.tabular import *
# In[]:
import seaborn as sns

# In[4]:

# export
class DateProc:
    def __init__(
        self,
        path: Path,
        field_name: str,
        num_of_workers=None,
        con_cols=["Year", "Day", "Dayofweek", "Dayofyear", "Elapsed"],
    ):
        self.meta = get_meta(path)
        self.num_of_workers = num_of_workers
        self.field_name = field_name
        self.con_cols = con_cols

    def __call__(self, files: List[Path]):
        # return multithread_f(self._setup, files, self.num_of_workers)

        r = []
        for i,f in enumerate(files):
            r.append(self._setup(f))
            if i % 100 == 0:
                print(i)
        return r

    def _setup(self, f: Path):
        ts = get_ts_datapoint(f)
        df = pd.DataFrame(ts["ts_cat"])
        df = add_datepart(df, self.field_name)

        ts["ts_cat"] = {k: list(v) for k, v in dict(df).items()}
        df[self.con_cols] = (df[self.con_cols] - df[self.con_cols].mean()) / df[
            self.con_cols
        ].std()
        ts["ts_con"] = {
            k: list(v) for k, v in dict(df).items() if k in self.con_cols
        }
        open(f, "wb").write(orjson.dumps(dict(ts)))
        return f


# In[ ]:
path = Path("../data/m5_tiny/rows")
new_path = Path('../data/m5_tiny/rows_date')
if not new_path.exists():new_path.mkdir()
for f in path.glob('*.json'):
    f.copy(new_path / f.name)
(path / '.ts_meta').copy(new_path / '.ts_meta')
# In[]:
# horizon,lookback = 7, 14
# del_create([20]*10, path = path)
fs = get_files(new_path, extensions=".json", folders=False)

proc = DateProc(new_path, "date", num_of_workers=1)
r = proc(fs)

# In[ ]:
print(get_ts_datapoint(r[0]))
# In[ ]:


# In[ ]:


# ## M5 example

# In[9]:


path = Path("../data/m5_tiny/rows")
path.ls()


# In[10]:


tmf = CatProc(path)
tmf.f.f.vocab


# In[11]:


horizon, lookback = 28, 28 * 3
dls = MTSDataLoaders.from_m5_path(path, "sales", horizon=horizon, lookback=lookback,)
dls.show_batch()


# In[30]:


get_ipython().run_cell_magic("time", "", "for o in dls.train:\n    pass")


# In[ ]:


# In[12]:


# hide
from nbdev.export import *

notebook2script()


# In[118]:


git_add("04_data.procs.ipynb", commit_msg="CatProc")


# In[ ]:
