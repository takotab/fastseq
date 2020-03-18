# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_data.external.ipynb (unless otherwise specified).

__all__ = ['m4_base', 'dummy_data_generator', 'dummy_generator_multi_easy', 'dummy_data_generator_multi', 'TSMulti',
           'get_df', 'Meta', 'TS', 'get_ts_datapoint', 'get_meta', 'python_type', 'add_dct', 'reconize_cols',
           'make_compact', 'meta_file', 'save_row', 'save_df', 'del_create']

# Cell
from ..core import *
from fastcore.utils import *
from fastcore.imports import *
from fastai2.basics import *
import pandas as pd

# Cell
m4_base = "https://motionnet-m4-dataset.s3.eu-central-1.amazonaws.com/"
URLs.m4_daily = f'{m4_base}m4_daily.tgz'

# Cell
def dummy_data_generator(lookback:int, horizon:int, signal_type='seasonality', nrows:int=5, random = True, batch_size=32, norm=False, noise = .2):
    def get_datapoint():
        lin_space = np.linspace(-lookback, horizon, lookback + horizon)
        if random:
            offset = np.random.standard_normal() * .10
        else:
            offset = 1
        if signal_type == 'lin':
            a =  np.random.standard_normal() * lin_space + offset * 100

        a = np.zeros_like(lin_space)
        if signal_type is not 'seasonality':
            p = 4
            a = [(lin_space**(i))[None,:] for i in range(p)]
            T = np.concatenate(a)
            thetas = np.random.randn(4)*1*9**-p
            a= np.matmul(thetas,T)

        if signal_type is not 'trend':
            a += np.cos(2 * np.random.randint(low=1, high=3) * np.pi * lin_space)* np.random.standard_normal() * .5
            a += np.cos(2 * np.random.randint(low=2, high=4) * np.pi * lin_space)* np.random.standard_normal() * .5
            a += np.sin(2 * np.random.randint(low=1, high=3) * np.pi * lin_space)
            a -= np.sin(2 * np.random.randint(low=2, high=4) * np.pi * lin_space)
            a += lin_space * offset + np.random.rand() * 10

        a += np.random.randn(a.shape[0])*noise
        if norm:
            return (a[None,:]-a.mean())/a.std()
        else:
            return a[None,:]

    data = L()
    for i in range(nrows):
        data.append(get_datapoint())

    return data


# Cell
def dummy_generator_multi_easy(length, signal_type='none',nrows:int=5, random = True, noise = .3,
                               norm = True, norm_t = True, increase_noise = False, rang = [5,5]):

    data = L()
    for i in range(nrows):
        weather = dummy_data_generator(length-10, 10, signal_type = 'seasonality', nrows=1, random=random, noise = 0 )[0]
        n = (1+np.random.randn(length) * np.arange(0,10*length, 10) * .001 * noise)[None,:]
        final = (rang[0] + np.random.sample()*(rang[1]-rang[0])) * weather * n
        if norm:
            final = (final-final.mean())/final.std()
        if norm_t:
            weather = (weather-weather.mean())/weather.std()
        tot = {'x':final,'weather': weather}
        data.append(tot)

    return pd.DataFrame(data)

# Cell

