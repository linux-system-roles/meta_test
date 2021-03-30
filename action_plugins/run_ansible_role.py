#!/usr/bin/python
# SPDX-License-Identifier: MIT

from __future__ import absolute_import

__metaclass__ = type

from ansible import context
from ansible.errors import AnsibleActionFail
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.parsing.dataloader import DataLoader
from ansible.playbook.play import Play
from ansible.plugins.action import ActionBase
from ansible.vars.manager import VariableManager

STATS_NAMES = (
    "ok",
    "failures",
    "unreachable",
    "changed",
    "skipped",
    "rescued",
    "ignored",
)


def run_role(inventory_file, role_name, check=False, verbosity=2):
    loader = DataLoader()

    context.CLIARGS = ImmutableDict(
        connection="ssh",
        module_path=["~/.ansible/plugins/modules:/usr/share/ansible/plugins/modules"],
        forks=1,
        check=check,
        diff=False,
        verbosity=verbosity,
    )

    inventory = InventoryManager(loader=loader, sources=inventory_file)

    variable_manager = VariableManager(loader=loader, inventory=inventory)

    play_source = dict(
        name="Ansible Play",
        hosts="all",
        gather_facts="yes",
        roles=[dict(name=role_name)],
    )

    play = Play().load(
        play_source,
        variable_manager=variable_manager,
        loader=loader,
    )

    tqm = None
    try:
        tqm = TaskQueueManager(
            inventory=inventory,
            variable_manager=variable_manager,
            loader=loader,
            passwords=None,
        )
        result = tqm.run(play)
    finally:
        # we always need to cleanup child procs and the structures
        #   we use to communicate with them
        if tqm is not None:
            tqm.cleanup()

    if result != 0:
        return None

    return tqm._stats


def update_result(result, failed, msg, *args):
    result["failed"] = failed
    result["msg"] = msg % args


def failed(result, msg, *args):
    update_result(result, True, msg, *args)
    return result


def succeed(result, msg, *args):
    update_result(result, False, msg, *args)
    return result


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        module_args = self._task.args.copy()
        role_name = module_args.get("name")
        inventory_file = module_args.get("inventory")
        check = module_args.get("check", False)
        verbosity = module_args.get("verbosity", 2)

        if role_name is None:
            raise AnsibleActionFail("missing required parameter: name")
        if inventory_file is None:
            raise AnsibleActionFail("missing required parameter: inventory")

        msg_template = "%s check of role '%s' %%s." % (
            "Check mode" if check else "Idempotence",
            role_name,
        )
        play_recap = {}
        result = dict(failed=False, msg="", play_recap=play_recap)

        stats = run_role(inventory_file, role_name, check, verbosity)
        if stats is None:
            return failed(result, "Fatal error.")

        for stats_name in STATS_NAMES:
            state = getattr(stats, stats_name, None)
            if state is not None:
                play_recap[stats_name] = sum([count for _, count in state.items()])

        if (not check and play_recap.get("changed")) or play_recap.get("failures"):
            return failed(result, msg_template, "failed")

        return succeed(result, msg_template, "OK")
