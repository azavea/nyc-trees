.PHONY: build clean
.PHONY: vpc-stack
.PHONY: private-hosted-zones
.PHONY: data-store-stack
.PHONY: monitoring-ami app-ami tiler-ami app-and-tiler-amis
.PHONY: tiler-stack app-stack app-stack-green app-stack-blue
.PHONY: delete-green-app-stack delete-blue-app-stack

build:
	@find troposphere -name "*.py" | grep -v "utils" | xargs -I{} python {}

clean:
	@rm troposphere/*.json

vpc-stack: build
	./deployment-helper.sh create-vpc-stack

data-store-stack: build
	./deployment-helper.sh create-data-store-stack

private-hosted-zones:
	./deployment-helper.sh create-private-hosted-zones

monitoring-ami:
	./deployment-helper.sh create-monitoring-ami

app-ami:
	./deployment-helper.sh create-app-ami

tiler-ami:
	./deployment-helper.sh create-tiler-ami

app-and-tiler-amis:
	./deployment-helper.sh create-app-and-tiler-amis

tiler-stack: build
	./deployment-helper.sh create-tiler-stack

app-stack: build
	./deployment-helper.sh create-app-stack

delete-green-app-stack:
	./deployment-helper.sh delete-green-app-stack

delete-blue-app-stack:
	./deployment-helper.sh delete-blue-app-stack

delete-green-tiler-stack:
	./deployment-helper.sh delete-green-tiler-stack

delete-blue-tiler-stack:
	./deployment-helper.sh delete-blue-tiler-stack

app-stack-green: build
	./deployment-helper.sh toggle-green-app-stack

app-stack-blue: build
	./deployment-helper.sh toggle-blue-app-stack

tiler-stack-green: build
	./deployment-helper.sh toggle-green-tiler-stack

tiler-stack-blue: build
	./deployment-helper.sh toggle-blue-tiler-stack
