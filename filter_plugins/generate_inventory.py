# SPDX-License-Identifier: MIT

class FilterModule(object):
    """Custom Ansible filter for generating static inventory"""

    def filters(self):
        return {
            "generate_inventory": self.generate_inventory
        }

    def generate_inventory(self, hosts, variables, role_name, extra_vars=None):
        """
        Generate a content of the static inventory.

        :param list hosts: A list of hosts.
        :param dict variables: A dict of all variables.
        :param str role_name: A name of an Ansible role.
        :param list extra_vars: A list of names of extra variables from
            `variables`.
        :returns: A content of a static inventory (:class:`dict`).

        For each host in hosts, add all variables starting with `{role_name}_`
        or `__{role_name}_` prefix to host. Additionally, add also all
        variables from extra_vars to every host. All other variables are
        ignored.
        """
        extra_vars = extra_vars or []
        # Strip prefix from the role_name:
        role_name = role_name.split(".")[-1]

        # Role variable prefixes according to conventions:
        rv_prefix = "{0}_".format(role_name)
        prv_prefix = "__{0}".format(rv_prefix)

        # Generate a dictionary of host variables:
        host_variables = {}
        for v in variables:
            if v.startswith(rv_prefix) or v.startswith(prv_prefix) \
            or v in extra_vars:
                host_variables[v] = variables[v]

        return { 
            "all": { "hosts": dict([(h, host_variables) for h in hosts]) }
        }
