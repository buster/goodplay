# -*- coding: utf-8 -*-

import ansible  # noqa: F401

import pytest


pytest_plugins = 'pytester'

skip_if_ansible_v1 = pytest.mark.skipif('ansible.__version__.startswith("1.")')


def create_playbook_and_collect_items(testdir, playbook):
    testdir.makefile('', inventory='all')
    testdir.makefile('.yml', test_playbook=playbook)

    items, result = testdir.inline_genitems()

    return items, result


def test_nothing_collected_when_inventory_missing(testdir):
    testdir.makefile('.yml', test_playbook='''---
- hosts: all
  tasks:
    - name: task1
      ping:
      tags: test
''')

    items, result = testdir.inline_genitems()
    assert result.countoutcomes() == [0, 0, 0]
    assert len(items) == 0


def test_fail_on_non_unique_task_names_both_tagged_test(testdir):
    items, result = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - name: task1
      ping:
      tags: test

    - name: task1
      ping:
      tags: test
''')
    assert result.countoutcomes() == [0, 0, 1]
    assert "ValueError: <AnsiblePlaybook 'test_playbook.yml'> contains tests with non-unique name 'task1'" in \
        str(result.getfailures()[0].longrepr)
    assert len(items) == 0


def test_pass_on_non_unique_task_names_single_one_tagged_test(testdir):
    items, result = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - name: task1
      ping:

    - name: task1
      ping:
      tags: test
''')
    assert result.countoutcomes() == [0, 0, 0]
    assert len(items) == 1
    assert items[0].name == 'task1'


def test_single_play_no_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - name: task1
      ping:
''')
    assert len(items) == 0


def test_single_play_single_test(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - name: task1
      ping:
      tags: test
''')
    assert len(items) == 1
    assert items[0].name == 'task1'


def test_single_play_multiple_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - name: task1
      ping:
      tags: test

    - name: task2
      ping:
      tags: test
''')
    assert len(items) == 2
    assert items[0].name == 'task1'
    assert items[1].name == 'task2'


def test_multiple_plays_no_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - name: task1
      ping:

- hosts: all
  tasks:
    - name: task2
      ping:
''')
    assert len(items) == 0


def test_multiple_plays_single_test(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - name: task1
      ping:

- hosts: all
  tasks:
    - name: task2
      ping:
      tags: test
''')
    assert len(items) == 1
    assert items[0].name == 'task2'


def test_multiple_plays_multiple_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - name: task1
      ping:
      tags: test

    - name: task2
      ping:

- hosts: all
  tasks:
    - name: task3
      ping:

    - name: task4
      ping:
      tags: test

    - name: task5
      ping:
      tags: test
''')
    assert len(items) == 3
    assert items[0].name == 'task1'
    assert items[1].name == 'task4'
    assert items[2].name == 'task5'


# ansible block support

@skip_if_ansible_v1
def test_single_play_single_block_no_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:
''')
    assert len(items) == 0


@skip_if_ansible_v1
def test_single_play_single_block_single_test(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:
          tags: test
''')
    assert len(items) == 1
    assert items[0].name == 'task1'


@skip_if_ansible_v1
def test_single_play_single_block_multiple_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:
          tags: test

        - name: task2
          ping:
          tags: test
''')
    assert len(items) == 2
    assert items[0].name == 'task1'
    assert items[1].name == 'task2'


@skip_if_ansible_v1
def test_single_play_multiple_blocks_no_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:

    - block:
        - name: task2
          ping:
''')
    assert len(items) == 0


@skip_if_ansible_v1
def test_single_play_multiple_blocks_single_test(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:

    - block:
        - name: task2
          ping:
          tags: test
''')
    assert len(items) == 1
    assert items[0].name == 'task2'


@skip_if_ansible_v1
def test_single_play_multiple_blocks_multiple_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:
          tags: test

        - name: task2
          ping:

    - block:
        - name: task3
          ping:
          tags: test

        - name: task4
          ping:
          tags: test
''')
    assert len(items) == 3
    assert items[0].name == 'task1'
    assert items[1].name == 'task3'
    assert items[2].name == 'task4'


@skip_if_ansible_v1
def test_multiple_plays_single_block_no_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:

- hosts: all
  tasks:
    - block:
        - name: task2
          ping:
''')
    assert len(items) == 0


@skip_if_ansible_v1
def test_multiple_plays_single_block_single_test(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:

- hosts: all
  tasks:
    - block:
        - name: task2
          ping:
          tags: test
''')
    assert len(items) == 1
    assert items[0].name == 'task2'


@skip_if_ansible_v1
def test_multiple_plays_single_block_multiple_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:

        - name: task2
          ping:
          tags: test

- hosts: all
  tasks:
    - block:
        - name: task3
          ping:

        - name: task4
          ping:
          tags: test
''')
    assert len(items) == 2
    assert items[0].name == 'task2'
    assert items[1].name == 'task4'


@skip_if_ansible_v1
def test_multiple_plays_multiple_blocks_no_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:

    - block:
        - name: task2
          ping:

- hosts: all
  tasks:
    - block:
        - name: task3
          ping:

    - block:
        - name: task4
          ping:
''')
    assert len(items) == 0


@skip_if_ansible_v1
def test_multiple_plays_multiple_blocks_single_test(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:

    - block:
        - name: task2
          ping:

- hosts: all
  tasks:
    - block:
        - name: task3
          ping:

    - block:
        - name: task4
          ping:
          tags: test
''')
    assert len(items) == 1
    assert items[0].name == 'task4'


@skip_if_ansible_v1
def test_multiple_plays_multiple_blocks_multiple_tests(testdir):
    items, _ = create_playbook_and_collect_items(testdir, '''---
- hosts: all
  tasks:
    - block:
        - name: task1
          ping:
          tags: test

        - name: task2
          ping:

    - block:
        - name: task3
          ping:
          tags: test

        - name: task4
          ping:
          tags: test

- hosts: all
  tasks:
    - block:
        - name: task5
          ping:
          tags: test

    - block:
        - name: task6
          ping:
          tags: test

        - name: task7
          ping:
''')
    assert len(items) == 5
    assert items[0].name == 'task1'
    assert items[1].name == 'task3'
    assert items[2].name == 'task4'
    assert items[3].name == 'task5'
    assert items[4].name == 'task6'
