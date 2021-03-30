# SPDX-License-Identifier: MIT

CONNECTION_VARS = (
    # Connection (general):
    "ansible_connection",
    "ansible_host",
    "ansible_port",
    "ansible_user",
    "ansible_password",
    # Connection (SSH):
    "ansible_ssh_private_key_file",
    "ansible_ssh_common_args",
    "ansible_sftp_extra_args",
    "ansible_scp_extra_args",
    "ansible_ssh_extra_args",
    "ansible_ssh_pipelining",
    "ansible_ssh_executable",
    # Privilege escalation:
    "ansible_become",
    "ansible_become_method",
    "ansible_become_user",
    "ansible_become_password",
    "ansible_become_exe",
    "ansible_become_flags",
    # Remote host environment parameters:
    "ansible_shell_type",
    "ansible_python_interpreter",
    "ansible_shell_executable",
)


class FilterModule(object):
    """Custom Ansible filter for generating static inventory."""

    def filters(self):
        return {"generate_inventory": self.generate_inventory}

    def generate_inventory(self, hostvars, variables, role_name, extra_vars=None):
        """
        Generate the content of the static inventory.

        :param dict hostvars: A dict of hosts variables.
        :param dict variables: A dict of all variables.
        :param str role_name: A name of an Ansible role.
        :param list extra_vars: A list of names of extra variables from
            `variables`.
        :returns: A content of the static inventory (:class:`dict`).

        For each host in `hostvars`, add all variables starting with
        `{role_name}_` or `__{role_name}_` prefix to host. Additionally,
        add also all variables from `extra_vars` to every host. All other
        variables are ignored.
        """
        extra_vars = extra_vars or []
        # Strip prefix from the role_name:
        role_name = role_name.split(".")[-1]

        # Role variable prefixes according to conventions:
        rv_prefix = "{0}_".format(role_name)
        prv_prefix = "__{0}".format(rv_prefix)

        # Gather user defined "host" variables:
        user_vars = {}
        for v in variables:
            if v.startswith(rv_prefix) or v.startswith(prv_prefix) or v in extra_vars:
                user_vars[v] = variables[v]

        # Prepare host variables:
        host_vars = {}
        for host in hostvars:
            host_vars[host] = {}
            # Copy connection variables:
            for connvar in CONNECTION_VARS:
                if connvar in hostvars[host]:
                    host_vars[host][connvar] = hostvars[host][connvar]
            # Merge user_vars in:
            host_vars[host].update(user_vars)

        return {"all": {"hosts": host_vars}}
