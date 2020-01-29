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
data = TSDataLoaders.from_folder(path, horizon = 14, nrows = 300,step=3)
```

    Train:68161; Valid: 900; Test 300


```python
data.show_batch()
```


![png](docs/images/output_5_0.png)


```python
# TODO make custom learner with custom model
learn = nbeats_learner(data,layers=[512, 512], stack_types=("trend","seasonality"), b_loss=.4, nb_blocks_per_stack=5,
                       loss_func=CombinedLoss(F.mse_loss, smape, ratio = {'smape':.05})
                      )
```

```python
from fastai2.callback.all import *
learn.lr_find()
```






    ---------------------------------------------------------------------------

    TypeError                                 Traceback (most recent call last)

    <ipython-input-8-bd8b18fd11a5> in <module>
          1 from fastai2.callback.all import *
    ----> 2 learn.lr_find()
    

    ~/dev/fastai2/fastai2/callback/schedule.py in lr_find(self, start_lr, end_lr, num_it, stop_div, show_plot)
        194     n_epoch = num_it//len(self.dls.train) + 1
        195     cb=LRFinder(start_lr=start_lr, end_lr=end_lr, num_it=num_it, stop_div=stop_div)
    --> 196     with self.no_logging(): self.fit(n_epoch, cbs=cb)
        197     if show_plot: self.recorder.plot_lr_find()


    ~/dev/fastai2/fastai2/learner.py in fit(self, n_epoch, lr, wd, cbs, reset_opt)
        287                     try:
        288                         self.epoch=epoch;          self('begin_epoch')
    --> 289                         self._do_epoch_train()
        290                         self._do_epoch_validate()
        291                     except CancelEpochException:   self('after_cancel_epoch')


    ~/dev/fastai2/fastai2/learner.py in _do_epoch_train(self)
        262         try:
        263             self.dl = self.dls.train;                  self('begin_train')
    --> 264             self.all_batches()
        265         except CancelTrainException:                         self('after_cancel_train')
        266         finally:                                             self('after_train')


    ~/dev/fastai2/fastai2/learner.py in all_batches(self)
        240     def all_batches(self):
        241         self.n_iter = len(self.dl)
    --> 242         for o in enumerate(self.dl): self.one_batch(*o)
        243 
        244     def one_batch(self, i, b):


    ~/dev/fastai2/fastai2/data/load.py in __iter__(self)
         95         self.randomize()
         96         self.before_iter()
    ---> 97         for b in _loaders[self.fake_l.num_workers==0](self.fake_l):
         98             if self.device is not None: b = to_device(b, self.device)
         99             yield self.after_batch(b)


    ~/dev/env37/lib/python3.7/site-packages/torch/utils/data/dataloader.py in __next__(self)
        817             else:
        818                 del self._task_info[idx]
    --> 819                 return self._process_data(data)
        820 
        821     next = __next__  # Python 2 compatibility


    ~/dev/env37/lib/python3.7/site-packages/torch/utils/data/dataloader.py in _process_data(self, data)
        844         self._try_put_index()
        845         if isinstance(data, ExceptionWrapper):
    --> 846             data.reraise()
        847         return data
        848 


    ~/dev/env37/lib/python3.7/site-packages/torch/_utils.py in reraise(self)
        383             # (https://bugs.python.org/issue2651), so we work around it.
        384             msg = KeyErrorMessage(msg)
    --> 385         raise self.exc_type(msg)
    

    TypeError: Caught TypeError in DataLoader worker process 0.
    Original Traceback (most recent call last):
      File "/home/tako/dev/env37/lib/python3.7/site-packages/torch/utils/data/_utils/worker.py", line 135, in _worker_loop
        init_fn(worker_id)
      File "/home/tako/dev/fastai2/fastai2/data/load.py", line 17, in _wif
        set_seed(info.seed)
      File "/home/tako/dev/fastai2/fastai2/torch_core.py", line 123, in set_seed
        try: np.random.seed(s%(2**32-1))
    TypeError: 'int' object is not callable



```python
learn.fit_one_cycle(3, 1e-4, cbs=cbs)
learn.recorder.plot_loss()
```

```python
learn.show_results(2,max_n=9)
```

## Interperation

```python
from fastai2.interpret import *
from fastseq.interpret import *
```

```python
interp = NBeatsInterpretation.from_learner(learn)
```

```python
interp.plot_top_losses(3)
```
