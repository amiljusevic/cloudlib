# Copyright 2015, Kevin Carter.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import unittest

import mock

from cloudlib import arguments


class TestArgumentClassVars(unittest.TestCase):
    def setUp(self):
        self.args = {}

    def test_class_variables(self):
        self.arguments = arguments.ArgumentParserator(
            arguments_dict=self.args,
            env_name='test_args',
            epilog='epilog',
            title='title',
            detail='detail',
            description='description'
        )
        self.assertEqual(self.arguments.usage, '%(prog)s')
        self.assertEqual(self.arguments.env_name, 'test_args')
        self.assertEqual(self.arguments.epilog, 'epilog')
        self.assertEqual(self.arguments.title, 'title')
        self.assertEqual(self.arguments.detail, 'detail')
        self.assertEqual(self.arguments.description, 'description')


class TestArguments(unittest.TestCase):
    def setUp(self):
        self.sys_argv_original = arguments.argparse._sys.argv
        self.sys_argv = arguments.argparse._sys.argv = []
        self.print_patched = mock.patch(
            'cloudlib.arguments.argparse._sys.stderr'
        )
        self.mock_open = self.print_patched.start()

        self.args = {
            'optional_args': {
                'base_option1': {
                    'commands': ['--base-option1'],
                    'help': 'Helpful Information'
                }
            },
            'positional_args': {
                'possitional1': {
                    'help': 'Helpful Information',
                }
            },
            'subparsed_args': {
                'subparsed1': {
                    'help': 'Helpful Information',
                    'optional_args': {
                        'groups': {
                            'some_group_name': {
                                'text': 'other information',
                                'group': [
                                    'other_option3'
                                ]
                            }
                        },
                        'mutually_exclusive': {
                            'some_name': {
                                'text': 'some information',
                                'required': False,
                                'group': [
                                    'option1',
                                    'option2'
                                ]
                            }
                        },
                        'option1': {
                            'commands': ['--option1'],
                            'default': False,
                            'action': 'store_true',
                            'help': 'Helpful Information'
                        },
                        'option2': {
                            'commands': ['--option2'],
                            'default': False,
                            'action': 'store_true',
                            'help': 'Helpful Information'
                        },
                        'other_option3': {
                            'commands': ['--other-option3', '-O'],
                            'metavar': '[STRING]',
                            'type': str,
                            'help': 'Helpful Information'
                        }
                    }
                }
            }
        }
        self.arguments = arguments.ArgumentParserator(
            arguments_dict=self.args,
            env_name='test_args',
            epilog='epilog',
            title='title',
            detail='detail',
            description='description'
        )

    def tearDown(self):
        arguments.argparse._sys.argv = self.sys_argv_original
        self.print_patched.stop()

    def test_arg_parser_simple(self):
        arguments.argparse._sys.argv = ['app', 'subparsed1', 'testval1']
        self.assertTrue(isinstance(self.arguments.arg_parser(), dict))

    def test_arg_parser_options_simple(self):
        arguments.argparse._sys.argv = [
            'app', '--base-option1', 'testval1', 'subparsed1', 'testval2'
        ]
        self.assertTrue(isinstance(self.arguments.arg_parser(), dict))

    def test_arg_parser_options_simple_options(self):
        arguments.argparse._sys.argv = [
            'app', '--base-option1', 'testval1', 'subparsed1', '--option1',
            'testval2'
        ]
        self.assertTrue(isinstance(self.arguments.arg_parser(), dict))

    def test_arg_parser_options_simple_options_multual_exclusive(self):
        arguments.argparse._sys.argv = [
            'app', '--base-option1', 'testval1', 'subparsed1',
            '--option1', '--option2', 'testval2'
        ]
        # Mutual exclusive arguments in sub groups was partial broken in
        # Python 2.6.x. Related http://bugs.python.org/issue10680
        if sys.version_info < (2, 6, 0):
            self.assertRaises(SystemExit, self.arguments.arg_parser)

    def test_arg_parser_options_simple_more_options(self):
        arguments.argparse._sys.argv = [
            'app', '--base-option1', 'testval1', 'subparsed1',
            '--option1', '--other-option3', 'testval3', 'testval2'
        ]
        self.assertTrue(isinstance(self.arguments.arg_parser(), dict))

    def test__setup_parser(self):
        arguments.argparse._sys.argv = ['app', 'subparsed1', 'testval1']
        setup = self.arguments._setup_parser()
        parser, subparser, rargs = setup

        self.assertTrue(isinstance(setup, tuple))
        self.assertTrue(isinstance(parser, arguments.argparse.ArgumentParser))
        self.assertTrue(
            isinstance(subparser, arguments.argparse._SubParsersAction)
        )
        self.assertTrue(isinstance(rargs, list))

    def test__add_opt_argument(self):
        arguments.argparse._sys.argv = ['app', 'subparsed1', 'testval1']
        setup = self.arguments._setup_parser()
        parser, subparser, rargs = setup
        op_args = {
            'option1': {
                'commands': ['--base-option1'],
                'help': 'Helpful Information'
            }
        }
        self.arguments._add_opt_argument(op_args, parser)
