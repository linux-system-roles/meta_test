# SPDX-License-Identifier: MIT

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


class ActionModule(ActionBase):
    """
    Run Ansible role in a fresh instance of Ansible.

    How to use in playbook::

        run_ansible_role:
          name: "a role name (required)"
          inventory: "a path to the static inventory file (required)"
          # When true, the role is run in check mode. When false, idempotence
          # is tested. This parameter is optional (default: false).
          check: true
          # Verbosity level. This parameter is optional (default: 2).
          verbosity: 3
    """

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

        result = run_role(inventory_file, role_name, check, verbosity)
        if result is None:
            return dict(failed=True, msg="Fatal error.")

        stats = {}
        for stats_name in STATS_NAMES:
            state = getattr(result, stats_name, None)
            if state is not None:
                stats[stats_name] = sum([count for _, count in state.items()])

        check_msg = "Check mode" if check else "Idempotence"
        if (not check and stats.get("changed")) or stats.get("failures"):
            failed = True
            msg = "%s check of role '%s' failed." % (check_msg, role_name)
        else:
            failed = False
            msg = "%s check of role '%s' OK." % (check_msg, role_name)

        return dict(failed=failed, msg=msg, second_run_stats=stats)
