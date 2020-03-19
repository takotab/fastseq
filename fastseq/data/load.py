# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/02_data.load.ipynb (unless otherwise specified).

__all__ = ['TensorCatI', 'CatSeqI', 'CatTfm', 'get_classes', 'make_vocab', 'make_ids', 'split_ts_con', 'json2TSMulti',
           'catagories', 'TSMulti_', 'CatMultiTfm', 'MTSDataLoader']

# Cell
from ..core import *
from .external import *
from fastcore.utils import *
from fastcore.imports import *
from fastai2.basics import *
from fastai2.data.transforms import *
from fastai2.tabular.core import *
import orjson

# Cell
def _get_classes(df, cat_cols, classes=None):
    classes = ifnone(classes, {})
    if classes == {}:
        for col in cat_cols:
            classes[col] = unpack_list(list(df[col]))
    return classes

def _make_vocab_df(df,cat_cols, classes = None):
    vocab,o2i = {},{}
    classes = _get_classes(df, cat_cols, classes)
    for col, vals in classes.items():
        vocab[col], o2i[col] = uniqueify(vals, sort=True, bidir=True)
    return vocab, o2i

# Cell
from IPython.core.debugger import set_trace
class TensorCatI(TensorBase):pass
class CatSeqI(TensorSeq):pass

class CatTfm(Transform):
    def __init__(self, df:pd.DataFrame = None, cat_cols:[] = None,
                 classes = None, vocab=None, o2i=None):
        if vocab is not None and o2i is not None:
            self.vocab,self.o2i = vocab, o2i
        else:
            self.vocab,self.o2i = _make_vocab_df(df,cat_cols)

    def encodes(self, x: TensorCat):
        r = []
        for i, (o, key) in enumerate(zip(x.o, x._meta['label'])):
            r.append(self.o2i[key][o])#TensorCat
        return TensorCatI(r, label = x._meta['label'])

    def decodes(self, x:TensorCatI):
        if len(x.shape) == 1:
            x = TensorCatI(x[None,:],**x._meta)
        return TensorCat(reverse_lst(self._decode(TensorCatI(x.T,**x._meta))),
                         label = x._meta.get('label', None))

    def encodes(self, x:CatSeq):
        r = []
        for i,(o, key) in enumerate(zip(x.o,x._meta['label'])):
            r.append([])
            for a in o:
                r[i].append(self.o2i[key][a]) #CatSeq
        return CatSeqI(r, label = x._meta['label'])

    def decodes(self, x:CatSeqI):
        if len(x.shape) == 2:
            x = CatSeqI(x[None,:],**x._meta)
        r = []
        for o in x:
            r.append(self._decode(CatSeqI(o,**x._meta)))
        return CatSeq(r, label = x._meta.get('label', None))

    def _decode(self, x):
        r = []
        for i, (o, key) in enumerate(zip(x, x._meta['label'])):
            r.append([])
            for a in o:
                r[i].append(self.vocab[key][a])
        return r

# Cell
def get_classes(path:Path):
    return get_meta(path)['classes']

def make_vocab(path, classes = None):
    if classes is None:
        classes = get_classes(path)
    vocab, o2i = {},{}
    for col, vals in classes.items():
        vocab[col], o2i[col] = uniqueify(vals, sort=True, bidir=True)
    return vocab, o2i

# Cell
def make_ids(dl):
    """Make ids if the sequence is shorter than `min_seq_len`, it will drop that sequence."""
    # Slice each time series into examples, assigning IDs to each
    last_id = 0
    n_dropped = 0
    n_needs_padding = 0
    dl._ids = {}
    for f in dl.dataset:
        dp = get_ts_datapoint(f)
        num_examples = (dp['_length'] - dl.lookback - dl.horizon + dl.step) // dl.step
        # Time series shorter than the forecast horizon need to be dropped.
        if dp['_length'] < dl.min_seq_len:
            n_dropped += 1
            continue
        # For short time series zero pad the input
        if dp['_length'] < dl.lookback + dl.horizon:
            n_needs_padding += 1
            num_examples = 1
        for j in range(num_examples):
            dl._ids[last_id + j] = (str(f), j * dl.step)
        last_id += num_examples

    # Inform user about time series that were too short
    if n_dropped > 0:
        print("Dropped {}/{} time series due to length.".format(
                n_dropped, len(dl.dataset)))

    # Inform user about time series that were short
    if n_needs_padding > 0:
        print("Need to pad {}/{} time series due to length.".format(
                n_needs_padding, len(dl.dataset)))
    # Store the number of training examples
    dl.n = int(dl._ids.__len__() )
    return dl, dl.n


