.PHONY: build clean
.PHONY: vpc-stack update-vpc-stack
.PHONY: private-dns-stack update-private-dns-stack
.PHONY: data-store-stack monitoring-ami tiler-stack app-stack
.PHONY: app-and-tiler-amis

build:
	@find troposphere -name "*.py" | grep -v "utils" | xargs -I{} python {}

clean:
	@rm troposphere/*.json

vpc-stack:
	./deployment-helper.sh create-vpc-stack

data-store-stack:
	./deployment-helper.sh create-data-store-stack

private-dns-stack:
	./deployment-helper.sh create-private-dns-stack

monitoring-ami:
	./deployment-helper.sh create-monitoring-ami

update-vpc-stack:
	./deployment-helper.sh update-vpc-stack

update-private-dns-stack:
	./deployment-helper.sh update-private-dns-stack

app-and-tiler-amis:
	./deployment-helper.sh create-app-and-tiler-amis

tiler-stack:
	./deployment-helper.sh create-tiler-stack

app-stack:
	./deployment-helper.sh create-app-stack

app-ami:
	./deployment-helper.sh create-app-ami
