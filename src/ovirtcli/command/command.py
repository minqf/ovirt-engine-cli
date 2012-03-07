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


from cli.command import Command
from ovirtcli.utils.typehelper import TypeHelper

from ovirtsdk.xml import params
from ovirtsdk.utils.parsehelper import ParseHelper
import uuid
from ovirtcli.utils.methodhelper import MethodHelper
from ovirtsdk.infrastructure import brokers
from papyon.util.odict import odict


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
            if opt.endswith('-id') or not opt.endswith('-identifier'):
                continue
            typename = opt[2:-11]
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

    def __do_set_data(self, obj, prop, fq_prop, val):
        """INTERNAL: set data in to object based on 'prop' map segmentation"""
        if prop.find('-') != -1:
            props = prop.split('-')
            props_len = len(props)

            for i in range(props_len):
                if i == (props_len - 1):
                    self.__set_property(obj, props[i], val, fq_prop)
                    return
                if type(obj) == list:
                    if len(obj) == 0:
                        cand = ParseHelper.getXmlType(props[i])
                        if cand:
                            obj_cand = cand.factory()
                            self.__do_set_data(obj_cand, '-'.join(props[i + 1:]), fq_prop, val)
                            obj.append(obj_cand)
                            return
                    else:
                        self.__do_set_data(obj[-1], '-'.join(props[i + 1:]), fq_prop, val)
                        return
                elif hasattr(obj, props[i]):
                    content = getattr(obj, props[i])
                    if content is None:
                        cand1 = ParseHelper.getXmlType(props[i])
                        if cand1:
                            cand = cand1.factory()
                            setattr(obj, props[i], cand)
                            obj = cand
                    else:
                        obj = content
                else:
                    cand2 = ParseHelper.getXmlTypeInstance(props[i])
                    if cand2 and hasattr(obj, cand2):
                        cand1 = ParseHelper.getXmlType(cand2)
                        if cand1:
                            props[i] = cand2
                            cand = cand1.factory()
                            setattr(obj, props[i], cand)
                            obj = cand
                        else:
                            self.error('failed locating "%s" type.' % cand2)
                    else:
#                        self.error('failed locating "%s" type.' % props[i])
                        self.error('*%s* is not valid argument segment.' % props[i])
        else:
            self.__set_property(obj, prop, val, fq_prop)

    def __set_property(self, obj, prop, val, fq_prop):
        """INTERNAL: set data in to property"""
        if hasattr(obj, prop):
            setattr(obj, prop, val)
        elif hasattr(obj, prop + '_'):
            setattr(obj, prop + '_', val)
        else:
            pass