# Cell
@typedispatch
def get_part_of_ts(x, lookback_id, length, pad=np.mean, t = tensor, **kwargs):
    if x.shape[-1] < length:
        # If the time series is too short, we pad
        padding = pad(x, -1)
        x = t(np.pad(
            x, # report issue https://github.com/numpy/numpy/issues/15606
            pad_width=((0, 0), (length - x.shape[-1], 0)),
            mode='constant',
            constant_values=padding
        ), **kwargs).float()
        assert x.shape == (x.shape[0],length), f"{x.shape}\t,{lookback_id}, 'tsshape':{x.shape}"
    else:
        x = t(x[:,lookback_id:lookback_id + length], **kwargs).float()
    return x


# Cell
@typedispatch
def get_part_of_ts(x:list, lookback_id, length, t = L, **kwargs):
    if len(x[0]) < length:
        # If the time series is too short, we pad
        padding = [o[-1] for o in x]
        pad_len = length - len(x[0])
        x = [o[lookback_id:lookback_id + length] + [padding[i]]*pad_len for i,o in enumerate(x)]
    else:
        x = [o[lookback_id:lookback_id + length] for o in x]
    return t(x, **kwargs)

@typedispatch
def get_part_of_ts(x:L, *args, **kwargs):
    return get_part_of_ts(list(x),*args, **kwargs)

# Cell
catagories = dict( )
catagories[type('1')] = dict(seq = CatSeq,  cat = TensorCat,  multi = TSMulti)
catagories[type(1)]   = dict(seq = CatSeqI, cat = TensorCatI, multi =  TSMulti_)

def split_ts_con(ts, y_name, meta:Meta):
    ts_con_names = [o for o in meta['col_names']['ts_con_names'] if o != y_name]
    y = ts['ts_con'][y_name]
    tsx = [ts['ts_con'][k] for k in ts_con_names]
    return y, tsx, ts_con_names


def json2TSMulti(ts, lookback_id, y_name, lookback, horizon, meta:Meta):
    y, tsx, ts_con_names = split_ts_con(ts, y_name, meta)

    y = get_part_of_ts([y], lookback_id, lookback + horizon,
                       t = TensorSeq, label=[y_name + '_y'], m=['g'])
    x = TensorSeq(y[:,:lookback], label=[y_name + '_x'], m=['g'])
    tsx_con = get_part_of_ts(tsx, lookback_id, lookback + horizon,
                             t = TensorSeq, label=ts_con_names)
    con = TensorCon(ts.get_ts(meta,'con'), label=meta['col_names']['con_names'])
    tsx_cat = ts.get_ts(meta,'ts_cat')
    types = catagories[type(tsx_cat[0][0])]

    tsx_cat = get_part_of_ts(tsx_cat, lookback_id, lookback + horizon,
                             t = types['seq'], label=meta['col_names']['ts_cat_names'])
    r = [x, tsx_con, tsx_cat]
    r.append(types['cat'](ts.get_ts(meta,'cat'), label=meta['col_names']['cat_names']))
    r.append(con)
    r.append(y)
    return types['multi'](r)

# Cell
class TSMulti_(Tuple):
    def _dict(self):
        return {str(str(i)+'_'+str(type(a))):a.shape for i,a in enumerate(self)}

class CatMultiTfm(ItemTransform):
    @delegates(CatTfm.__init__)
    def __init__(self, **kwargs): # maybe change to proccs
        self.f = CatTfm(**kwargs)

    def encodes(self, o):
        if type(o[2]) == CatSeq:
            return TSMulti_(self.f(a) for a in o)
        return o

    def decodes(self, o):
        return TSMulti(self.f.decode(a) for a in o)


