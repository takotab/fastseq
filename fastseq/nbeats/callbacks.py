# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/06_nbeats.callbacks.ipynb (unless otherwise specified).

__all__ = ['NBeatsTheta', 'NBeatsBackwards', 'NBeatsForward', 'NBeatsAttention']

# Cell
from fastcore.utils import *
from fastcore.imports import *
from fastai2.basics import *
from fastai2.callback.hook import num_features_model
from fastai2.callback.all import *
from fastai2.torch_core import *
from torch.autograd import Variable
from ..all import *

from .model import *

# Cell
def _get_key_from_nested_dct(dct, s_key, exclude = [], namespace=''):
    r = {}
    for key in dct.keys():
        if sum([exc in key for exc in exclude])== 0 :
            if type(dct[key]) == dict:
                r.update(_get_key_from_nested_dct(dct[key], s_key, exclude, namespace=namespace+key))
            if s_key in key:
                r[namespace+key] = dct[key]
    return r

# Cell
class NBeatsTheta(Metric):
    "The sqaure of the `theta` for every block. "
    def reset(self):           self.total,self.count = 0.,0
    def accumulate(self, learn):
        bs = find_bs(learn.yb)
        theta_dct = _get_key_from_nested_dct(learn.model.dct,'theta',['bias','total','att'])
        t = torch.sum(tensor([v.float().abs().mean() for k,v in theta_dct.items()]))
        self.total += to_detach(t.abs().mean())*bs
        self.count += bs
    @property
    def value(self): return self.total/self.count if self.count != 0 else None
    @property
    def name(self):  return "theta"

# Cell
class NBeatsBackwards(Metric):
    "The loss according to the `loss_func` on the backwards part of the time-serie."
    def reset(self):           self.total,self.count = 0.,0
    def accumulate(self, learn):
        bs = find_bs(learn.yb)
        loss = to_detach(learn.loss_func(learn.pred[:,0,:learn.model.lookback], learn.yb[0][:,0,:learn.model.lookback]))
#         print('NBeatsBackwards',loss)
        self.total += loss.mean()*bs
        self.count += bs
    @property
    def value(self): return self.total/self.count if self.count != 0 else None
    @property
    def name(self):  return "b_loss"

# Cell
class NBeatsForward(Metric):
    "The loss according to the `loss_func` on the backwards part of the time-serie."
    def reset(self):           self.total,self.count = 0.,0
    def accumulate(self, learn):
        bs = find_bs(learn.yb)
        loss = learn.loss_func(learn.pred[:,0,-learn.model.horizon:], learn.yb[0][:,0,-learn.model.horizon:])
        self.total += loss*bs
        self.count += bs
    @property
    def value(self): return self.total/self.count if self.count != 0 else None
    @property
    def name(self):  return "f_loss"

# Cell
class NBeatsAttention(Callback):
    def means(self, df=True):
        theta_means = {k.replace('theta',''):v.float().cpu().data for k,v in _get_key_from_nested_dct(self.learn.model.dct,'theta',['total']).items()}
        ret = {}
        for k,v in theta_means.items():
            ret[k] = {}
            for i in range(v.shape[-1]):
                ret[k].update({'theta_'+str(i)+'_mean': v[:,i].mean().numpy(),
                               'theta_'+str(i)+'_std': v[:,i].std().numpy(),
                              })

        att = {k.replace('attention','att_mean'):v.float().cpu().numpy() for k,v in _get_key_from_nested_dct(self.learn.model.dct,'att',['total']).items()}
        for k in ret.keys():
            for att_key in att.keys():
                if k in att_key:
                    ret[k].update({'att_mean':att[att_key].mean(),
                                   'att_std':att[att_key].std(),
                                  })

        if df:
            return pd.DataFrame(ret)
        return ret