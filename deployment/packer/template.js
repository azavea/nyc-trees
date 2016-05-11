{
  "variables": {
    "version": "{{env `GIT_COMMIT`}}",
    "branch": "{{env `GIT_BRANCH`}}",
    "postgresql_password": "{{env `NYC_TREES_DB_PASSWORD`}}",
    "aws_region": "us-east-1",
    "aws_instance_type": "t2.large",
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
        "Version": "{{user `version`}}",
        "Branch": "{{user `branch`}}",
        "Created": "{{ isotime }}",
        "Service": "Monitoring",
        "Environment": "Staging"
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
        "Version": "{{user `version`}}",
        "Branch": "{{user `branch`}}",
        "Created": "{{ isotime }}",
        "Service": "Tiler",
        "Environment": "Staging"
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
        "Version": "{{user `version`}}",
        "Branch": "{{user `branch`}}",
        "Created": "{{ isotime }}",
        "Service": "Application",
        "Environment": "Staging"
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
        "sudo pip install paramiko==1.16.0",
        "sudo pip install ansible==2.0.1.0"
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
        "--extra-vars 'tiler_deploy_branch={{user `version`}} postgresql_password={{user `postgresql_password`}}'"
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
        "--extra-vars 'app_deploy_branch={{user `version`}} postgresql_password={{user `postgresql_password`}}'"
      ],
      "only": [
        "nyc-trees-app"
      ]
    }
  ]
}
