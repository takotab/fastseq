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
from fastseq.all import *
from fastai2.basics import *
from fastseq.models.nbeats import *
from fastseq.data.external import *
```

Getting the data fastai style:

```python
path = untar_data(URLs.m4_daily)
data = TSDataBunch.from_folder(path, horizon = 14,nrows = 300,step=3)
```

    Train:68161; Valid: 900; Test 300


```python
# items = dummy_data_generator(50, 10, nrows=1000)
# data = TSDataBunch.from_items(items, horizon = 7)
data.show_batch()
```


![png](docs/images/output_5_0.png)


```python
# TODO make custom learner with custom model
learn = nbeats_learner(data,layers=[512, 512], stack_types=("trend","seasonality"), b_loss=.4,
                       loss_func= CombinedLoss(F.mse_loss, smape, ratio = {'smape':.05})
                      )
```

```python
from fastai2.callback.all import *
learn.lr_find()
```






![png](docs/images/output_7_1.png)


```python
learn.fit_one_cycle(3, 1e-3)
learn.recorder.plot_loss()
```


<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: left;">
      <th>epoch</th>
      <th>train_loss</th>
      <th>valid_loss</th>
      <th>mae</th>
      <th>smape</th>
      <th>mse_loss</th>
      <th>theta</th>
      <th>b_loss</th>
      <th>time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>4.525622</td>
      <td>4.018864</td>
      <td>0.773341</td>
      <td>1.091936</td>
      <td>0.995230</td>
      <td>3.933015</td>
      <td>33.663334</td>
      <td>01:08</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2.175433</td>
      <td>1.932836</td>
      <td>0.729152</td>
      <td>1.042686</td>
      <td>0.878769</td>
      <td>4.470623</td>
      <td>12.260767</td>
      <td>01:09</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3.739684</td>
      <td>4.743078</td>
      <td>0.727991</td>
      <td>1.004584</td>
      <td>0.873061</td>
      <td>4.947448</td>
      <td>48.929226</td>
      <td>01:10</td>
    </tr>
  </tbody>
</table>



![png](docs/images/output_8_1.png)


```python
learn.show_results(1,max_n=9)
```






![png](docs/images/output_9_1.png)


## Interperation

```python
from fastai2.interpret import *
from fastseq.interpret import *
```

```python
interp = NBeatsInterpretation.from_learner(learn)
```





```python
interp.plot_top_losses(9)
```


![png](docs/images/output_13_0.png)

