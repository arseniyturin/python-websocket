.PHONY: install tests example build

all: install tests example

build:
	python -m pip install --upgrade build
	python -m build

install:
	python -m pip install .

tests:
	python -m unittest -v

example:
	python ./example/chat.py
