import pandas as pd
from utils import init_logger
import numpy as np

logger = None

def init_analyzer(cfg):
    global logger
    logger = init_logger(cfg['logging']['file'], cfg['logging']['level'])


def compute_summary(df, label):
    clicks = int(df['clicks'].sum())
    impr = int(df['impressions'].sum())
    ctr = clicks / impr if impr else 0
    avgp = (df['position'] * df['impressions']).sum() / impr if impr else 0
    logger.info(f"[{label}] clicks={clicks}, impressions={impr}, CTR={ctr:.2%}, AvgPos={avgp:.2f}")
    return {'segment': label, 'clicks': clicks, 'impressions': impr, 'ctr': ctr, 'avg_position': avgp}


def segment_dataframe(df, regex):
    """Split into branded vs non-branded vs anonymous by simple regex containment."""
    branded   = df[df['query'].str.contains(regex, regex=True, na=False)]
    nonb      = df[~df['query'].str.contains(regex, regex=True, na=False)]
    anonymous = df.drop(branded.index).drop(nonb.index)
    logger.info(f"Segments sizes: branded={len(branded)}, nonb={len(nonb)}, anon={len(anonymous)}")
    return branded, nonb, anonymous

def detect_low_hanging(df, min_impressions, max_ctr):
    df['ctr_calc'] = df['clicks'] / df['impressions']
    low = df[(df['impressions'] >= min_impressions) & (df['ctr_calc'] < max_ctr)].copy()
    logger.info(f"Low-hanging opportunities: {len(low)}")
    return low


def compute_mom(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M')
    agg = df.groupby('month').agg({
        'clicks': 'sum',
        'impressions': 'sum',
        'ctr': lambda x: x.sum() / df.loc[x.index, 'impressions'].sum(),
        'position': lambda x: (x * df.loc[x.index, 'impressions']).sum() / df.loc[x.index, 'impressions'].sum()
    }).reset_index()
    agg['month'] = agg['month'].dt.to_timestamp()
    agg.rename(columns={'position': 'avg_position'}, inplace=True)
    agg['month_label'] = agg['month'].dt.strftime('%B %Y')
    agg['delta_clicks'] = agg['clicks'].diff()
    agg['pct_clicks'] = agg['delta_clicks'] / agg['clicks'].shift(1)
    return agg

import numpy as np

def detect_anomalies(df, date_col='date', metric='clicks',
                     window=7, z_thresh=2.5):
    """
    Flags points where the metric deviates > z_thresh * rolling_std from rolling_mean.
    Returns a DataFrame of anomalies.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    # rolling stats
    df['roll_mean'] = df[metric].rolling(window, min_periods=1, center=True).mean()
    df['roll_std' ] = df[metric].rolling(window, min_periods=1, center=True).std().fillna(0)
    # z-score
    df['z_score']  = (df[metric] - df['roll_mean']) / df['roll_std'].replace(0, np.nan)
    # flag anomalies
    df['anomaly']  = df['z_score'].abs() >= z_thresh
    return df[df['anomaly']].loc[:, [date_col, metric, 'roll_mean', 'roll_std', 'z_score']]
