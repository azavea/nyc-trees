#!/bin/bash

set -e
set -x

function get_latest_ubuntu_ami() {
  # 1. Get list of daily Ubuntu AMIs
  # 2. Filter AMIs with EBS instance store, amd64 architecture, and in
  #    AWS_DEFAULT_REGION
  # 3. Filter again by HVM AMIs
  # 4. Sort by date in reverse
  # 5. Take the top row
  # 6. Take the 8th column
  curl -s "http://cloud-images.ubuntu.com/query/trusty/server/daily.txt" \
    | egrep "ebs\s+amd64\s+${AWS_DEFAULT_REGION}" \
    | grep "hvm" \
    | sort -k4 -r \
    | head -n1 \
    | cut -f8
}

function get_stack_outputs() {
  aws cloudformation describe-stacks \
    --stack-name "${1}" \
    --output text --query "Stacks[*].Outputs[*].[OutputKey, OutputValue]"
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
    # Get the most recent daily Ubuntu AMI
    AWS_BASTION_HOST_AMI=$(get_latest_ubuntu_ami)

    # Build parameters argument
    AWS_STACK_PARAMS="ParameterKey=KeyName,ParameterValue=${AWS_KEY_NAME}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=BastionHostAMI,ParameterValue=${AWS_BASTION_HOST_AMI}"

    # Create VPC stack
    aws cloudformation create-stack \
      --stack-name "NYCTreesVPC" \
      --template-body "file://troposphere/vpc_template.json" \
      --parameters ${AWS_STACK_PARAMS}
    ;;


  update-vpc-stack)
    # Get the latest monitoring AMI
    AWS_BASTION_HOST_AMI=$(get_latest_internal_ami "nyc-trees-monitoring")

    # Update VPC stack
    aws cloudformation update-stack \
      --stack-name "NYCTreesVPC" \
      --use-previous-template \
      --parameters "ParameterKey=BastionHostAMI,ParameterValue=${AWS_BASTION_HOST_AMI}"
    ;;


  create-data-store-stack)
    # Get CloudFormation VPC stack outputs
    AWS_VPC_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesVPC")

    AWS_SG_DATABASE_SERVER=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "sgDatabaseServer" | cut -f2)
    AWS_SG_CACHE_CLUSTER=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "sgCacheCluster" | cut -f2)
    AWS_DATA_STORE_SUBNETS=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "DataStoreServerSubnets" | cut -f2)

    # Build parameters argument
    AWS_STACK_PARAMS="ParameterKey=KeyName,ParameterValue=${AWS_KEY_NAME}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=GlobalNotificationsARN,ParameterValue=${AWS_SNS_TOPIC}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=sgDatabaseServer,ParameterValue=${AWS_SG_DATABASE_SERVER}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=sgCacheCluster,ParameterValue=${AWS_SG_CACHE_CLUSTER}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=DataStoreServerSubnets,ParameterValue='${AWS_DATA_STORE_SUBNETS}'"

    # Create data store stack
    aws cloudformation create-stack \
      --stack-name "NYCTreesDataStores" \
      --template-body "file://troposphere/data_store_template.json" \
      --parameters ${AWS_STACK_PARAMS}
    ;;


  create-private-dns-stack)
    # Get CloudFormation VPC stack outputs
    AWS_VPC_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesVPC")
    AWS_DATA_STORE_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesDataStores")

    # Create private DNS hosted zone
    aws route53 create-hosted-zone \
      --name nyc-trees.internal \
      --caller-reference "create-private-dns-stack-$(date +"%Y-%m-%d-%H:%M")" \
      --vpc "VPCRegion=${AWS_DEFAULT_REGION},VPCId=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "VpcId" | cut -f2)" \
      --hosted-zone-config Comment=create-private-dns-stack,PrivateZone=true

    AWS_BASTION_HOST_PRIVATE_IP=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "BastionPrivateIPAddress" | cut -f2)
    AWS_TILE_SERVER_ENDPOINT=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "TileServerLoadBalancerEndpoint" | cut -f2)
    AWS_DATABASE_ENDPOINT=$(echo "${AWS_DATA_STORE_STACK_OUTPUTS}" | grep "DatabaseServerEndpoint" | cut -f2 | cut -d":" -f1)
    AWS_CACHE_CLUSTER_ENDPOINT=$(aws elasticache describe-cache-clusters --show-cache-node-info | grep ENDPOINT | cut -f2)

    # Build parameters argument
    AWS_STACK_PARAMS="ParameterKey=BastionPrivateIPAddress,ParameterValue=${AWS_BASTION_HOST_PRIVATE_IP}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=TileServerLoadBalancerEndpoint,ParameterValue=${AWS_TILE_SERVER_ENDPOINT}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=DatabaseServerEndpoint,ParameterValue=${AWS_DATABASE_ENDPOINT}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=CacheClusterEndpoint,ParameterValue=${AWS_CACHE_CLUSTER_ENDPOINT}"

    # Create private DNS stack
    aws cloudformation create-stack \
      --stack-name "NYCTreesPrivateDNS" \
      --template-body "file://troposphere/private_dns_template.json" \
      --parameters ${AWS_STACK_PARAMS}
    ;;


  update-private-dns-stack)
    # Get CloudFormation VPC stack outputs
    AWS_VPC_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesVPC")

    AWS_BASTION_HOST_PRIVATE_IP=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "BastionPrivateIPAddress" | cut -f2)

    # Build parameters argument
    AWS_STACK_PARAMS="ParameterKey=BastionPrivateIPAddress,ParameterValue=${AWS_BASTION_HOST_PRIVATE_IP}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=TileServerLoadBalancerEndpoint,UsePreviousValue=true"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=DatabaseServerEndpoint,UsePreviousValue=true"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=CacheClusterEndpoint,UsePreviousValue=true"

    # Update VPC stack
    aws cloudformation update-stack \
      --stack-name "NYCTreesPrivateDNS" \
      --use-previous-template \
      --parameters ${AWS_STACK_PARAMS}
    ;;


  create-tiler-stack)
    # Get CloudFormation VPC stack outputs
    AWS_VPC_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesVPC")

    AWS_SG_TILE_SERVER=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "sgTileServer" | cut -f2)
    AWS_TILE_SUBNETS=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "TileServerSubnets" | cut -f2)
    AWS_TILE_SERVER_AMI=$(get_latest_internal_ami "nyc-trees-tiler" )

    # Build parameters argument
    AWS_STACK_PARAMS="ParameterKey=KeyName,ParameterValue=${AWS_KEY_NAME}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=GlobalNotificationsARN,ParameterValue=${AWS_SNS_TOPIC}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=TileServerAMI,ParameterValue=${AWS_TILE_SERVER_AMI}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=sgTileServer,ParameterValue=${AWS_SG_TILE_SERVER}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=TileServerSubnets,ParameterValue='${AWS_TILE_SUBNETS}'"

    # Create tile server stack
    aws cloudformation create-stack \
      --stack-name "NYCTreesTileServers" \
      --template-body "file://troposphere/tiler_template.json" \
      --parameters ${AWS_STACK_PARAMS}
    ;;


  create-app-stack)
    # Get CloudFormation VPC stack outputs
    AWS_VPC_STACK_OUTPUTS=$(get_stack_outputs "NYCTreesVPC")

    AWS_SG_APP_SERVER=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "sgAppServer" | cut -f2)
    AWS_APP_SUBNETS=$(echo "${AWS_VPC_STACK_OUTPUTS}" | grep "AppServerSubnets" | cut -f2)
    AWS_APP_SERVER_AMI=$(get_latest_internal_ami "nyc-trees-app" )

    # Build parameters argument
    AWS_STACK_PARAMS="ParameterKey=KeyName,ParameterValue=${AWS_KEY_NAME}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=GlobalNotificationsARN,ParameterValue=${AWS_SNS_TOPIC}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=AppServerAMI,ParameterValue=${AWS_APP_SERVER_AMI}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=sgAppServer,ParameterValue=${AWS_SG_APP_SERVER}"
    AWS_STACK_PARAMS="${AWS_STACK_PARAMS} ParameterKey=AppServerSubnets,ParameterValue='${AWS_APP_SUBNETS}'"

    # Create tile server stack
    aws cloudformation create-stack \
      --stack-name "NYCTreesAppServers" \
      --template-body "file://troposphere/app_template.json" \
      --parameters ${AWS_STACK_PARAMS}
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
    echo "    - update-vpc-stack"
    echo "    - create-data-store-stack"
    echo "    - create-private-dns-stack"
    echo "    - update-private-dns-stack"
    echo "    - create-tiler-stack"
    echo "    - create-app-stack"
    echo "    - create-monitoring-ami"
    echo "    - create-tiler-ami"
    echo "    - create-app-ami"
    exit 1
    ;;

esac

exit 0
