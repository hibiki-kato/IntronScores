import argparse
import os

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.artist import Artist
from matplotlib.backend_bases import PickEvent
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.text import Text

PLOT_BOUNDS_BY_SPECIES: dict[str, tuple[float, float, float, float]] = {
    "Athal": (10.0, 52.0, 48.0, 75.0),
    "Dmel": (40.0, 52.0, 40.0, 55.0),
    "Mmus": (10.0, 18.0, 40.0, 46.0),
    "Hsap": (10.0, 19.0, 27.0, 36.0),
}
FALLBACK_PLOT_BOUNDS: tuple[float, float, float, float] = (40.0, 50.0, 40.0, 50.0)

LEGEND_FONT_SIZE = 14
AXIS_TICK_FONT_SIZE = 16
AXIS_LABEL_FONT_SIZE = 18
TITLE_FONT_SIZE = 20
LEGEND_HIDDEN_ALPHA = 0.2
LEGEND_VISIBLE_ALPHA = 1.0
NON_GUI_BACKENDS: set[str] = {"agg", "cairo", "pdf", "pgf", "ps", "svg", "template"}

def resolve_plot_bounds(species: str) -> tuple[float, float, float, float]:
    """Resolve plotting bounds with species defaults."""
    default_bounds = PLOT_BOUNDS_BY_SPECIES.get(species)
    if default_bounds is None:
        return FALLBACK_PLOT_BOUNDS
    return default_bounds

def _sync_legend_entry_visibility(legend_handle: Artist, legend_text: Text, plotted_artist: Artist) -> None:
    """Match legend entry opacity to the plotted artist visibility."""
    alpha = LEGEND_VISIBLE_ALPHA
    if not plotted_artist.get_visible():
        alpha = LEGEND_HIDDEN_ALPHA
    legend_handle.set_alpha(alpha)
    legend_text.set_alpha(alpha)

def _connect_interactive_legend_toggle(fig: Figure, legend: Legend, labeled_artists: dict[str, Artist]):
    """Attach legend click handlers that toggle plotted artist visibility."""
    legend_targets = {}
    legend_handles = list(legend.legend_handles)
    legend_texts = list(legend.get_texts())

    for legend_handle, legend_text in zip(legend_handles, legend_texts):
        label = legend_text.get_text()
        plotted_artist = labeled_artists.get(label)
        if plotted_artist is None:
            continue
        
        legend_handle.set_picker(True)
        legend_text.set_picker(True)
        _sync_legend_entry_visibility(legend_handle, legend_text, plotted_artist)
        
        legend_targets[legend_handle] = (legend_handle, legend_text, plotted_artist)
        legend_targets[legend_text] = (legend_handle, legend_text, plotted_artist)

    def on_pick(event: PickEvent) -> None:
        """Toggle the artist associated with a picked legend entry."""
        target = legend_targets.get(event.artist)
        if target is None:
            return
        legend_handle, legend_text, plotted_artist = target
        plotted_artist.set_visible(not plotted_artist.get_visible())
        _sync_legend_entry_visibility(legend_handle, legend_text, plotted_artist)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("pick_event", on_pick)
    return on_pick

def _validate_interactive_backend() -> None:
    """Fail clearly when interactive plotting uses a non-GUI backend."""
    backend = matplotlib.get_backend().lower()
    if backend in NON_GUI_BACKENDS:
        raise RuntimeError(
            "Interactive plotting requires a GUI Matplotlib backend, "
            f"but the current backend is '{matplotlib.get_backend()}'. "
            "Ensure DISPLAY/XAUTHORITY are available."
        )

