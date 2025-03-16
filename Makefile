VERSION=0.4.5

build:
	python -m build

dev-build:
	python -m pip install --editable .

check:
	twine check dist/*

publish:
	python -m build
	twine upload dist/*$(VERSION)*