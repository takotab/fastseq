SRC = $(wildcard nbs/*.ipynb)

all: fastseq docs

fastseq: $(SRC)
	nbdev_build_lib
	touch fastseq

docs: $(SRC)
	nbdev_build_docs
	touch docs

test:
	nbdev_test_nbs

release: bump dist
	twine upload --repository pypi dist/*

pypi: dist
	twine upload --repository pypi dist/*

bump:
	nbdev_bump_version

dist: clean
	python setup.py sdist bdist_wheel

clean:
	rm -rf dist