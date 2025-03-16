import uproot
import json
import numpy as np
import matplotlib.pyplot as plt
from typing import TypedDict
import os

class RootFileResult(TypedDict):
    """
    Represents the outcome of opening a ROOT file.
    - file: the uproot.ReadOnlyDirectory object
    - keys: top-level object names/keys in the file
    - view: a JSON string showing classnames for a quick textual overview
    """
    file: uproot.ReadOnlyDirectory
    keys: list[str]
    view: str

def open_root_file(path: str = "/example.root") -> RootFileResult:
    """
    Opens a ROOT file using uproot, returning:
      - the file object
      - a list of top-level keys
      - a JSON 'view' of classnames for quick inspection
    """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {path} not found in Pyodide file system")
        if os.path.getsize(path) == 0:
            raise ValueError(f"File {path} is empty")
        f = uproot.open(path)
        print(f"Opening ROOT file: {path}")
        f = uproot.open(path)
        view = json.dumps(f.classnames(), indent=4)
        return {
            "file": f,
            "keys": f.keys(),
            "view": view,
        }
    except Exception as e:
        print(f"Error opening {path}: {e}")
        raise

class TreeArrayResult(TypedDict):
    """
    Represents the outcome of reading a TTree branch.
    - array: the NumPy array of data from that branch
    - stats: basic descriptive statistics (mean, std, min, max)
    """
    array: np.ndarray
    stats: dict[str, float]

def read_tree_branch(
    root_file: uproot.ReadOnlyDirectory,
    tree_name: str,
    branch_name: str
) -> TreeArrayResult:
    """
    Reads a single branch from a TTree in the given RootFileResult.
    Returns the data as a NumPy array, plus basic statistics.
    """
    # Retrieve the opened file object from the typed dict
    f = root_file
    # Access the TTree
    tree = f[tree_name]
    # Read the branch into a NumPy array
    arr = tree[branch_name].array(library="np")

    # Compute basic stats
    stats = {
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
    }

    return {
        "array": arr,
        "stats": stats,
    }

class PlotResult(TypedDict):
    """
    Represents the outcome of creating a plot.
    - path: file path where the plot was saved
    - description: a short message describing the plot
    """
    path: str
    description: str

def plot_histogram(
    data: np.ndarray,
    bins: int = 50,
    out_path: str = "hist.png",
    title: str = "Histogram"
) -> PlotResult:
    """
    Creates a histogram of the given data using matplotlib, saves the figure to 'out_path',
    and returns a small typed dict with the path and a description.
    """
    plt.figure()
    plt.hist(data, bins=bins, edgecolor='black')
    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.savefig(out_path)
    plt.close()

    return {
        "path": out_path,
        "description": f"Histogram saved to {out_path}"
    }