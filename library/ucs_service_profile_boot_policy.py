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
module: ucs_service_profile_boot_policy

short_description: Sets boot policy for a service profile or template

description:
  -Sets the boot policy for a service profile or service profile template

extends_documentation_fragment: ucs

options:
    service_profile_name:
        description:
        - Name of the service profile or template
        type: str
        required: true

    boot_policy_name:
        description:
        - Name of the boot policy to associate with service profile or template
        type: str
        required: true

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
    - Craig Briese (craig.briese@uscellular.com)
version_added: "2.10"
'''

EXAMPLES = r'''
- name: Set boot policy of service profile {{ service_profile }} to {{ boot_policy }}
  ucs_service_profile_vhba_facts:
    hostname: "{{ ucs_hostname }}"
    username: "{{ ucs_username }}"
    password: "{{ ucs_password }}"
    service_profile_name: "{{ service_profile }}"
    boot_policy_name: "{{ boot_policy }}"
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
        boot_policy_name=dict(type='str', required=True),
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

    ucs.result['changed'] = False

    try:
        filter_string = '(name, "{:s}", type="eq")'.format(module.params['service_profile_name'])

        service_profiles = ucs.login_handle.query_classid(class_id="lsServer", filter_str=filter_string)

        if len(service_profiles) == 0:
            raise Exception('Service profile {:s} does not exist'.format(
                    module.params['service_profile_name']
                )
            )
        elif len(service_profiles) > 1:
            raise Exception('Service profile name {:s} is not unique'.format(
                    module.params['service_profile_name']
                )
            )

        service_profile = service_profiles[0]

        filter_string = '(name, "{:s}", type="eq")'.format(module.params['boot_policy_name'])

        boot_policies = ucs.login_handle.query_classid(class_id="lsbootPolicy", filter_str=filter_string)

        if len(boot_policies) == 0:
            raise Exception('Boot policy {:s} does not exist'.format(
                    module.params['boot_policy_name']
                )
            )
        elif len(boot_policies) > 1:
            raise Exception('Boot policy name {:s} is not unique'.format(
                    module.params['boot_policy_name']
                )
            )

        boot_policy = boot_policies[0]

        if service_profile.boot_policy_name == boot_policy.name:
            ucs.result['changed'] = False
            module.exit_json(**ucs.result)

        service_profile.boot_policy_name = boot_policy.name

        ucs.login_handle.set_mo(service_profile)

        ucs.login_handle.commit()
        ucs.result['changed'] = True

    except Exception as e:
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)

    if err:
        module.fail_json(**ucs.result)

    module.exit_json(**ucs.result)


if __name__ == '__main__':
    main()