#            self.error('%s is not valid argument.' % fq_prop)

    def update_object_data(self, obj, options, scope=None):
        """Updates object properties with values from `options'."""

        for key in options.keys():
            prop = key.replace('--', '')
            val = options[key]
            if not prop.endswith('-id') and prop.endswith('-identifier'): continue
            self.__do_set_data(obj=obj, prop=prop, fq_prop=key, val=val)

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


    def _get_query_params(self, opts, query_arg='--query', kwargs_arg='--kwargs'):
        """INTERNAL: retrieves query and kwargs from attribute options"""
        query = opts[query_arg] if opts.has_key(query_arg) else None
        kw = {}
        if opts.has_key(kwargs_arg):
            for item in opts[kwargs_arg].split(';'):
                k, v = item.split('=')
                kw[k.replace('-', '.')] = v
        return query, kw


    def get_collection(self, typ, opts={}, base=None):
        """retrieves collection members"""
        self.check_connection()
        connection = self.context.connection
        query, kwargs = self._get_query_params(opts)

        if base is None:
            if hasattr(connection, typ):
                options = self.get_options(method='list', resource=TypeHelper.to_singular(typ), as_params_collection=True)

                #TODO: support generic parameters processing                 
                if query and 'query' not in options:
                    self.error('"--query" argument is not available for this type of listing')
                if kwargs and 'kwargs' not in options:
                    self.error('"--kwargs" argument is not available for this type of listing')

                if query and kwargs:
                    return getattr(connection, typ).list(query=query, **kwargs)
                if query:
                    return getattr(connection, typ).list(query=query)
                if kwargs:
                    return getattr(connection, typ).list(**kwargs)
                return getattr(connection, typ).list()
        else:
            if hasattr(base, typ):
                options = self.get_options(method='list', resource=getattr(base, typ), as_params_collection=True)

                if query and 'query' not in options:
                    self.error('"--query" argument is not available for this type of listing')
                if kwargs and 'kwargs' not in options:
                    self.error('"--kwargs" argument is not available for this type of listing')

                if query and kwargs:
                    return getattr(base, typ).list(query=query, **kwargs)
                if query:
                    return getattr(base, typ).list(query=query)
                if kwargs:
                    return getattr(base, typ).list(**kwargs)
                return getattr(base, typ).list()

    def get_object(self, typ, obj_id, base=None, opts={}):
        """Return an object by id or name."""
        self.check_connection()
        connection = self.context.connection
        name, kwargs = self._get_query_params(opts, query_arg='--name')

        candidate = typ if typ is not None and isinstance(typ, type('')) \
                        else type(typ).__name__.lower()

        if base:
            options = self.get_options(method='get', resource=base, as_params_collection=True)
        else:
            options = self.get_options(method='get', resource=typ, as_params_collection=True)
            base = connection

        #TODO: support generic parameters processing        
        if name and 'name' not in options:
            self.error('"--name" argument is not available for this type of show')
        if kwargs and 'kwargs' not in options:
            self.error('"--kwargs" argument is not available for this type of show')

        if hasattr(base, candidate + 's'):
            coll = getattr(base, candidate + 's')
            if coll is not None:
                if name and kwargs:
                    return coll.get(name=name, **kwargs)
                if name:
                    return coll.get(name=name)
                if kwargs:
                    return coll.get(**kwargs)
                else:
                    uuid_cand = self._toUUID(obj_id)
                    if uuid_cand != None:
                        return coll.get(id=obj_id)
                    else:
                        return coll.get(name=obj_id)
        else:
            self.error('no such type: %s' % candidate)
        return None

    def _toUUID(self, string):
        try:
            return uuid.UUID(string)
        except:
            return None

    def get_singular_types(self, method=None):
        """Return a list of singular types."""
        return TypeHelper.get_types_by_method(False, method)

    def get_plural_types(self, method=None):
        """Return a list of plural types."""
        return TypeHelper.get_types_by_method(True, method)

    def get_options(self, method, resource, sub_resource=None, as_params_collection=False):
        """Return a list of options for typ/action."""

        method_ref = None
        connection = self.check_connection()

        if isinstance(resource, type('')):
            if not sub_resource:
                    if resource and hasattr(connection, resource + 's') and \
                       type(getattr(connection, resource + 's')).__dict__.has_key(method):
                        method_ref = getattr(getattr(connection,
                                                     resource + 's'),
                                             method)
            else:
                if hasattr(sub_resource, resource + 's') and \
                type(getattr(sub_resource, resource + 's')).__dict__.has_key(method):
                    method_ref = getattr(getattr(sub_resource,
                                                 resource + 's'),
                                         method)
                elif hasattr(sub_resource, resource + 's') and \
                hasattr(brokers, TypeHelper.to_singular(type(getattr(sub_resource,
                                                             resource + 's')).__name__)) and \
                hasattr(getattr(brokers, TypeHelper.to_singular(type(getattr(sub_resource,
                                                                     resource + 's')).__name__)),
                        method):
                    method_ref = getattr(getattr(brokers,
                                                 TypeHelper.to_singular(type(getattr(sub_resource,
                                                                             resource + 's')).__name__)),
                                         method)

            if not method_ref:
                self.error('cannot find any context for type "%s"' % resource)

        elif isinstance(resource, brokers.Base):
            if hasattr(resource, method):
                method_ref = getattr(resource, method)
            elif hasattr(brokers, type(resource).__name__ + 's') and \
            hasattr(getattr(brokers, type(resource).__name__ + 's'), method):
                method_ref = getattr(getattr(brokers, type(resource).__name__ + 's'), method)

        return MethodHelper.get_documented_arguments(method_ref, as_params_collection)

    def is_supported_type(self, types, typ):
        if typ not in types:
            self.error('not supported type "%s"' % typ)
            return False
        return True

    def execute_method(self, resource, method_name, opts={}):
        """executes given method with specified opts."""

        if hasattr(resource, method_name):
            method = getattr(resource, method_name)

            method_args = odict().fromkeys(MethodHelper.getMethodArgs(brokers,
                                                                      method.im_class.__name__,
                                                                      method_name,
                                                                      drop_self=True))

            if method_args:
                for arg in method_args.keys():
                    param_type = ParseHelper.getXmlType(arg)
                    if param_type:
                        method_args[arg] = self.update_object_data(param_type.factory(), opts)
                    elif opts.has_key('--' + arg):
                        method_args[arg] = opts['--' + arg]
                    else:
                        #TODO: throw error if param is mandatory
                        pass

                result = method(**method_args)
            else:
                result = method()
            return result
        else:
            self.error('no such action "%s"' % method_name)

    def _get_action_methods(self, obj):
        """INTERNAL: return a list of type actions."""

        return MethodHelper.get_object_methods(obj, exceptions=['delete', 'update'])
