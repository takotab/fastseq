# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/08_nbeats.interpret.ipynb (unless otherwise specified).

__all__ = ['NBeatsInterpretation', 'add_stack', 'add_stack_full', 'plot_top_losses', 'ts_plot_top_losses']

# Cell
from ..all import *
from ..data.external import *
from fastai2.basics import *
from .learner import *
from .callbacks import *


# Cell
from .callbacks import _get_key_from_nested_dct

# Cell
class NBeatsInterpretation():
    "Interpretation base class, can be inherited for task specific Interpretation classes"
    def __init__(self, dl, inputs, preds, targs, decoded, losses, full_every_block = None):
        store_attr(self, "dl,inputs,preds,targs,decoded,losses,full_every_block")

    @classmethod
    def from_learner(cls, learn, ds_idx=1, dl=None, act=None):
        "Construct interpretatio object from a learner"
        if dl is None: dl = learn.dls[ds_idx]
        cb = Components()
        learn.add_cb(cb)
        res = learn.get_preds(dl=dl, with_input=True, with_loss=True, with_decoded=True, act=None, reorder=False)
        learn.remove_cb(cb)
        return cls(dl, *res, full_every_block=cb.stored)

    def top_losses(self, k=None, largest=True):
        "`k` largest(/smallest) losses and indexes, defaulting to all losses (sorted by `largest`)."
        return self.losses.topk(ifnone(k, len(self.losses)), largest=largest)


# Cell
def add_stack(b):
    res = {}
    print('add stack before',b.keys())
    for stack in set([o[:-4] for o in b.keys()]):
        for direction in ['f','b']:
            for key in b.keys():
                if stack in key and direction == key[-1] :
                    if stack+'_'+direction in res:
                        res[stack+'_'+direction] += b[key]
                    else:
                        res[stack+'_'+direction] = b[key]
    print('add stack after',res.keys())
    return res

def add_stack_full(b):
    res = {}
    for stack in set([o[:-7] for o in b.keys()]):
        for key in b.keys():
            direction = 'full'
            if stack in key and direction in key:
                if stack+'_'+direction in res:
                    res[stack+'_'+direction] += b[key]
                else:
                    res[stack+'_'+direction] = b[key]
    return res


# Cell
def plot_top_losses(self, k, largest=True, **kwargs):
        losses,idx = self.top_losses(k, largest)
#         total_b = self.dct['b'][idx.long(), :]
#         keys_wo_total_b = [o for o in list(self.dct.keys()) if 'total_b' not in o]
        if not isinstance(self.inputs, tuple):
            self.inputs = (self.inputs,)

        if isinstance(self.inputs[0], Tensor):
            inps = tuple(o[idx] for o in self.inputs)
            self.dl.after_batch(inps)
        else:
            xb = [tuple(o[i] for o in self.inputs) for i in idx]
            inps = self.dl.create_batch(self.dl.before_batch(xb))
        assert self.dl.after_batch[0].m.shape[0] == k

        b = inps + tuple(o[idx] for o in (self.targs if is_listy(self.targs) else (self.targs,)))
        x,y,its = self.dl._pre_show_batch(b, max_n=k)
        full_every_block = [{k:self.dl.after_batch.decode((o[i,None,:]))[0][0][0] for k,o in full_every_block = self.full_every_block .items()} for i in idx]
        b_out = inps + tuple(o[idx] for o in (self.decoded if is_listy(self.decoded) else (self.decoded,)))
        x1,y1,outs = self.dl._pre_show_batch(b_out, max_n=k)
#         return self.preds[idx], full_every_block
        if its is not None:
            ts_plot_top_losses(x, y, its, outs.itemgot(slice(len(inps), None)), self.preds[idx], losses,blocks= full_every_block, **kwargs)
#         #TODO: figure out if this is needed
#         #its None means that a batch knos how to show itself as a whole, so we pass x, x1
#         else:
#         show_results(x, x1, its, ctxs=ctxs, max_n=max_n, **kwargs)
NBeatsInterpretation.plot_top_losses = plot_top_losses

# Cell
def ts_plot_top_losses(x:TSTensorSeq, y:TSTensorSeqy, *args, blocks=[], total_b=None, combine_stack=False,
                    rows=None, cols=None, figsize=None, **kwargs):

    figsize = (2*3, x.shape[0]*3+0) if figsize is None else figsize
    _, axs = plt.subplots(x.shape[0], 2, figsize=figsize, sharey='row')
    axs = axs.flatten()
    normal = np.arange(0,x.shape[0]*2,2)

    for i, (_x, _y, block, pred, t) in enumerate(zip(x, y, blocks, args[2], args[3])):
        if combine_stack:
            block = add_stack_full(block)
        ax = axs[i*2]
        ctx = show_graph(_x, ax=ax, title=str(f"loss:{np.round(t.data.item(),2)}"), label='x')
        TSTensorSeqy(_y, m = '*g', label = 'y').show(ctx=ctx)
        TSTensorSeqy(pred, m = '-*r', label = 'pred').show(ctx=ctx)
        ax = axs[i*2 + 1]
        total = torch.zeros_like(block[list(block.keys())[0]])
        for k, c in zip(block.keys(), ['y','k','g','r','b','k','b','b']):
#             if 'season' in k:
            ax = TSTensorSeqy(block[k], m = '-*'+c, label = k.replace('_full','')).show(ctx=ax)
            total += block[k]
            ax.legend(bbox_to_anchor=(1.2, 1.05), ncol=3, fancybox=True)


#         ax = TSTensorSeqy(-total, m = '-*y', label= 'tot').show(ctx=axs[i*2])
        ax.legend()
