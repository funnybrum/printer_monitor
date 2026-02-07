.PHONY: all build run test clean

all: build test

build:
	docker build -t printer_monitor .

run:
	docker run -it --rm -v $(PWD)/config:/app/config printer_monitor

test:
	python3 -m unittest discover -s tests

clean:
	rm -f tests/test_config.yaml
	rm -f config/config.yaml
