# Meta Test

*Meta Test* is an Ansible role that helps with Linux system roles testing. To
meet different requirements in different roles (now and in the future), it is
designed as a library of scenarios. A scenario is a list of tasks that are
executed with a given parameters. A scenario selection, together with its
parameters definition, is done via `meta_test_scenario` role variable. More
about this variable and about supported scenarios is described in the following
section.

## Role Variables

There is just one variable so far, `meta_test_scenario`, which is a dictionary
containing a scenario name and additional scenario parameters. A scenario name
is stored under the key `name` of the dictionary and it is mandatory. At this
moment, there are supported these scenarios:

* `wrap_role`

The default value of `meta_test_scenario` variable is `null`, which means that
no actions are taken.

### `wrap_role`

#### Parameters

```yaml
# A name of a role (required)
role_name: "some_role"
# A list of names of extra variables to be stored
# in static inventory (optional)
extra_vars: []
# Perform check mode tests (optional)
test_checkmode: no
# Perform idempotency tests (optional)
test_idempotency: no
```

#### Description

Execute a role given by `role_name` in the context of current playbook. If
`test_checkmode` is set, execute it again in a fresh Ansible instance with
check mode enabled. If `test_idempotency` is set, execute it again in a fresh
Ansible instance and check if there are some changes.

Because of launching of fresh Ansible instance, all role specific variables are
stored to the static inventory passed to that instance. As a role specific
variable is considered a variable starting with `{role_name}_` or
`__{role_name}_` (if a `role_name` contains a dot, its part up to the last dot
is stripped, including the last dot). To include also variables that are not
specific to role, list their names in `extra_vars`.

Having `test_checkmode` and `test_idempotency` both set to `true` may give an
unexpected results and thus such a combination is forbidden.

## Examples

Below are several use cases of this role.

### Check mode and idempotency testing

Consider a playbook `tests_foo.yml` given below:

```yaml
- name: Test foo
  hosts: all
  vars:
    meta_test_scenario:
      name: wrap_role
      role_name: foo
      extra_vars:
        - test_data1
        - test_data2
      test_checkmode: "{{ test_checkmode | d(False) }}"
      test_idempotency: "{{ test_idempotency | d(False) }}"
    foo_var: 123
    test_data1: A quick brown fox jumps over the lazy dog.
    test_data2:
      - milk
      - eggs
      - potatoes

  tasks:
    - name: Setup test
      ...

    - name: Import meta_test role
      import_role:
        name: linux-system-roles.meta_test

    - name: Verify results
      ...

    - name: Cleanup
      ...
```

This playbook first setups test environment, runs tasks from `foo` role,
verifies the result and as the last step performs some cleaning. Since
`test_checkmode` and `test_idempotency` are both set to `False`, no check mode
and idempotency testing is performed.

Now consider a playbook `tests_foo_checkmode.yml`:

```yaml
- import_playbook: tests_foo.yml
  vars:
    test_checkmode: yes
```

This playbook do the same as the previous one, but with check mode testing
enabled. In a next playbook, `tests_foo_idempotency.yml`, idempotency testing
is enabled:

```yaml
- import_playbook: tests_foo.yml
  vars:
    test_idempotency: yes
```

Recall that either check mode or idempotency testing can be enabled, but not
both.

## License

* MIT

## Authors

* Jiří Kučera <jkucera AT redhat.com>
