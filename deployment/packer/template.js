{
  "variables": {
    "version": "{{env `GIT_COMMIT`}}",
    "aws_region": "us-east-1",
    "aws_instance_type": "m3.large",
    "aws_ssh_username": "ubuntu",
    "aws_ubuntu_ami": ""
  },
  "builders": [
    {
      "name": "nyc-trees-monitoring",
      "type": "amazon-ebs",
      "region": "{{user `aws_region`}}",
      "source_ami": "{{user `aws_ubuntu_ami`}}",
      "instance_type": "{{user `aws_instance_type`}}",
      "ssh_username": "{{user `aws_ssh_username`}}",
      "ami_name": "nyc-trees-monitoring-{{timestamp}}-{{user `version`}}",
      "run_tags": {
        "PackerBuilder": "amazon-ebs"
      },
      "tags": {
        "Name": "nyc-trees-monitoring",
        "Version": "{{user `version`}}"
      }
    },
    {
      "name": "nyc-trees-tiler",
      "type": "amazon-ebs",
      "region": "{{user `aws_region`}}",
      "source_ami": "{{user `aws_ubuntu_ami`}}",
      "instance_type": "{{user `aws_instance_type`}}",
      "ssh_username": "{{user `aws_ssh_username`}}",
      "ami_name": "nyc-trees-tiler-{{timestamp}}-{{user `version`}}",
      "run_tags": {
        "PackerBuilder": "amazon-ebs"
      },
      "tags": {
        "Name": "nyc-trees-tiler",
        "Version": "{{user `version`}}"
      }
    },
    {
      "name": "nyc-trees-app",
      "type": "amazon-ebs",
      "region": "{{user `aws_region`}}",
      "source_ami": "{{user `aws_ubuntu_ami`}}",
      "instance_type": "{{user `aws_instance_type`}}",
      "ssh_username": "{{user `aws_ssh_username`}}",
      "ami_name": "nyc-trees-app-{{timestamp}}-{{user `version`}}",
      "run_tags": {
        "PackerBuilder": "amazon-ebs"
      },
      "tags": {
        "Name": "nyc-trees-app",
        "Version": "{{user `version`}}"
      }
    }
  ],
  "provisioners": [
    {
      "type": "shell",
      "inline": [
        "sleep 5",
        "sudo apt-get update -qq",
        "sudo apt-get install python-pip python-dev -y",
        "sudo pip install ansible==1.8.2"
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
      "extra_arguments": [
        "--extra-vars 'tiler_deploy_branch={{user `version`}}'"
      ],
      "only": [
        "nyc-trees-tiler"
      ]
    },
    {
      "type": "ansible-local",
      "playbook_file": "ansible/app-servers.yml",
      "playbook_dir": "ansible",
      "inventory_file": "ansible/inventory/packer-app-server",
      "extra_arguments": [
        "--extra-vars 'app_deploy_branch={{user `version`}}'"
      ],
      "only": [
        "nyc-trees-app"
      ]
    }
  ]
}
