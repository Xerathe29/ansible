# vse_csv_plugin.py

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    name: vse_csv_plugin
    plugin_type: inventory
    short_description: Returns Ansible inventory from CSV
    description: Returns Ansible inventory from CSV
    options:
        plugin:
            description: Name of the plugin
            required: true
            choices: ['vse_csv_plugin']    
        path_to_inventory:
            description: Directory location of the CSV inventory
            required: true
        csv_file:
            description: File name of the CSV inventory file
            required: true
'''

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError, AnsibleParserError
import csv

class InventoryModule (BaseInventoryPlugin):
    NAME = 'vse_csv_plugin'

    def verify_file(self, path):
        ''' Return true/false if this is possibly a valid file for the this plugin to consume '''
        valid = False
        if super(InventoryModule, self).verify_file(path):
            # base class verifies that file exists
            # and is readable by current user
            if path.endswith(('csv_inventory.yaml', 'csv_inventory.yml')):
                valid = True
        return valid
    
    def _get_structured_inventory(self, inventory_file):

        #Init dictionary
        inventory_data = {}
        # Read CSV data into the dictionary
        with open(inventory_file, 'r') as fh:
            csvdict = csv.DictReader(fh)
            for rows in csvdict:
                hostname = rows['Device Name']
                inventory_data[hostname] = rows
        return inventory_data
        
    def _populate(self):
        ''' Return the hosts and groups '''
        self.inventory_file = self.inv_dir + '/' + self.inv_file
        self.myinventory = self._get_structured_inventory(self.inventory_file)        
        #import pdb; pdb.set_trace()
        # Create the file, platform, OS version, and variable groups
        roles = {}
        platforms = {}
        os_vers = {}
        varGroups = {}
        for data in self.myinventory.values():
            if data['Role'] is not "":
                if not data['Role'] in roles:
                    roles.append(data['Role'])
            if data['Platform'] is not "":
                if not data['Platform'] in platforms:
                    platforms.append(data['Platform'])
            if data['OS_Ver'] is not "":
                if not data['OS_Ver'] in os_vers:
                    os_vers.append(data['OS_Ver'])
            if data['variableGroup'] is not "":
                if not data['variableGroup'] in varGroups:
                    varGroups.append(data['variableGroup'])
        for role in roles:
            self.inventory.add_group(role)
        for platform in platforms:
            self.inventory.add_group(platform)
        for os_ver in os_vers:
            self.inventory.add_group(os_ver)
        for varGroup in VarGroups:
            self.inventory.add_group(varGroup)

        for hostname,data in self.myinventory.items():
            # Add the hosts to the groups
            if data['Role'] is not "":
                self.inventory.add_host(host=hostname, group=data['Role'])
            if data['Platform'] is not "":
                self.inventory.add_host(host=hostname, group=data['Platform'])
            if data['OS_Ver'] is not "":
                self.inventory.add_host(host=hostname, group=data['OS_Ver'])
            if data['variableGroup'] is not "":
                self.inventory.add_host(host=hostname, group=data['variableGroup'])
            # Set host variables
            if data['OOB_IP'] is not "":
                self.inventory.set_variable(hostname, 'ansible_host', data['OOB_IP'])
            if data['connection'] is not "":
                self.inventory.set_variable(hostname, 'ansible_connection', data['connection'])
            if data['connection'] == "winrm":
                self.inventory.set_variable(hostname, 'ansible_winrm_server_cert_validation', 'ignore')
                self.inventory.set_variable(hostname, 'ansible_winrm_kerberos_hostname_override', data['Device Name'])
            if data['become'] is not "":
                self.inventory.set_variable(hostname, 'ansible_become_method', data['become'])
            if data['transport'] is not "":
                self.inventory.set_variable(hostname, 'ansible_winrm_transport', data['transport'])
            if data['port'] is not "":
                self.inventory.set_variable(hostname, 'ansible_port', data['port'])


    def parse(self, inventory, loader, path, cache):
        ''' Return dynamic inventory from source '''
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        # Read the inventory YAML file
        self._read_config_data(path)
        try:
            # Store the options from the YAML file
            self.plugin = self.get_option('plugin')
            self.inv_dir = self.get_option('path_to_inventory')
            self.inv_file = self.get_option('csv_file')
        except:
            raise AnsibleParserError('All correct options required: ()'.format(e))

        # Call our internal helper to populate the dynamic inventory
        self._populate()