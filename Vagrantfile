# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 1.5"

# Uses the contents of roles.txt to ensure that ansible-galaxy is run if any
# dependencies are missing.
def install_dependent_roles
  File.foreach("deployment/ansible/roles.txt") do |line|
    role_path = "deployment/ansible/roles/#{line.split(",").first}"

    if !File.directory?(role_path) && !File.symlink?(role_path)
      unless system("ansible-galaxy install -f -r deployment/ansible/roles.txt -p #{File.dirname(role_path)}")
        $stderr.puts "\nERROR: An attempt to install Ansible role dependencies failed."
        exit(1)
      end

      break
    end
  end
end

# Install missing role dependencies based on the contents of roles.txt
if [ "up", "provision" ].include?(ARGV.first)
  install_dependent_roles
end

ANSIBLE_INVENTORY_PATH = "deployment/ansible/inventory"
VAGRANT_PROXYCONF_ENDPOINT = ENV["VAGRANT_PROXYCONF_ENDPOINT"]
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"

  # Wire up the proxy if:
  #
  #   - The vagrant-proxyconf Vagrant plugin is installed
  #   - The user set the VAGRANT_PROXYCONF_ENDPOINT environmental variable
  #
  if Vagrant.has_plugin?("vagrant-proxyconf") &&
     !VAGRANT_PROXYCONF_ENDPOINT.nil?
    config.proxy.http     = VAGRANT_PROXYCONF_ENDPOINT
    config.proxy.https    = VAGRANT_PROXYCONF_ENDPOINT
    config.proxy.no_proxy = "localhost,127.0.0.1"
  end

  config.vm.define "app" do |app|
    app.vm.network "private_network", ip: "33.33.33.10"
    app.vm.network "forwarded_port", guest: 80, host: 8080

    app.vm.provision "ansible" do |ansible|
      ansible.playbook = "deployment/ansible/app-servers.yml"
      ansible.inventory_path = ANSIBLE_INVENTORY_PATH
      ansible.raw_arguments = ["--timeout=60"]
    end
  end

  config.vm.define "tiler" do |tiler|
    tiler.vm.network "private_network", ip: "33.33.33.20"

    tiler.vm.provision "ansible" do |ansible|
      ansible.playbook = "deployment/ansible/tile-servers.yml"
      ansible.inventory_path = ANSIBLE_INVENTORY_PATH
      ansible.raw_arguments = ["--timeout=60"]
    end
  end

  config.vm.define "services" do |db|
    db.vm.network "private_network", ip: "33.33.33.30"
    db.vm.network "forwarded_port", guest: 80, host: 8081
    db.vm.network "forwarded_port", guest: 5432, host: 5432
    db.vm.network "forwarded_port", guest: 6379, host: 6379

    db.vm.provider "virtualbox" do |v|
      v.memory = 1024
    end

    db.vm.provision "ansible" do |ansible|
      ansible.playbook = "deployment/ansible/services.yml"
      ansible.inventory_path = ANSIBLE_INVENTORY_PATH
      ansible.raw_arguments = ["--timeout=60"]
    end
  end
end
