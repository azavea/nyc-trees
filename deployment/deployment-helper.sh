#!/bin/bash

set -e

if env | grep -q "NYC_TREES_DEPLOY_DEBUG"; then
  set -x
fi

function get_latest_ubuntu_ami() {
  # 1. Get list of daily Ubuntu AMIs
  # 2. Filter AMIs with EBS SSD instance store, amd64 architecture, and in
  #    AWS_DEFAULT_REGION
  # 3. Filter again by HVM AMIs
  # 4. Sort by date in reverse
  # 5. Take the top row
  # 6. Take the 8th column
  curl -s "http://cloud-images.ubuntu.com/query/trusty/server/daily.txt" \
    | egrep "ebs-ssd\s+amd64\s+${AWS_DEFAULT_REGION}" \
    | grep "hvm" \
    | sort -k4 -r \
    | head -n1 \
    | cut -f8
}

function get_stack_outputs() {
  aws cloudformation describe-stacks \
    --stack-name "${1}" \
    --query "Stacks[*].Outputs[*].[OutputKey, OutputValue]"
}

function wait_for_stack() {
  local n=0

  until [ $n -ge 30 ]  # 30 * 60 = 1800 = 30 minutes
  do
    echo "Waiting for stack..."

    aws cloudformation describe-stacks \
      --stack-name "${1}" \
      | cut -f"7,8" \
      | egrep -q "(CREATE|UPDATE|ROLLBACK)_COMPLETE" && break

    n=$[$n+1]
    sleep 60
  done

  aws cloudformation describe-stacks --stack-name "${1}"
}

wait_for_elb_health() {
  local n=0

  until [ $n -ge 20 ]  # 20 * 30 = 600 = 10 minutes
  do
    echo "Waiting for ELB health..."

    aws elb describe-instance-health \
      --load-balancer-name "${1}" \
      | cut -f5 \
      | grep -q "InService" && break

    n=$[$n+1]
    sleep 30
  done

  aws elb describe-instance-health --load-balancer-name "${1}"
}

toggle_app_server_stack() {
  AWS_STACKS=$(aws cloudformation describe-stacks | grep STACKS | cut -f7)
  AWS_APP_STACK_OUTPUTS=$(get_stack_outputs "NYCTrees${1}AppServers")

  AWS_ELB_APP_ENDPOINT=$(echo $AWS_APP_STACK_OUTPUTS | grep "AppServerLoadBalancerEndpoint" | cut -d' ' -f2)
  AWS_ELB_HOSTED_ZONE_ID=$(echo $AWS_APP_STACK_OUTPUTS | grep "AppServerLoadBalancerHostedZoneNameID" | cut -d' ' -f4)

  # Build parameters argument
  AWS_STACK_PARAMS="ParameterKey=PublicHostedZone,ParameterValue=${AWS_PUBLIC_HOSTED_ZONE}"
  AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=AppServerAliasTarget,ParameterValue=${AWS_ELB_APP_ENDPOINT}"
  AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=AppServerLoadBalancerHostedZoneNameID,ParameterValue=${AWS_ELB_HOSTED_ZONE_ID}"

  if echo "${AWS_STACKS}" | grep -q "NYCTreesAppHostedZone"; then
    aws cloudformation update-stack \
      --stack-name "NYCTreesAppHostedZone" \
      --use-previous-template \
      --parameters ${AWS_STACK_PARAMS}
  else
    aws cloudformation create-stack \
      --stack-name "NYCTreesAppHostedZone" \
      --template-body "file://troposphere/app_hosted_zone_template.json" \
      --parameters ${AWS_STACK_PARAMS}
  fi

  wait_for_stack "NYCTreesAppHostedZone"
}

