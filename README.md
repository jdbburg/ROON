# ROON

A node bsed editor for python using with a modern svelte frontend UI

Use Meta+Shift+P to access command prompt

## Commands
- `:n`: all nodes that can be inserted into the graph have `:n` in the title for quick search. Nodes can be searched for by name or module
- `Source2Nodes`: Convert the source in the editor window into a node and insert it into the graph - source must contain function definitions or no nodes will be generated

# Development
## Svelte Application
Uses rollup + svelte
For development (live reload etc.):
```
npm run dev
```

For a production build:
```
npm run build
```

Note: the `.env` file is used to set the python backend:
```
PYTHON_BACKEND=auto
```
Options are: `auto`, `pyodide`, `pywebview`, `jupyter` - but `pywebview` is the primary target with others to be implemented later. Pyodide works for a fully browser based implementation, but the filesystem (needed for any real data analysis) is only supported in chrome and edge.

Make sure that production builds for the python package are setup with `pywebview` - because it takes some time for the js bridge to fully load, the automatic detection of the backend is slower than being set directly.

note: the svelte app is setup to write out the build files to a custom directory for integration with python app (in the `roon/static/` directory) instead of the standard `public`. So you need to symlink to make development builds available in browser (if you want to work in the browser)
```
ln -s roon/static/svelte/public public
```

## Python application

Use makefile for installing development builds and for building the package for publication
```
dev-build:
	python -m pip install --editable .

build:
	python -m build
```

We use twine to publish the pypi package (use Makefile target `check` and `publish`)
Twine uses authentication in `$HOME/.pypirc` for pushing to PyPi.


# ROADMAP
- Fix widgets
- hotkeys for inserting nodes
- view node source
- import nodes from libs directly from (numpy) or provide wrapper
- write nodes in app
- "h" - home hotkey to zoom according to actual extend of nodes in graph
- comment out nodes
- dynamic nodes: dictionaries and kwargs etc.
- viewer nodes for plots etc.
- pause python execution for input (view plots one at a time...)

