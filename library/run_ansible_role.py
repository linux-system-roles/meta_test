#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, Red Hat, Inc.
# MIT (see LICENSE)
# SPDX-License-Identifier: MIT

# This module is a documentation stub and its purpose it also to satisfy
# ansible-lint. All the work is done via eponymous action plugin.

DOCUMENTATION = r"""
---
module: run_ansible_role

short_description: Run Ansible role within wrapper play (meta_test helper)

description: |
  Given a role name and the static inventory, create a play

    - name: Ansible Play
      hosts: all
      gather_facts: yes
      roles:
        - "{{ name }}"

  and run it in a fresh fork of Ansible. If I(check) is true, the check mode is
  enabled. Otherwise, if I(check) is false, the module checks for changes
  occurrence (i.e. the module checks if the role is idempotent).

version_added: "2.8"

author:
  - Jiří Kučera (@i386x)
  - Sergio Oliveira (@seocam)

options:
  name:
    description: The role name.
    required: true
    type: str
  inventory:
    description: The path to the static inventory.
    required: true
    type: str
  check:
    description: Run the role within wrapper play in check mode.
    required: false
    type: bool
    default: false
  verbosity:
    description: The verbosity level of Ansible fork.
    required: false
    type: int
    default: 2
"""

EXAMPLES = r"""
# Run dummy role in check mode with verbosity level 3
- name: Run dummy in check mode
  run_ansible_role:
    name: dummy
    inventory: hostvars.yaml
    check: true
    verbosity: 3

# Test dummy idempotence
- name: Test dummy idempotence
  run_ansible_role:
    name: dummy
    inventory: hostvars.yaml
"""

RETURN = r"""
msg:
  description: The module status message.
  type: str
  returned: always
  sample: "Idempotence check of role 'dummy' OK."
play_recap:
  description: The play run's statistics.
  type: dict
  returned: always
  contains:
    ok:
      description: The number of ok task runs.
      type: int
      returned: always
    failures:
      description: The number of failed task runs.
      type: int
      returned: always
    unreachable:
      description: The number of unreachable hosts.
      type: int
      returned: always
    changed:
      description: The number of task runs than changed host's state.
      type: int
      returned: always
    skipped:
      description: The number of skipped task runs.
      type: int
      returned: always
    rescued:
      description: The number of rescued task runs.
      type: int
      returned: always
    ignored:
      description: The number of ignored task runs.
      type: int
      returned: always
"""