# Cell
class MTSDataLoader(TfmdDL):
    @delegates(TfmdDL.__init__)
    def __init__(self, dataset, meta:Meta, y_name = 'x', lookback=14, horizon=7, step=1, min_seq_len=None,
                train = True, procs = None, vocab=None, o2i=None, **kwargs):
        assert type(meta) == Meta or type(meta) == dict
        store_attr(self,'dataset,y_name,lookback,horizon,step,meta')
        self.min_seq_len = ifnone(min_seq_len, lookback)
        self, n = make_ids(self)
        if vocab is None: # from MTSDataLoaders
            vocab, o2i = make_vocab(dataset, classes = self.meta['classes'])
        kwargs['after_item'] = kwargs.get('after_item', CatMultiTfm(vocab = vocab, o2i=o2i))
        super().__init__(dataset=self.dataset, **kwargs)
        self.n = n
        self.procs = Pipeline(L(procs))
        self.procs.setup(self, train)

    @delegates(__init__)
    @classmethod
    def from_path(cls, path, **kwargs):
        return cls(get_files(path, extensions='.json'), get_meta(path),**kwargs)

    @delegates(TfmdDL.new)
    def new(self, dataset=None, cls=None, **kwargs):
        for k,v in {k:getattr(self,k) for k in ['meta','horizon', 'lookback', 'step']}.items():
            if k not in kwargs:
                kwargs[k] = v
        res = super().new(dataset = dataset,cls= cls, y_name= self.y_name, **kwargs)
        res, n = make_ids(res)
        res.n = n
        return res

    def create_item(self, idx):
        if idx>=self.n:
            raise IndexError
        fpath, lookback_id = self._ids[idx]
        ts = get_ts_datapoint(fpath)
        return json2TSMulti(ts, lookback_id, self.y_name, self.lookback, self.horizon, self.meta)


# Cell

def _show_batch_class(self, b=None, max_n=9, ctxs=None, show=True, **kwargs):
    if b is None: b = self.one_batch()
    x, y, its = self._pre_show_batch(b, max_n=max_n)
    x = self.after_item.decode(TSMulti_(x))
    if not show: return x, y, its
    show_batch(x,y,its, ctxs=ctxs, max_n=max_n, **kwargs)

MTSDataLoader.show_batch = _show_batch_class

# Cell
from fastai2.vision.data import get_grid
@typedispatch
def show_batch(x:TSMulti, y:TensorSeq, its, *args, ctxs=None, max_n=10, rows=None, cols=None, figsize=None, **kwargs):
    if ctxs is None: ctxs = get_grid(min(x[0].shape[0], max_n), add_vert=1, figsize=figsize, **kwargs)
    for i, ctx in enumerate(ctxs):
        o = TSMulti([type(o)(o,**o._meta) for o in its[i] if o.shape[-1] > 0])
        ctx = o.show(ctx=ctx)
    return ctxs

@typedispatch
def show_batch(x:TSMulti, y:None, its, *args, ctxs=None, max_n=10, rows=None, cols=None, figsize=None, **kwargs):
    if ctxs is None: ctxs = get_grid(min(x[0].shape[0], max_n), add_vert=1, figsize=figsize, **kwargs)
    for i, ctx in enumerate(ctxs):
        o = TSMulti([type(o)(o[i],**o[i]._meta) for o in x if o.shape[-1] > 0])
        ctx = o.show(ctx=ctx)
    return ctxs

# Cell
# from fastseq.data.load_pd import *

@typedispatch
def show_results(x:TSMulti, y, its, outs, ctxs=None, max_n=9,rows=None, cols=None, figsize=None, **kwargs):
    if ctxs is None: ctxs = get_grid(min(x[0].shape[0], max_n), add_vert=1, figsize=figsize, **kwargs)
    for i, ctx in enumerate(ctxs):
        r = [type(o)(o,**o._meta) for o in its[i] if o.shape[-1] > 0]
        r.append(type(its[i][-1])(outs[i][0], label=['pred_y'], m=['r']))
        o = TSMulti(r)
        ctx = o.show(ctx=ctx)