toggle_tile_server_stack() {
  AWS_STACKS=$(aws cloudformation describe-stacks | grep STACKS | cut -f7)
  AWS_TILE_STACK_OUTPUTS=$(get_stack_outputs "NYCTrees${1}TileServers")

  AWS_ELB_TILE_ENDPOINT=$(echo $AWS_TILE_STACK_OUTPUTS | grep "TileServerLoadBalancerEndpoint" | cut -d' ' -f2)

  # Build parameters argument
  AWS_STACK_PARAMS="ParameterKey=PublicHostedZone,ParameterValue=${AWS_PUBLIC_HOSTED_ZONE}"
  AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=TileServerAliasTarget,ParameterValue=${AWS_ELB_TILE_ENDPOINT}"

  if echo "${AWS_STACKS}" | grep -q "NYCTreesTileHostedZone"; then
    aws cloudformation update-stack \
      --stack-name "NYCTreesTileHostedZone" \
      --use-previous-template \
      --parameters ${AWS_STACK_PARAMS}
  else
    aws cloudformation create-stack \
      --stack-name "NYCTreesTileHostedZone" \
      --template-body "file://troposphere/tiler_hosted_zone_template.json" \
      --parameters ${AWS_STACK_PARAMS}
  fi

  wait_for_stack "NYCTreesTileHostedZone"
}

function get_latest_internal_ami() {
  # 1. Get list of AMIs owned by this account
  # 2. Filter by type (only argument to this function)
  # 3. Filter again for the IMAGES row
  # 4. Sort by AMI name (contains a date created timestamp)
  # 5. Take the top row
  # 6. Take the 4th column
  aws ec2 describe-images --owners self \
    | grep "${1}" \
    | grep IMAGES \
    | sort -k5 -r \
    | head -n1 \
    | cut -f4
}

function create_ami() {
  packer build \
    -only="${1}" \
    -var "aws_ubuntu_ami=$(get_latest_ubuntu_ami)" \
    packer/template.js
}

