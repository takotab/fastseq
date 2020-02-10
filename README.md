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
from fastseq.nbeats.learner import *
horizon, lookback = 7, 35    
```

Getting the data fastai style:

```python
path = untar_data(URLs.m4_daily)
data = TSDataLoaders.from_folder(path, horizon = horizon, lookback = lookback, nrows = 300, step=3, max_std=1.5)
```

    torch.Size([1, 1020])
    Train:70707; Valid: 1200; Test 300


```python
data.show_batch()
```


![png](docs/images/output_5_0.png)


```python
from fastseq.nbeats.callbacks import *
learn = nbeats_learner(data, cbs=ClipLoss(20), season =lookback+horizon)   
```

```python
from fastai2.callback.all import *
learn.lr_find()
```






![png](docs/images/output_7_1.png)


```python
learn.fit_flat_cos(5, 2e-2)
learn.recorder.plot_loss()
learn.recorder.plot_sched()
```


<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: left;">
      <th>epoch</th>
      <th>train_loss</th>
      <th>valid_loss</th>
      <th>mae</th>
      <th>smape</th>
      <th>theta</th>
      <th>b_loss</th>
      <th>f_loss</th>
      <th>time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>1.540548</td>
      <td>2.303195</td>
      <td>2834467.500000</td>
      <td>0.772452</td>
      <td>1.759676</td>
      <td>nan</td>
      <td>nan</td>
      <td>01:22</td>
    </tr>
    <tr>
      <td>1</td>
      <td>1.536659</td>
      <td>2.219578</td>
      <td>2834467.500000</td>
      <td>0.768887</td>
      <td>1.594365</td>
      <td>nan</td>
      <td>nan</td>
      <td>01:22</td>
    </tr>
    <tr>
      <td>2</td>
      <td>1.409645</td>
      <td>2.161446</td>
      <td>2834467.500000</td>
      <td>0.712815</td>
      <td>1.681730</td>
      <td>nan</td>
      <td>nan</td>
      <td>01:23</td>
    </tr>
    <tr>
      <td>3</td>
      <td>1.415572</td>
      <td>2.195107</td>
      <td>2834467.500000</td>
      <td>0.724577</td>
      <td>1.614143</td>
      <td>nan</td>
      <td>nan</td>
      <td>01:24</td>
    </tr>
    <tr>
      <td>4</td>
      <td>1.300322</td>
      <td>2.121976</td>
      <td>2834467.500000</td>
      <td>0.677533</td>
      <td>1.609086</td>
      <td>nan</td>
      <td>nan</td>
      <td>01:22</td>
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


```python
learn.fit_flat_cos(5,5e-4)
learn.recorder.plot_loss()
learn.recorder.plot_sched()
```

## Interperation

```python
learn.n_beats_attention.means()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>trend0_0</th>
      <th>trend0_1</th>
      <th>seasonality1_0</th>
      <th>seasonality1_1</th>
      <th>seasonality1_2</th>
      <th>seasonality1_3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>theta_0_mean</th>
      <td>1.0484735</td>
      <td>0.5712331</td>
      <td>0.7695762</td>
      <td>-0.13409285</td>
      <td>-0.165535</td>
      <td>0.5304334</td>
    </tr>
    <tr>
      <th>theta_0_std</th>
      <td>0.53147</td>
      <td>0.5104649</td>
      <td>0.89892924</td>
      <td>0.12476344</td>
      <td>0.11738308</td>
      <td>1.0524368</td>
    </tr>
    <tr>
      <th>theta_1_mean</th>
      <td>0.0</td>
      <td>-0.008486307</td>
      <td>0.33995187</td>
      <td>-0.123186365</td>
      <td>-0.072090976</td>
      <td>0.2616474</td>
    </tr>
    <tr>
      <th>theta_1_std</th>
      <td>0.0</td>
      <td>0.008260585</td>
      <td>0.25519606</td>
      <td>0.20760116</td>
      <td>0.3698771</td>
      <td>0.18846405</td>
    </tr>
    <tr>
      <th>theta_2_mean</th>
      <td>-0.0034576228</td>
      <td>-0.0004631914</td>
      <td>0.09690633</td>
      <td>-0.085941315</td>
      <td>-0.055885807</td>
      <td>-0.046996526</td>
    </tr>
    <tr>
      <th>theta_2_std</th>
      <td>0.0018157117</td>
      <td>0.0012395354</td>
      <td>0.120248154</td>
      <td>0.15570128</td>
      <td>0.07383171</td>
      <td>0.09366264</td>
    </tr>
    <tr>
      <th>theta_3_mean</th>
      <td>0.044545975</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>-0.0034272978</td>
      <td>0.09713822</td>
      <td>0.18888618</td>
    </tr>
    <tr>
      <th>theta_3_std</th>
      <td>0.030647082</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.03154439</td>
      <td>0.15776587</td>
      <td>0.62231266</td>
    </tr>
    <tr>
      <th>theta_4_mean</th>
      <td>0.2584329</td>
      <td>0.049222477</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.005607492</td>
      <td>-0.03192711</td>
    </tr>
    <tr>
      <th>theta_4_std</th>
      <td>0.44719952</td>
      <td>0.06712501</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.059638757</td>
      <td>0.30349037</td>
    </tr>
    <tr>
      <th>theta_5_mean</th>
      <td>-0.13016799</td>
      <td>0.07761635</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.026232796</td>
    </tr>
    <tr>
      <th>theta_5_std</th>
      <td>0.22034122</td>
      <td>1.1497012</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.1286816</td>
    </tr>
    <tr>
      <th>att_mean</th>
      <td>0.443135</td>
      <td>0.715307</td>
      <td>0.775233</td>
      <td>0.568036</td>
      <td>0.799381</td>
      <td>0.971488</td>
    </tr>
    <tr>
      <th>att_std</th>
      <td>0.436081</td>
      <td>0.409965</td>
      <td>0.416275</td>
      <td>0.494035</td>
      <td>0.394072</td>
      <td>0.164985</td>
    </tr>
    <tr>
      <th>theta_6_mean</th>
      <td>NaN</td>
      <td>0.22906151</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>theta_6_std</th>
      <td>NaN</td>
      <td>1.1522285</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>theta_7_mean</th>
      <td>NaN</td>
      <td>-0.32102555</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>theta_7_std</th>
      <td>NaN</td>
      <td>0.52404284</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>