def plot_eval_scores(species: str, data_dir: str, out_png: str | None = None, interactive: bool = False) -> Figure | None:
    """Plot sensitivity/precision points from eval text files.
    
    If out_png is None, the plot will not be saved.
    Returns the Matplotlib Figure object.
    """
    if interactive and out_png is not None:
        _validate_interactive_backend()

    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    files = [f for f in os.listdir(data_dir) if f.endswith(".txt")]
    files.sort()
    if not files:
        raise FileNotFoundError(f"No .txt files found under: {data_dir}")

    fig, ax = plt.subplots(figsize=(16, 12), dpi=100)
    markers = ["o", "s", "^", "D", "v", "p", "*", "h", "x", "+"]
    labeled_artists: dict[str, Artist] = {}

    for index, filename in enumerate(files):
        data = np.loadtxt(os.path.join(data_dir, filename), usecols=(3, 4))
        if data.ndim == 1:
            data = np.expand_dims(data, axis=0)
        sensitivity = data[:, 0]
        precision = data[:, 1]
        label = filename[:-4]
        
        scatter_artist = ax.scatter(
            sensitivity,
            precision,
            s=2,
            marker=markers[index % len(markers)],
            label=label,
        )
        labeled_artists[label] = scatter_artist

    x_min, x_max, y_min, y_max = resolve_plot_bounds(species)
    print(f"Plotting bounds: x=({x_min}, {x_max}) y=({y_min}, {y_max})")

    ax.set_xlabel("Sensitivity", fontsize=AXIS_LABEL_FONT_SIZE)
    ax.set_ylabel("Precision", fontsize=AXIS_LABEL_FONT_SIZE)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_title(species, fontsize=TITLE_FONT_SIZE)
    ax.tick_params(axis="both", labelsize=AXIS_TICK_FONT_SIZE)
    ax.set_aspect("equal")
    ax.grid(True, linestyle="--", alpha=0.5)
    
    legend = ax.legend(markerscale=7, fontsize=LEGEND_FONT_SIZE, loc="lower left")
    
    # Enable interactive legend clicking for visibility toggling
    if interactive or out_png is None:
        _connect_interactive_legend_toggle(fig, legend, labeled_artists)

    if out_png:
        out_parent = os.path.dirname(out_png)
        if out_parent:
            os.makedirs(out_parent, exist_ok=True)
            
        plt.savefig(out_png)
        print(f"Saved plot to {out_png}")
        
    if interactive and out_png is not None:
        plt.show(block=True)
        
    return fig

def plot_eval_scores_plotly(species: str, data_dir: str):
    """Plot sensitivity/precision points from eval text files using Plotly for interactive web displays."""
    try:
        import plotly.graph_objects as go
    except ImportError:
        raise ImportError("plotly must be installed to use this interactive function.")

    if not os.path.isdir(data_dir):
        raise FileNotFoundError(f"Directory not found: {data_dir}")

    files = [f for f in os.listdir(data_dir) if f.endswith(".txt")]
    files.sort()
    if not files:
        raise FileNotFoundError(f"No .txt files found under: {data_dir}")

    # Plotly translates Matplotlib markers a bit differently. These are approximations.
    markers = ["circle", "square", "triangle-up", "diamond", "triangle-down", "pentagon", "star", "hexagon", "x", "cross"]
    x_min, x_max, y_min, y_max = resolve_plot_bounds(species)
    
    fig = go.Figure()
    
    for index, filename in enumerate(files):
        data = np.loadtxt(os.path.join(data_dir, filename), usecols=(3, 4))
        if data.ndim == 1:
            data = np.expand_dims(data, axis=0)
        sensitivity = data[:, 0]
        precision = data[:, 1]
        label = filename[:-4]
        
        # We only want to show the legend for the first trace of each file if we sub-grouped,
        # but here each file is one trace.
        fig.add_trace(go.Scatter(
            x=sensitivity,
            y=precision,
            mode='markers',
            name=label,
            marker=dict(
                symbol=markers[index % len(markers)],
                size=4
            )
        ))

    fig.update_layout(
        title=species,
        xaxis_title="Sensitivity",
        yaxis_title="Precision",
        xaxis=dict(range=[x_min, x_max]),
        yaxis=dict(range=[y_min, y_max], scaleanchor="x", scaleratio=1), # Make aspect equal
        legend=dict(
            itemsizing='constant' # Make legend markers larger if we want, currently keeps them uniform
        ),
        template="plotly_white",
        width=800,
        height=600
    )
    
    # Enable toggling off specific traces by clicking the legend (this is enabled by default in plotly)
    return fig

def main():
    parser = argparse.ArgumentParser(description="Plot IntronScores evaluation results.")
    parser.add_argument("--species", required=True, help="Species name")
    parser.add_argument("--data_dir", required=True, help="Directory containing eval_score text files")
    parser.add_argument("--out_png", required=True, help="Path to save output PNG")
    parser.add_argument("--interactive", choices=["on", "off"], default="off", help="Interactive plot mode")

    args = parser.parse_args()

    # Create the output directory if it does not exist
    os.makedirs(os.path.dirname(os.path.abspath(args.out_png)), exist_ok=True)

    plot_eval_scores(
        species=args.species,
        data_dir=args.data_dir,
        out_png=args.out_png,
        interactive=(args.interactive == "on")
    )

if __name__ == "__main__":
    main()
