VERSION=0.4.10

build:
	python -m build

dev-build:
	python -m pip install --editable .

check:
	echo "Checking roon version $(VERSION)"
	twine check dist/*$(VERSION)*

publish:
	echo "Publishing roon version $(VERSION)"
	python -m build
	twine upload dist/*$(VERSION)*