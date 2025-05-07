import os
import matplotlib.pyplot as plt
from utils import init_logger

# Use Agg backend for headless environments
plt.switch_backend('Agg')
logger = None

def init_visualizer(cfg):
    """
    Initialize the logger for visualizations based on configuration.
    """
    global logger
    logger = init_logger(cfg['logging']['file'], cfg['logging']['level'])


def plot_pie(df, names_col, values_col, title, out_dir):
    """Filter out NaNs/zeros before plotting."""
    try:
        d = df[[names_col, values_col]].copy()
        d = d.dropna(subset=[values_col])
        d = d[d[values_col] > 0]
        if d.empty:
            logger.warning(f"No valid data for pie chart '{title}'")
            return None

        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, _, _ = ax.pie(d[values_col], labels=None, autopct='%1.1f%%')
        ax.legend(wedges, d[names_col], title=title, loc='best', bbox_to_anchor=(1,0,0.5,1))
        ax.axis('equal'); ax.set_title(title)

        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"pie_{title.replace(' ', '_')}.png")
        fig.savefig(path, bbox_inches='tight')
        logger.info(f"Saved pie chart: {path}")
        plt.close(fig)
        return path

    except Exception as e:
        logger.warning(f"Pie chart generation failed for {title}: {e}")
        return None


def plot_line(df, x_col, y_col, title, out_dir):
    """
    Generate a line chart for a single metric.
    Rotates X-axis labels for readability.
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df[x_col], df[y_col], marker='o')
        ax.set_title(title)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(45)
            lbl.set_ha('right')
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"line_{y_col}.png")
        fig.savefig(path, bbox_inches='tight')
        logger.info(f"Saved line chart: {path}")
        plt.close(fig)
        return path
    except Exception as e:
        logger.warning(f"Line chart generation failed for {y_col}: {e}")
        return None


def plot_multi_line(data_maps, x_col, y_col, title, out_dir):
    """
    Generate a combined line chart for multiple segments on one plot.
    data_maps: dict of label -> DataFrame.
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        for label, df in data_maps.items():
            if x_col in df.columns and y_col in df.columns:
                ax.plot(df[x_col], df[y_col], marker='o', label=label)
        ax.set_title(title)
        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.legend()
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(45)
            lbl.set_ha('right')
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, f"multi_line_{y_col}.png")
        fig.savefig(path, bbox_inches='tight')
        logger.info(f"Saved multi-line chart: {path}")
        plt.close(fig)
        return path
    except Exception as e:
        logger.warning(f"Multi-line chart generation failed for {y_col}: {e}")
        return None
