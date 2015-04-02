#!/bin/bash

set -e

if env | grep -q "NYC_TREES_DEPLOY_DEBUG"; then
  set -x
fi

function packer_isotime() {
   date -u +"%Y-%m-%dT%H:%M:%SZ"
}

if (env | grep -q "NYC_TREES_PROMOTE_AMI" && env | grep -q "NYC_TREES_PROMOTE_ACCOUNT_ID"); then
    # Grant launch permissions to provided account ID
    aws ec2 modify-image-attribute \
        --image-id ${NYC_TREES_PROMOTE_AMI} \
        --operation-type add \
        --user-ids ${NYC_TREES_PROMOTE_ACCOUNT_ID} \
        --attribute launchPermission && \
    # Update tags on AMI to denote that it has been promoted
    # to production
    aws ec2 create-tags \
        --resources ${NYC_TREES_PROMOTE_AMI} \
        --tags Key=Environment,Value=Production Key=Promoted,Value=$(packer_isotime)
else
    echo "An AMI ID and AWS account ID to promote must be provided."

    exit 1
fi
