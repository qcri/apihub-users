# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|

  config.vm.box = "bento/ubuntu-20.04"

  config.vagrant.plugins = ["vagrant-vbguest"]

  config.vm.network "forwarded_port", guest: 8000, host: 8000

  config.vm.network "private_network", ip: "192.168.33.10"

  config.vm.synced_folder ".", "/home/vagrant/api-hub-users"


  config.vm.provider "virtualbox" do |vb|

    vb.memory = "5120"
  end

  config.vm.provision "shell", path: "./scripts/provisioning/install-system-requirements.sh"
  config.vm.provision "shell",  privileged: false,path: "./scripts/provisioning/install-python.sh"
  config.vm.provision "shell", path: "./scripts/provisioning/postgres-config.sh"

end
