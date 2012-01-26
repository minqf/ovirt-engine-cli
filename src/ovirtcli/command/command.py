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


import uuid

from ovirtcli import metadata
from cli.command import Command
from ovirtcli.utils.typehelper import TypeHelper

from ovirtsdk.xml import params
from ovirtsdk.utils.parsehelper import ParseHelper
from ovirtsdk.infrastructure import brokers
import inspect
from ovirtcli.utils.methodhelper import MethodHelper


class OvirtCommand(Command):
    """Base class for oVirt commands."""

    def check_connection(self):
        """ensure we have a connection."""
        if self.context.connection is None:
            self.error('not connected', help='try \'help connect\'')
        return self.context.connection

    def resolve_base(self, options):
        """resolve a base object from a set of '--typeid value' options."""
        connection = self.check_connection()

        for opt, val in options.items():
            if not opt.endswith('id'):
                continue
            typename = opt[2:-2]
            coll = typename + 's'
            if not (TypeHelper.isKnownType(typename) or  TypeHelper.isKnownType(coll)):
                self.error('no such type: %s' % typename)

            if hasattr(connection, coll):
                coll_ins = getattr(connection, coll)
                uuid_cand = self._toUUID(val)
                if uuid_cand != None:
                    base = coll_ins.get(id=val)
                else:
                    base = coll_ins.get(name=val)

                if base is None and len(options) > 0:
                    self.error('cannot find object %s' % val)
                return base

    def create_object(self, typ, options, scope=None):
        """Create a new object of type `typ' based on the command-line
        options in `options'."""

        candidate = getattr(params, ParseHelper.getXmlWrapperType(typ))
        if candidate is not None:
            obj = candidate.factory()
            fields = metadata.get_fields(candidate, 'C', scope)
            for field in fields:
                key = '--%s' % field.name
                if key in options:
                    field.set(obj, options[key], self.context)
            return obj
        return None

    def update_object(self, obj, options, scope=None):
        """Create a new binding type of type `typ', and set its attributes
        with values from `options'."""
        fields = metadata.get_fields(type(obj.superclass), 'U', scope)
        for field in fields:
            key = '--%s' % field.name
            if key in options:
                field.set(obj, options[key], self.context)
        return obj

    def read_object(self):
        """If input was provided via stdin, then parse it and return a binding
        instance."""
        stdin = self.context.terminal.stdin
        # REVISE: this is somewhat of a hack (this detects a '<<' redirect by
        # checking if stdin is a StringIO)
        if not hasattr(stdin, 'len'):
            return
        buf = stdin.read()
        try:
            obj = params.parseString(buf)
        except Exception:
            self.error('could not parse input')
        return obj

    def get_collection(self, typ, opts=[], base=None):
        self.check_connection()
        connection = self.context.connection

        if base is None:
            if hasattr(connection, typ):
                return getattr(connection, typ).list(query=' '.join(opts) if len(opts) > 0
                                                                          else None)
        else:
            if hasattr(base, typ):
                return getattr(base, typ).list(query=' '.join(opts) if len(opts) > 0
                                                                    else None)
        return None

    def get_object(self, typ, id, base=None):
        """Return an object by id or name."""
        self.check_connection()
        connection = self.context.connection

        candidate = typ if typ is not None and isinstance(typ, type('')) \
                        else type(typ).__name__.lower()

        if base is None: base = connection
        if hasattr(base, candidate + 's'):
            coll = getattr(base, candidate + 's')
            if coll is not None:
                uuid_cand = self._toUUID(id)
                if uuid_cand != None:
                    return coll.get(id=id)
                else:
                    return coll.get(name=id)
        else:
            self.error('no such type: %s' % candidate)
        return None

    def _toUUID(self, string):
        try:
            return uuid.UUID(string)
        except:
            return None

    def _get_types(self, plural, method=None):
        """INTERNAL: return a list of types."""
        connection = self.check_connection()
        types = connection.__dict__.keys()
        sing_types = []

        if method:
            for decorator in TypeHelper.getKnownDecoratorsTypes():
                dct = getattr(brokers, decorator).__dict__
                if dct.has_key(method):
                    if decorator.endswith('s'):
                        cls_name = TypeHelper.getDecoratorType(decorator[:len(decorator) - 1])
                        if cls_name:
                            args = MethodHelper.getMethodArgs(brokers, cls_name, '__init__')
                            if len(args) == 3:
                                sing_types.append(args[2] + ' (context "' + args[1] + '")')
                            elif len(args) == 2:
                                sing_types.append(args[1])
            return sing_types

        if not plural:
            for item in types:
                if item and hasattr(connection, item) and type(getattr(connection, item)).__dict__.has_key(method):
                    if item.endswith('s'):
                        sing_types.append(item[:len(item) - 1])
                    else:
                        sing_types.append(item)
            return sing_types
        return types

    def get_singular_types(self, method=None):
        """Return a list of singular types."""
        return self._get_types(False, method)

    def get_plural_types(self, method=None):
        """Return a list of plural types."""
        return self._get_types(True, method)

    def get_options(self, method, resource, sub_resource=None):
        """Return a list of options for typ/action."""

        connection = self.check_connection()

        if isinstance(resource, type('')):
            if method == 'add':
                if not sub_resource:
                    if resource and hasattr(connection, resource + 's') and \
                       type(getattr(connection, resource + 's')).__dict__.has_key(method):
                        method_ref = getattr(getattr(connection, resource + 's'), method)
                else:
                    if hasattr(sub_resource, resource + 's') and \
                       hasattr(getattr(sub_resource, resource + 's'), method):
                        method_ref = getattr(getattr(sub_resource, resource + 's'), method)
                if not method_ref:
                    self.error('type cannot be created: %s' % resource)
        elif isinstance(resource, brokers.Base):
            if not sub_resource:
                if hasattr(resource, method):
                    method_ref = getattr(resource, method)
            else:
                pass

        doc = method_ref.__doc__
        params_arr = doc.split('\n')
        params_list = []
        params_hash = {}

        for var in params_arr:
            if '' != var and var.find('@param') != -1:
                splitted_line = var.strip().split(' ')
                if len(splitted_line) >= 2:
                    prefix = splitted_line[0].replace('@param ', '--').replace('@param', '--')
                    param = splitted_line[1]
                    typ = ''.join(splitted_line[2:])
                    if param.find('.') != -1:
                        splitted_param = param.split('.')
                        new_param = '_'.join(splitted_param[1:])
                        if new_param.find('id|name') != -1:
                            param = new_param.replace('_id|name', '')
                        else:
                            param = new_param

                    params_hash[param.replace(':', '')] = splitted_line[1].replace(':', '') \
                                                                          .replace('id|name', 'name')
                    params_list.append(prefix + param + ' ' + typ)
        return params_list
