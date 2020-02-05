# Fastseq
> A way to use fastai with sequence data


## Installing

Please install [fastai2](https://dev.fast.ai/#Installing) according to the instructions.

Then install Fastseq by:
```
pip install -e .
```

## How to use

```python
from fastai2.basics import *
from fastseq.all import *
from fastseq.nbeats.model import *
```

Getting the data fastai style:

```python
horizon, lookback = 7, 25    
path = untar_data(URLs.m4_daily)
data = TSDataLoaders.from_folder(path, horizon = horizon, lookback = lookback, nrows = 300,step=3)
```

    Train:71691; Valid: 1200; Test 300


```python
data.show_batch()
```


![png](docs/images/output_5_0.png)


```python
mdl = NBeatsNet(device = data.train.device, stack_types=('trend','seasonality'), horizon=horizon, lookback=lookback)
learn = Learner(data, mdl, loss_func=F.mse_loss, opt_func= Adam, )       
```

```python
from fastai2.callback.all import *
learn.lr_find()       
```






![png](docs/images/output_7_1.png)


```python
learn.fit_flat_cos(1, 2e-2)
learn.recorder.plot_loss()
learn.recorder.plot_sched()
```


<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: left;">
      <th>epoch</th>
      <th>train_loss</th>
      <th>valid_loss</th>
      <th>time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>106363518976.000000</td>
      <td>52734368669499392.000000</td>
      <td>00:58</td>
    </tr>
  </tbody>
</table>



![png](docs/images/output_8_1.png)



![png](docs/images/output_8_2.png)


```python
learn.show_results(0)
```






![png](docs/images/output_9_1.png)


```python
learn.show_results(1)
```






![png](docs/images/output_10_1.png)


## Interperation

so the spikes are the origin of the high loss. need to clean the data I guess.
