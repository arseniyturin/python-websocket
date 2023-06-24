.PHONY: example test

example:
	pip install ./src
	python ./example/chat.py

test:
	python -m unittest ./src/tests
