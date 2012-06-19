#
# Copyright (c) 2010 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


from ovirtcli.shell.cmdshell import CmdShell
from ovirtcli.utils.typehelper import TypeHelper
from ovirtcli.utils.autocompletionhelper import AutoCompletionHelper
from ovirtsdk.infrastructure import brokers
from ovirtcli.utils.methodhelper import MethodHelper


class DeleteCmdShell(CmdShell):
    NAME = 'delete'

    def __init__(self, context, parser):
        CmdShell.__init__(self, context, parser)

    def do_delete(self, args):
        return self.context.execute_string(DeleteCmdShell.NAME + ' ' + args + '\n')

    def __add_resource_specific_options(self, obj, specific_options, line, key=None):
        obj_type = TypeHelper.getDecoratorType(TypeHelper.to_singular(obj))
        if obj_type and hasattr(brokers, obj_type):
            obj_typ_ref = getattr(brokers, obj_type)
            if obj_typ_ref and hasattr(obj_typ_ref, DeleteCmdShell.NAME):
                method_args = MethodHelper.get_documented_arguments(method_ref=getattr(obj_typ_ref, DeleteCmdShell.NAME),
                                                                    as_params_collection=True,
                                                                    spilt_or=True)

                if method_args:
                    specific_options[key if key is not None else obj] = method_args

    def complete_delete(self, text, line, begidx, endidx):
        args = TypeHelper.get_types_containing_method(DeleteCmdShell.NAME, expendNestedTypes=True)
        specific_options = self.get_resource_specific_options(args,
                                                              line,
                                                              callback=self.__add_resource_specific_options)

        return AutoCompletionHelper.complete(line, text, args, specific_options=specific_options)

