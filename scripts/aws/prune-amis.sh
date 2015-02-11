#!/bin/bash

set -e

if env | grep -q "NYC_TREES_DEPLOY_DEBUG"; then
  set -x
fi

# Given the AMI name, produce the AMI and EBS snapshot ID, and remove
# them.
function prune_ami() {
    echo "  Identified that [${1}] is eligible to be pruned.."

    IMAGE_AND_SNAPSHOT_ID=$(aws ec2 describe-images \
        --owners self \
        --filters Name=name,Values=$1 \
        --query "Images[*].[ImageId, BlockDeviceMappings[0].Ebs.SnapshotId]")

    IMAGE_ID=$(echo "${IMAGE_AND_SNAPSHOT_ID}" | cut -f1)
    SNAPSHOT_ID=$(echo "${IMAGE_AND_SNAPSHOT_ID}" | cut -f2)

    echo "  Attempting to deregister [${IMAGE_ID}] and remove [${SNAPSHOT_ID}].."

    aws ec2 deregister-image --image-id "${IMAGE_ID}" && \
        sleep 3 && \
        aws ec2 delete-snapshot --snapshot-id "${SNAPSHOT_ID}"
}

# Export the `prune_ami` function so that it can be used with `xargs`.
export -f prune_ami

# Loop through application and tiler AMIs and prune all but the last
# 10 for each service type, but only if they're targeted at the staging
# environment.
for service in Application Tiler;
do
    echo "Determining [${service}] AMIs that are eligible for pruning.."
    echo ""

    aws ec2 describe-images \
      --owners self \
      --filters Name=tag:Service,Values="${service}" Name=tag:Environment,Values=Staging \
      --query "Images[*].{Name:Name}" \
      | sort -r \
      | tail -n +11 \
      | xargs -I{} bash -c "prune_ami {}"

    echo ""
done
