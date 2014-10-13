.DEFAULT: build
.PHONY: build clean

build:
	@find . -name "*.py" | grep -v "utils" | xargs -I{} python {}

clean:
	@rm *.json