def dummy_data_generator_multi(length, citys=2, cont = False, signal_type='none',nrows:int=5, random = True, noise = .2, incl_city_trend = False, norm= True, increase_noise = False):
    city_names=['adam','rdam','zdam','istanbul','berlin','barcalona','NYC','LA']
    data = L()
    for city_i in range(citys):
        city_trend = dummy_data_generator(length//2, length//2, signal_type = 'trend', nrows=1, random=random, noise = 0 )[0]
        for i in range(nrows):
            if noise > .15:
                weather = dummy_data_generator(length//2, 0, signal_type = 'seasonality', nrows=1, random=random, noise = 0 )[0]
                weather = np.concatenate([weather,weather],-1)
            else:
                weather = dummy_data_generator(length-10, 10, signal_type = 'seasonality', nrows=1, random=random, noise = 0 )[0]

            cont = np.random.randn()
            if cont:
                city_weather = cont * city_trend + weather
            else:
                city_weather = city_trend + weather
            normal_signal = 3 * dummy_data_generator(length//2, length//2, signal_type = signal_type, nrows=1, random=random, noise = noise )[0]
            if increase_noise:
                city_weather += dummy_data_generator(2, length-2, signal_type = 'seasonality', nrows=1, random=random, noise = noise,norm=True )[0] * (np.random.randn(length) *(np.arange(length) * (1/length) ) * noise)
            final = normal_signal + city_weather * (1+np.random.randn(length) * .1 * noise)
            if norm:
                final = (final-final.mean())/final.std()
            tot = {'x': final,'weather': weather,'city': city_names[city_i]}
            if incl_city_trend:
                tot['city_trend']=city_trend
            if cont:
                tot['cont'] = cont
            data.append(tot)

    return pd.DataFrame(data)

# Cell
import numpy as np
import pandas as pd
import orjson

# Cell
class TSMulti(MultiTuple):pass

# Cell
def get_df(length = [100,120], use_str = True):
    dct = {'x':[],'con_ts_1':[],'con_ts_0':[],'cat_ts_1':[],'cat_ts_0':[],'con_0':[],'con_1':[], 'cat_0':[],'cat_1':[]}
    for i, l in enumerate(length):
        assert int(l/2) == l/2
        dct['x'].append(np.arange(l))
        dct['con_ts_0'].append(np.arange(l)[None,:])
        dct['con_ts_1'].append(pd.Series(np.arange(l)+np.random.randn(l)))
        dct['con_0'].append(np.random.rand()*2-1)
        dct['con_1'].append(10+np.random.rand()*2)
        lst = ['a','b'] if use_str else [0,1]
        dct['cat_ts_0'].append(L(lst*int(l/2)))
        lst = ['david','john'] if use_str else [0,1]
        dct['cat_ts_1'].append(L(lst*int(l/2)))
        lst = ['a','b'] if use_str else [0,1]
        dct['cat_0'].append(lst[i%2])
        lst = ['adam','rdam'] if use_str else [0,1]
        dct['cat_1'].append(lst[i%2])
    return pd.DataFrame(data=dct)

# Cell
class Meta(dict):pass
class TS(dict):
    @classmethod
    def load(cls, f):
        return cls(orjson.loads(open(f,'rb').read()))

    def get_ts(self, meta:Meta, key):
        """Ensures it is always same order"""
        try:
            return [self[key][o] for o in meta['col_names'][key+'_names']]
        except KeyError:
            assert key in ['cat','con','ts_cat','ts_con']

    def get_np(self,meta:Meta, key):return np.array(self.get_ts(meta,key))
    def __len__(self):return self['_length']

def get_ts_datapoint(f):
    return TS(orjson.loads(open(f,'rb').read()))

def get_meta(path:Path):
    classes = defaultdict(set)
    f = path / '.ts_meta'
    return Meta(json.load(open(f,'r')))

# Cell
def python_type(o):
    if isinstance(o,int) or type(o) == np.int64:
        return int(o)
    elif isinstance(o,float) or type(o) == np.float64:
        if int(o) == o:
            return int(o)
        return float(o)
    elif type(o) == str:
        return o
    elif type(o) == pd.Series:
        return [python_type(v) for k,v in dict(o).items()]
    elif isinstance(o,list) or isinstance(o,L):
        return [python_type(v) for v in o]
    elif isinstance(o,np.ndarray):
        return [python_type(v) for v in list(o.flatten())]
    raise Exception(f"{type(o)}, {o}")


# Cell
def add_dct(dct, k, o):
    if type(o) == set:
        o = list(o)

    if type(o) == list or type(o) == L:
        if k in dct:
            dct[k] = list(set(dct[k] +o))
        else:
            dct[k] = o
    elif type(o) == dict or type(o) == collections.defaultdict:
        if k not in dct:
            dct[k] = {}
        for _k,v in o.items():
            dct[k] = add_dct(dct[k], _k, v)
    elif type(o) == int or type(o) == float:
        dct[k] = o
    else:
        raise Exception(type(o))
    return dct

# Cell
import json
def _check_length(lst, length):
    if length is None:
        length = len(lst)
    else:
        assert len(lst) == length
    return length

def reconize_cols(datapoint:dict, con_names= [], cat_names=[], ts_con_names=[], ts_cat_names=[]):
    """Gets the con_names, cat_names, ts_con_names, ts_cat_names for the `datapoint`"""
    length = None
    classes = defaultdict(set)
    for k,v in datapoint.items():
        if k in con_names+cat_names+ ts_con_names+ts_cat_names:
            if k in [cat_names+ts_cat_names]:
                for _v in set(v):
                    classes[k].add(_v)
            if k in ts_cat_names:
                length = _check_length(v, length)
        elif type(v) == int or isinstance(v,float):
            con_names.append(k)
        elif type(v) == str:
            cat_names.append(k)
            classes[k] = [v]
        elif isinstance(v,list) and (type(v[0]) == int or type(v[0]) == float):
            ts_con_names.append(k)
            length = _check_length(v, length)
        elif isinstance(v, list) and (type(v[0]) == str):
            ts_cat_names.append(k)
            length = _check_length(v, length)
            for _v in set(v):
                classes[k].add(_v)
        else:
            raise TypeError(type(v), type(v[0]))
    col_names = {k:list(set(v)) for k,v in zip('con_names, cat_names, ts_con_names, ts_cat_names'.split(', '),
                                         [con_names, cat_names, ts_con_names, ts_cat_names],)}
    return length, classes, col_names, [list(set(o)) for o in [con_names, cat_names, ts_con_names, ts_cat_names]]

def make_compact(dp, con_names, cat_names, ts_con_names, ts_cat_names, **kwargs):
    r = {'_'+k:v for k,v in kwargs.items()}
    r['con'] = {k:dp[k] for k in con_names}
    r['cat'] = {k:dp[k] for k in cat_names}
    r['ts_con'] = {k:[float(i) for i in dp[k]] for k in ts_con_names}
    r['ts_cat'] = {k:dp[k] for k in ts_cat_names}
    return r

def meta_file(path, **kwargs):
    dct = {}
    f = path / '.ts_meta'
    if (path / '.ts_meta').exists():
        dct = json.load(open(f))
    for k,v in kwargs.items():
        dct = add_dct(dct,k,v)
    json.dump(dct, open(f,'w'), indent = 2, sort_keys = True)

@delegates(reconize_cols)
def save_row(row, path:Path, fname='1', **kwargs):
    if not path.exists(): path.mkdir()
    if fname[-5:] is not '.json': fname += '.json'
    o = {k:python_type(v) for k,v in dict(row).items()}
    length, classes, col_names, names = reconize_cols(o, **kwargs)
    o = make_compact(o, *names, length = length)
    meta_file(path, classes=classes, col_names = col_names)
    open(path / fname,'wb').write(orjson.dumps(o, ))
    return path / fname

# Cell
@delegates(save_row)
def save_df(df:pd.DataFrame, path:Path, **kwargs):
    for i, row in df.iterrows():
        save_row(row, path, fname=str(i), **kwargs)

# Cell
def del_create(length = [80, 80, 80], path = Path('../data/test_data'), use_str = True):
    df = get_df(length, use_str)
    if path.exists(): path.delete()
    path.mkdir()
    save_df(df, path, ts_cat_names = [o for o in list(df.columns) if o in ['cat_ts_0', 'cat_ts_1'] ],
           cat_names = ['cat_0','cat_1'])
    return [path / (str(i) + '.json') for i in range(0,3)]