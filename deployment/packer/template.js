{
  "variables": {
    "version": "{{env `GIT_COMMIT`}}",
    "aws_region": "us-east-1",
    "aws_instance_type": "m3.medium",
    "aws_ssh_username": "ubuntu",
    "aws_access_key": "{{env `AWS_ACCESS_KEY_ID`}}",
    "aws_secret_key": "{{env `AWS_SECRET_ACCESS_KEY`}}",
    "aws_ubuntu_ami": "",
    "aws_vpc_id": "",
    "aws_bastion_subnet": ""
  },
  "builders": [
    {
      "name": "nyc-trees-monitoring",
      "type": "amazon-ebs",
      "access_key": "{{user `aws_access_key`}}",
      "secret_key": "{{user `aws_secret_key` }}",
      "region": "{{user `aws_region`}}",
      "source_ami": "{{user `aws_ubuntu_ami`}}",
      "instance_type": "{{user `aws_instance_type`}}",
      "ssh_username": "{{user `aws_ssh_username`}}",
      "ami_name": "nyc-trees-monitoring-{{timestamp}}-{{user `version`}}",
      "tags": {
        "name": "nyc-trees-monitoring",
        "version": "{{user `version`}}"
      },
      "vpc_id": "{{user `aws_vpc_id`}}",
      "subnet_id": "{{user `aws_bastion_subnet`}}",
      "associate_public_ip_address": true
    },
    {
      "name": "nyc-trees-tiler",
      "type": "amazon-ebs",
      "access_key": "{{user `aws_access_key`}}",
      "secret_key": "{{user `aws_secret_key` }}",
      "region": "{{user `aws_region`}}",
      "source_ami": "{{user `aws_ubuntu_ami`}}",
      "instance_type": "{{user `aws_instance_type`}}",
      "ssh_username": "{{user `aws_ssh_username`}}",
      "ami_name": "nyc-trees-tiler-{{timestamp}}-{{user `version`}}",
      "tags": {
        "name": "nyc-trees-tiler",
        "version": "{{user `version`}}"
      },
      "vpc_id": "{{user `aws_vpc_id`}}",
      "subnet_id": "{{user `aws_bastion_subnet`}}",
      "associate_public_ip_address": true
    },
    {
      "name": "nyc-trees-app",
      "type": "amazon-ebs",
      "access_key": "{{user `aws_access_key`}}",
      "secret_key": "{{user `aws_secret_key` }}",
      "region": "{{user `aws_region`}}",
      "source_ami": "{{user `aws_ubuntu_ami`}}",
      "instance_type": "{{user `aws_instance_type`}}",
      "ssh_username": "{{user `aws_ssh_username`}}",
      "ami_name": "nyc-trees-app-{{timestamp}}-{{user `version`}}",
      "tags": {
        "name": "nyc-trees-app",
        "version": "{{user `version`}}"
      },
      "vpc_id": "{{user `aws_vpc_id`}}",
      "subnet_id": "{{user `aws_bastion_subnet`}}",
      "associate_public_ip_address": true
    }
  ],
  "provisioners": [
    {
      "type": "shell",
      "inline": [
        "sleep 5",
        "sudo apt-get update -qq",
        "sudo apt-get install python-pip python-dev -y",
        "sudo pip install ansible==1.7.2"
      ]
    },
    {
      "type": "ansible-local",
      "playbook_file": "ansible/monitoring-servers.yml",
      "playbook_dir": "ansible",
      "inventory_file": "ansible/inventory/packer-monitoring-server",
      "only": [
        "nyc-trees-monitoring"
      ]
    },
    {
      "type": "ansible-local",
      "playbook_file": "ansible/tile-servers.yml",
      "playbook_dir": "ansible",
      "inventory_file": "ansible/inventory/packer-tile-server",
      "only": [
        "nyc-trees-tiler"
      ]
    },
    {
      "type": "ansible-local",
      "playbook_file": "ansible/app-servers.yml",
      "playbook_dir": "ansible",
      "inventory_file": "ansible/inventory/packer-app-server",
      "only": [
        "nyc-trees-app"
      ]
    }
  ]
}
