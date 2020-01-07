# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/08_metrics.ipynb (unless otherwise specified).

__all__ = ['mape', 'smape', 'mase']

# Cell
from fastcore.utils import *
from fastcore.imports import *
from fastai2.basics import *


# Cell

def mape(data_samples, data_truth, agg=None, **kwargs) -> np.array:
    """Computes mean absolute percentage error (MAPE)
    Arguments:
        * data_samples (``np.array``): Sampled predictions (n_samples, n_timeseries, n_variables, n_timesteps).
        * data_truth (``np.array``): Ground truth time series values (n_timeseries, n_variables, n_timesteps).
        * agg: Aggregation function applied to sampled predictions (defaults to ``np.median``).
    """
    if data_samples.shape[1:] != data_truth.shape:
        raise ValueError('Last three dimensions of data_samples and data_truth need to be compatible')
    agg = np.median if not agg else agg

    # Aggregate over samples
    data = agg(data_samples, axis=0)

    norm = np.abs(data_truth)

    return np.mean(np.abs(data - data_truth) / norm, axis=(1, 2)) * 100.0

# Cell
def _smape(data_samples, data_truth, agg=None, **kwargs) -> np.array:
    """Computes symmetric mean absolute percentage error (SMAPE) on the mean

    Arguments:
        * data_samples (``np.array``): Sampled predictions (n_samples, n_timeseries, n_variables, n_timesteps).
        * data_truth (``np.array``): Ground truth time series values (n_timeseries, n_variables, n_timesteps).
        * agg: Aggregation function applied to sampled predictions (defaults to ``np.median``).
    """
    if data_samples.shape[1:] != data_truth.shape:
        raise ValueError('Last three dimensions of data_samples and data_truth need to be compatible')
    agg = np.median if not agg else agg

    # Aggregate over samples
    data = agg(data_samples, axis=0)

    eps = 1e-16  # Need to make sure that denominator is not zero
    norm = 0.5 * (np.abs(data) + np.abs(data_truth)) + eps

    return np.mean(np.abs(data - data_truth) / norm, axis=(1, 2)) * 100

def smape(pred, truth, agg=None, **kwargs) -> np.array:
    """Computes symmetric mean absolute percentage error (SMAPE) on the mean

    Arguments:
        * data_samples (``np.array``): Sampled predictions (n_timeseries, n_variables, n_timesteps).
        * data_truth (``np.array``): Ground truth time series values (n_timeseries, n_variables, n_timesteps).
        * agg: Aggregation function applied to sampled predictions (defaults to ``np.median``).
    """
    if pred.shape[:-3] != truth.shape:
        raise ValueError('Last three dimensions of data_samples and data_truth need to be compatible')
    if len(pred.shape)==4:
        agg = np.median if not agg else agg
        # Aggregate over samples
        pred = agg(pred, axis=0)

    eps = 1e-16  # Need to make sure that denominator is not zero
    norm = 0.5 * (np.abs(pred) + np.abs(truth)) + eps

    return np.mean(np.abs(pred - truth) / norm, axis=(1, 2)) * 100

# Cell
def _mase(data_samples,
         data_truth,
         data_insample,
         frequencies,
         agg=None,
         **kwargs) -> np.array:
    """Computes mean absolute scaled error (MASE) as in the `M4 competition
    <https://www.m4.unic.ac.cy/wp-content/uploads/2018/03/M4-Competitors-Guide.pdf>`_.
    Arguments:
        * data_samples (``np.array``): Sampled predictions (n_samples, n_timeseries, n_variables, n_timesteps).
        * data_truth (``np.array``): Ground truth time series values (n_timeseries, n_variables, n_timesteps).
        * data_insample (``np.array``): In-sample time series data (n_timeseries, n_variables, n_timesteps).
        * frequencies (list): Frequencies to be used when calculating the naive forecast.
        * agg: Aggregation function applied to sampled predictions (defaults to ``np.median``).
    """
    if data_samples.shape[1:] != data_truth.shape:
        raise ValueError('Last three dimensions of data_samples and data_truth need to be compatible')
    agg = np.median if not agg else agg

    # Calculate mean absolute for forecast and naive forecast per time series
    errs, naive_errs = [], []
    for i in range(data_samples.shape[1]):
        ts_sample = data_samples[:, i]
        ts_truth = data_truth[i]
        ts = data_insample[i]
        freq = int(frequencies[i])

        data = agg(ts_sample, axis=0)

        # Build mean absolute error
        err = np.mean(np.abs(data - ts_truth))

        # naive forecast is calculated using insample
        t_in = ts.shape[-1]
        naive_forecast = ts[:, :t_in-freq]
        naive_target = ts[:, freq:]
        err_naive = np.mean(np.abs(naive_target - naive_forecast))

        errs.append(err)
        naive_errs.append(err_naive)

    errs = np.array(errs)
    naive_errs = np.array(naive_errs)

    return errs / naive_errs

def mase(data_samples,
         data_truth,
         data_insample,
         frequencies,
         agg=None,
         **kwargs) -> np.array:
    """Computes mean absolute scaled error (MASE) as in the `M4 competition
    <https://www.m4.unic.ac.cy/wp-content/uploads/2018/03/M4-Competitors-Guide.pdf>`_.
    Arguments:
        * data_samples (``np.array``): Sampled predictions (n_samples, n_timeseries, n_variables, n_timesteps).
        * data_truth (``np.array``): Ground truth time series values (n_timeseries, n_variables, n_timesteps).
        * data_insample (``np.array``): In-sample time series data (n_timeseries, n_variables, n_timesteps).
        * frequencies (list): Frequencies to be used when calculating the naive forecast.
        * agg: Aggregation function applied to sampled predictions (defaults to ``np.median``).
    """
    if data_samples.shape[1:] != data_truth.shape:
        raise ValueError('Last three dimensions of data_samples and data_truth need to be compatible')
    if len(data_samples.shape)==4:
        agg = np.median if not agg else agg
        data_samples = agg(data_samples,
                           axis = 0)

    # Calculate mean absolute for forecast and naive forecast per time series
    errs, naive_errs = [], []
    for i in range(data_samples.shape[0]):
        ts_sample = data_samples[i]
        ts_truth = data_truth[i]
        ts = data_insample[i]
        freq = int(frequencies[i])
        # Build mean absolute error
        err = np.mean(np.abs(ts_sample - ts_truth))

        # naive forecast is calculated using insample
        t_in = ts.shape[-1]
        naive_forecast = ts[:, :t_in-freq]
        naive_target = ts[:, freq:]
        err_naive = np.mean(np.abs(naive_target - naive_forecast))

        errs.append(err)
        naive_errs.append(err_naive)

    errs = np.array(errs)
    naive_errs = np.array(naive_errs)

    return errs / naive_errs