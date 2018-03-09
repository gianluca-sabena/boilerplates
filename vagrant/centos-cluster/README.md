# Vagrant

Install vagrant <https://www.vagrantup.com>

Run `vagrant up`

## Ansible

Vagrant supports ansible provisioner

Vagrant generate an inventory files in `.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory`

This inventory works from local terminal

`ansible-playbook -i .vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory provisioning/ping.yml`