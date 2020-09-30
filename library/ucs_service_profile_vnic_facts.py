#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ucs_service_profile_vnic_facts

short_description: Queries UCS Manager for vHBA information

description:
  -Queries UCS Manager for vHBA information

extends_documentation_fragment: ucs

options:
    service_profile_name:
        description:
        - Name of the service profile
        type: str

    delegate_to:
        description:
        - Where the module will be run
        default: localhost
        type: str

requirements:
    - ucsmsdk

author:
    - John McDonough (@movinalot)
    - CiscoUcs (@CiscoUcs)
version_added: "2.10"
'''

EXAMPLES = r'''
- name: Obtain vNIC information for service profile {{ service_profile }}
  ucs_service_profile_vnic_facts:
    hostname: "{{ ucs_hostname }}"
    username: "{{ ucs_username }}"
    password: "{{ ucs_password }}"
    service_profile_name: "{{ service_profile }}"
  register: result

'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec


def retrieve_class_id(class_id, ucs):
    return ucs.login_handle.query_classid(class_id)


def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(
        service_profile_name=dict(type='str', required=True),
        delegate_to=dict(type='str', default='localhost')
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=False,
        mutually_exclusive=[],
    )

    # UCSModule verifies ucsmsdk is present and exits on failure.
    # Imports are below for UCS object creation.
    from ucsmsdk.mometa.ls.LsServer import LsServer

    ucs = UCSModule(module)
    err = False
    query_result = []

    try:
        all_service_profiles = ucs.login_handle.query_classid(class_id="lsServer")

        for profile in all_service_profiles:
            if module.params['service_profile_name']:
                if profile.name != module.params['service_profile_name']:
                    continue

            if profile.type != 'instance':
                continue

            vnics = ucs.login_handle.query_children(in_mo=profile, class_id='vnicEther')

            # Handy sorting function
            def sort_func(x):
                return(x.name)

            # Sort vHBA list by name
            vnics.sort(key=sort_func)
    
            for vnic in vnics:
                        vnic_obj = {
                            "profile": profile.name,
                            "name": vnic.name,
                            "addr": vnic.addr,
                            "switch_id": vnic.switch_id,
                            "mtu": vnic.mtu
                        }
                        query_result.append(vnic_obj)

        ucs.result['vnic_facts'] = query_result

    except Exception as e:
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)

    if err:
        module.fail_json(**ucs.result)

    ucs.result['changed'] = False
    module.exit_json(**ucs.result)


if __name__ == '__main__':
    main()
