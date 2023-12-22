.PHONY: install tests example

all: install tests example

install:
	python -m pip install .

tests:
	python -m unittest -v

example:
	python ./example/chat.py
