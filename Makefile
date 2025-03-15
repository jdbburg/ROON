

build:
	python -m build

dev-build:
	python -m pip install --editable .

update-svelte:
	rm -rf roon/static/svelte/*
	cp -r public/* roon/static/svelte/