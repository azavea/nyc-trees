# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.require_version ">= 1.5"

# Wipe azavea.* roles and download them using ansible-galaxy
def install_dependent_roles
  ansible_path = File.join("deployment", "ansible")

  FileUtils.rm_rf(Dir.glob(File.join("deployment", "ansible", "roles", "azavea.*")))

  unless system("ansible-galaxy install -f -r #{File.join(ansible_path, "roles.txt")} -p #{File.join(ansible_path, "roles")}")
    $stderr.puts "\nERROR: An attempt to install Ansible role dependencies failed."
    exit(1)
  end
end

# Install missing role dependencies based on the contents of roles.txt
if [ "up", "provision" ].include?(ARGV.first)
  install_dependent_roles
end

ANSIBLE_INVENTORY_PATH = if !ENV["VAGRANT_ENV"].nil? && ENV["VAGRANT_ENV"] == "TEST"
  "deployment/ansible/inventory/test"
else
  "deployment/ansible/inventory/development"
end

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

  config.vm.define "services" do |services|
    services.vm.hostname = "services"
    services.vm.network "private_network", ip: "33.33.33.30"

    services.vm.synced_folder ".", "/vagrant", disabled: true

    # Kibana
    services.vm.network "forwarded_port", guest: 80, host: 8081
    # Graphite Web
    services.vm.network "forwarded_port", guest: 8080, host: 8082
    # PortgreSQL
    services.vm.network "forwarded_port", guest: 5432, host: 15432
    # Redis
    services.vm.network "forwarded_port", guest: 6379, host: 16379

    services.vm.provider "virtualbox" do |v|
      v.memory = 1024
    end

    services.vm.provision "ansible" do |ansible|
      ansible.playbook = "deployment/ansible/services.yml"
      ansible.inventory_path = ANSIBLE_INVENTORY_PATH
      ansible.raw_arguments = ["--timeout=60"]
    end
  end

  config.vm.define "tiler" do |tiler|
    tiler.vm.hostname = "tiler"
    tiler.vm.network "private_network", ip: "33.33.33.20"

    tiler.vm.synced_folder ".", "/vagrant", disabled: true

    tiler.vm.provision "ansible" do |ansible|
      ansible.playbook = "deployment/ansible/tile-servers.yml"
      ansible.inventory_path = ANSIBLE_INVENTORY_PATH
      ansible.raw_arguments = ["--timeout=60"]
    end
  end

  config.vm.define "app" do |app|
    app.vm.hostname = "app"
    app.vm.network "private_network", ip: "33.33.33.10"

    app.vm.synced_folder ".", "/vagrant", disabled: true
    app.vm.synced_folder "src/nyc_trees", "/opt/app/"

    # Django runserver
    app.vm.network "forwarded_port", guest: 8000, host: 8000

    app.vm.provision "ansible" do |ansible|
      ansible.playbook = "deployment/ansible/app-servers.yml"
      ansible.inventory_path = ANSIBLE_INVENTORY_PATH
      ansible.raw_arguments = ["--timeout=60"]
    end
  end
end