case "$1" in

  create-vpc-stack)
    aws cloudformation create-stack \
      --stack-name "NYCTreesVPC" \
      --template-body "file://troposphere/vpc_template.json" \
      --parameters "ParameterKey=KeyName,ParameterValue=${AWS_KEY_NAME}"

    wait_for_stack "NYCTreesVPC"
    ;;


  create-private-hosted-zones)
    # Get CloudFormation VPC stack outputs
    AWS_VPC_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesVPC")

    # Create private DNS hosted zone
    aws route53 create-hosted-zone \
      --name nyc-trees.internal \
      --caller-reference "create-hosted-zone-$(date +"%Y-%m-%d-%H:%M")" \
      --vpc "VPCRegion=${AWS_DEFAULT_REGION},VPCId=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "VpcId" | cut -f2)" \
      --hosted-zone-config "Comment=create-hosted-zone"
    ;;


  create-data-store-stack)
    # Get CloudFormation VPC stack outputs
    AWS_VPC_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesVPC")

    AWS_VPC_ID=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "VpcId" | cut -f2)
    AWS_BASTION_HOST_AMI=$(get_latest_internal_ami "nyc-trees-monitoring")
    AWS_PUBLIC_SUBNETS=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "PublicSubnets" | cut -f2)
    AWS_PRIVATE_SUBNETS=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "PrivateSubnets" | cut -f2)

    # Build parameters argument
    AWS_STACK_PARAMS="ParameterKey=PublicHostedZone,ParameterValue=${AWS_PUBLIC_HOSTED_ZONE}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=KeyName,ParameterValue=${AWS_KEY_NAME}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=GlobalNotificationsARN,ParameterValue=${AWS_SNS_TOPIC}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=VpcId,ParameterValue=${AWS_VPC_ID}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=BastionHostAMI,ParameterValue=${AWS_BASTION_HOST_AMI}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=PublicSubnets,ParameterValue='${AWS_PUBLIC_SUBNETS}'"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=PrivateSubnets,ParameterValue='${AWS_PRIVATE_SUBNETS}'"

    # Create data store stack
    aws cloudformation create-stack \
      --stack-name "NYCTreesDataStores" \
      --template-body "file://troposphere/data_store_template.json" \
      --parameters ${AWS_STACK_PARAMS}

    wait_for_stack "NYCTreesDataStores"

    AWS_CACHE_CLUSTER_ENDPOINT=$(aws elasticache describe-cache-clusters --show-cache-node-info | grep ENDPOINT | cut -f2)
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=CacheClusterEndpoint,ParameterValue=${AWS_CACHE_CLUSTER_ENDPOINT}"

    echo "Updating data store stack with cache cluster endpoint..."

    # Update data store stack with cache cluster endpoint
    aws cloudformation update-stack \
      --stack-name "NYCTreesDataStores" \
      --use-previous-template \
      --parameters ${AWS_STACK_PARAMS}

    wait_for_stack "NYCTreesDataStores"
    ;;


  create-tiler-stack)
    AWS_VPC_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesVPC")
    AWS_STACKS=$(aws cloudformation describe-stacks | grep STACKS | cut -f7)

    AWS_VPC_ID=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "VpcId" | cut -f2)
    AWS_TILE_SERVER_AMI=$(get_latest_internal_ami "nyc-trees-tiler" )
    AWS_PUBLIC_SUBNETS=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "PublicSubnets" | cut -f2)
    AWS_PRIVATE_SUBNETS=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "PrivateSubnets" | cut -f2)

    # Determine stack color
    if echo "${AWS_STACKS}" | grep -q "NYCTreesBlueTileServers" &&
       echo "${AWS_STACKS}" | grep -q "NYCTreesGreenTileServers"; then
      # Both stack already exists
      echo "Both tiler stacks already exist."
      exit 1
    elif echo "${AWS_STACKS}" | grep -q "NYCTreesBlueTileServers"; then
      # Blue exists, so deploy green
      AWS_TILE_STACK_COLOR="Green"
    elif echo "${AWS_STACKS}" | grep -q "NYCTreesGreenTileServers"; then
      # Green exists, so deploy blue
      AWS_TILE_STACK_COLOR="Blue"
    else
      # No color exists, so deploy green
      AWS_TILE_STACK_COLOR="Green"
    fi

    echo "Launching the [${AWS_TILE_STACK_COLOR}] tiler stack..."

    # Build parameters argument
    AWS_STACK_PARAMS="ParameterKey=KeyName,ParameterValue=${AWS_KEY_NAME}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=StackColor,ParameterValue=${AWS_TILE_STACK_COLOR}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=GlobalNotificationsARN,ParameterValue=${AWS_SNS_TOPIC}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=VpcId,ParameterValue=${AWS_VPC_ID}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=TileServerAMI,ParameterValue=${AWS_TILE_SERVER_AMI}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=PublicSubnets,ParameterValue='${AWS_PUBLIC_SUBNETS}'"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=PrivateSubnets,ParameterValue='${AWS_PRIVATE_SUBNETS}'"

    # Create tile server stack
    aws cloudformation create-stack \
      --stack-name "NYCTrees${AWS_TILE_STACK_COLOR}TileServers" \
      --template-body "file://troposphere/tiler_template.json" \
      --parameters ${AWS_STACK_PARAMS}

    wait_for_stack "NYCTrees${AWS_TILE_STACK_COLOR}TileServers"

    AWS_TILE_LOAD_BALANCER=$(aws cloudformation list-stack-resources \
      --stack-name "NYCTrees${AWS_TILE_STACK_COLOR}TileServers" \
      | grep "elbTileServer" \
      | cut -f4)

    wait_for_elb_health "${AWS_TILE_LOAD_BALANCER}"
    ;;


  create-app-stack)
    AWS_VPC_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesVPC")
    AWS_STACKS=$(aws cloudformation describe-stacks | grep STACKS | cut -f7)

    AWS_VPC_ID=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "VpcId" | cut -f2)
    AWS_APP_SERVER_AMI=$(get_latest_internal_ami "nyc-trees-app" )
    AWS_PUBLIC_SUBNETS=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "PublicSubnets" | cut -f2)
    AWS_PRIVATE_SUBNETS=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "PrivateSubnets" | cut -f2)

    # Determine stack color
    if echo "${AWS_STACKS}" | grep -q "NYCTreesBlueAppServers" &&
       echo "${AWS_STACKS}" | grep -q "NYCTreesGreenAppServers"; then
      # Both stack already exists
      echo "Both application stacks already exist."
      exit 1
    elif echo "${AWS_STACKS}" | grep -q "NYCTreesBlueAppServers"; then
      # Blue exists, so deploy green
      AWS_APP_STACK_COLOR="Green"
    elif echo "${AWS_STACKS}" | grep -q "NYCTreesGreenAppServers"; then
      # Green exists, so deploy blue
      AWS_APP_STACK_COLOR="Blue"
    else
      # No color exists, so deploy green
      AWS_APP_STACK_COLOR="Green"
    fi

    echo "Launching the [${AWS_APP_STACK_COLOR}] application stack..."

    # Build parameters argument
    AWS_STACK_PARAMS="ParameterKey=KeyName,ParameterValue=${AWS_KEY_NAME}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=StackColor,ParameterValue=${AWS_APP_STACK_COLOR}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=GlobalNotificationsARN,ParameterValue=${AWS_SNS_TOPIC}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=AppSSLCertificateARN,ParameterValue=${AWS_SSL_CERTIFICATE}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=VpcId,ParameterValue=${AWS_VPC_ID}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=AppServerAMI,ParameterValue=${AWS_APP_SERVER_AMI}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=PublicSubnets,ParameterValue='${AWS_PUBLIC_SUBNETS}'"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=PrivateSubnets,ParameterValue='${AWS_PRIVATE_SUBNETS}'"

    # Create app server stack
    aws cloudformation create-stack \
      --stack-name "NYCTrees${AWS_APP_STACK_COLOR}AppServers" \
      --template-body "file://troposphere/app_template.json" \
      --parameters ${AWS_STACK_PARAMS}

    wait_for_stack "NYCTrees${AWS_APP_STACK_COLOR}AppServers"

    AWS_APP_LOAD_BALANCER=$(aws cloudformation list-stack-resources \
      --stack-name "NYCTrees${AWS_APP_STACK_COLOR}AppServers" \
      | grep "elbAppServer" \
      | cut -f4)

    wait_for_elb_health "${AWS_APP_LOAD_BALANCER}"
    ;;


  toggle-green-app-stack)
    toggle_app_server_stack "Green"
    ;;


  toggle-blue-app-stack)
    toggle_app_server_stack "Blue"
    ;;


  delete-green-app-stack)
    aws cloudformation delete-stack --stack-name "NYCTreesGreenAppServers"
    ;;


  delete-blue-app-stack)
    aws cloudformation delete-stack --stack-name "NYCTreesBlueAppServers"
    ;;


  toggle-green-tiler-stack)
    toggle_tile_server_stack "Green"
    ;;


  toggle-blue-tiler-stack)
    toggle_tile_server_stack "Blue"
    ;;


  delete-green-tiler-stack)
    aws cloudformation delete-stack --stack-name "NYCTreesGreenTileServers"
    ;;


  delete-blue-tiler-stack)
    aws cloudformation delete-stack --stack-name "NYCTreesBlueTileServers"
    ;;


  create-monitoring-ami)
    create_ami "nyc-trees-monitoring"
    ;;


  create-tiler-ami)
    create_ami "nyc-trees-tiler"
    ;;


  create-app-ami)
    create_ami "nyc-trees-app"
    ;;


  create-app-and-tiler-amis)
    create_ami "nyc-trees-app,nyc-trees-tiler"
    ;;


  *)
    echo "Usage: deployment-helper.sh {command}"
    echo ""
    echo "  Commands:"
    echo ""
    echo "    - create-vpc-stack"
    echo "    - create-private-hosted-zones"
    echo "    - create-data-store-stack"
    echo "    - create-tiler-stack"
    echo "    - create-app-stack"
    echo "    - toggle-green-app-stack"
    echo "    - toggle-blue-app-stack"
    echo "    - delete-green-app-stack"
    echo "    - delete-blue-app-stack"
    echo "    - toggle-green-tiler-stack"
    echo "    - toggle-blue-tiler-stack"
    echo "    - delete-green-tiler-stack"
    echo "    - delete-blue-tiler-stack"
    echo "    - create-monitoring-ami"
    echo "    - create-tiler-ami"
    echo "    - create-app-ami"
    echo "    - create-app-and-tiler-amis"
    exit 1
    ;;

esac

exit 0
