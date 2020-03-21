# default_exp model.test

# %%
# hide
import pandas as pd


# %%
# hide
from nbdev.showdoc import *

# %%
# export
from fastseq.core import *
from fastseq.data.external import *
from fastseq.data.load import *
from fastseq.data.core import *
from fastseq.data.procs import *
from fastcore.all import *
from fastcore.imports import *
from fastai2.basics import *
from fastai2.data.transforms import *
from fastai2.tabular.core import *
from fastai2.tabular.model import *
from fastai2.torch_basics import *
from fastai2.callback.all import *
from fastseq.metrics import *


# %%
# export 
def hello(a='world'):
    print('hello',a)


# %%
hello()


# %%
