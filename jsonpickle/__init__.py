# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""Python library for serializing any arbitrary object graph into 
`JSON <http://www.json.org/>`_.  It can take almost any Python object and turn
the object into JSON.  Additionally, it can reconstitute the object back into
Python. 

    >>> import jsonpickle
    >>> from jsonpickle.tests.classes import Thing

Create an object.

    >>> obj = Thing('A String')
    >>> print obj.name
    A String

Use jsonpickle to transform the object into a JSON string.
    
    >>> pickled = jsonpickle.encode(obj)
    >>> print pickled
    {"py/object": "jsonpickle.tests.classes.Thing", "name": "A String", "child": null}

Use jsonpickle to recreate a Python object from a JSON string
    
    >>> unpickled = jsonpickle.decode(pickled)
    >>> unpickled.name
    u'A String'

.. warning::

    Loading a JSON string from an untrusted source represents a potential
    security vulnerability.  jsonpickle makes no attempt to sanitize the input. 

The new object has the same type and data, but essentially is now a copy of 
the original.
    
    >>> obj == unpickled
    False
    >>> obj.name == unpickled.name
    True
    >>> type(obj) == type(unpickled)
    True

If you will never need to load (regenerate the Python class from JSON), you can
pass in the keyword unpicklable=False to prevent extra information from being
added to JSON.
    
    >>> oneway = jsonpickle.encode(obj, unpicklable=False)
    >>> print oneway
    {"name": "A String", "child": null}

"""




__version__ = '0.2.0a'
__all__ = ('encode', 'decode')


class JSONPluginMgr(object):
    """The JSONPluginMgr handles encoding and decoding.

    It tries these modules in this order:
        cjson, json, simplejson, demjson

    cjson is the fastest, and is tried first.
    json comes with python2.6 and is tried second.
    simplejson is a very popular backend and is tried third.
    demjson is the most permissive backend and is tried last.
    """
    def __init__(self):
        ## The names of backends that have been successfully imported
        self._backend_names = []

        ## A dictionary mapping backend names to encode/decode functions
        self._encoders = {}
        self._decoders = {}

        ## Options to pass to specific encoders
        self._encoder_options = {}

        ## The exception class that is thrown when a decoding error occurs
        self._decoder_exceptions = {}

        ## Whether we've loaded any backends successfully
        self._verified = False

        ## Try loading cjson, simplejson and demjson
        self.load_backend('cjson', 'encode', 'decode', 'DecodeError')
        self.load_backend('json', 'dumps', 'loads', ValueError)
        self.load_backend('simplejson', 'dumps', 'loads', ValueError)
        self.load_backend('demjson', 'encode', 'decode', 'JSONDecodeError')

    def _verify(self):
        """Ensures that we've loaded at least one JSON backend.
        """
        if not self._verified:
            raise AssertionError(
                    'jsonpickle requires at least one of the following:\n'
                    '    cjson, json (new in python2.6), simplejson, demjson'
                    )

    def load_backend(self, name, encode_name, decode_name, decode_exc):
        """Loads a backend by name.

        This method loads a backend and sets up references to that
        backend's encode/decode functions and exception classes.

        encode_name is the name of the backend's encode method.
        The method should take an object and return a string.

        decode_name names the backend's method for the reverse
        operation -- returning a Python object from a string.

        decode_exc can be either the name of the exception class
        used to denote decoding errors, or it can be a direct reference
        to the appropriate exception class itself.  If it is a name,
        then the assumption is that an exception class of that name
        can be found in the backend module's namespace.
        """
        try:
            ## Load the JSON backend
            mod = __import__(name)
            ## Handle submodules, e.g. django.utils.simplejson
            components = name.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
            ## We loaded a JSON backend, so setup our internal state
            self._verified = True
            self._encoders[name] = getattr(mod, encode_name)
            self._decoders[name] = getattr(mod, decode_name)
            ## Add this backend to the list of candidate backends
            self._backend_names.append(name)
            ## Setup the default args and kwargs for this encoder
            self._encoder_options[name] = ([], {})
            if type(decode_exc) is str:
                ## This backend's decoder exception is part of the backend
                self._decoder_exceptions[name] = getattr(mod, decode_exc)
            else:
                ## simplejson uses the ValueError exception
                self._decoder_exceptions[name] = decode_exc
        except ImportError:
            pass

    def encode(self, obj):
        """Attempts to encode an object into JSON.

        This tries the loaded backends in order and passes along the last
        exception if no backend is able to encode the object.
        """
        self._verify()
        for idx, name in enumerate(self._backend_names):
            try:
                optargs, kwargs = self._encoder_options[name]
                args = (obj,) + tuple(optargs)
                return self._encoders[name](*args, **kwargs)
            except:
                if idx == len(self._backend_names) - 1:
                    raise

    def decode(self, string):
        """Attempts to decode an object from a JSON string.

        This tries the loaded backends in order and passes along the last
        exception if no backends are able to decode the string.
        """
        self._verify()
        for idx, name in enumerate(self._backend_names):
            try:
                return self._decoders[name](string)
            except self._decoder_exceptions[name]:
                if idx == len(self._backend_names) - 1:
                    raise

    def set_preferred_backend(self, name):
        """Sets the preferred json backend.

        If a preferred backend is set then jsonpickle tries to use it
        before any other backend.

        For example,
            set_preferred_backend('simplejson')

        If the backend is not one of the built-in jsonpickle backends
        (cjson, json/simplejson, or demjson) then you must load the
        backend prior to calling set_preferred_backend.  An AssertionError
        exception is raised if the backend has not been loaded.
        """
        if name in self._backend_names:
            self._backend_names.remove(name)
            self._backend_names.insert(0, name)
        else:
            errmsg = 'The "%s" backend has not been loaded.' % name
            raise AssertionError(errmsg)

    def set_encoder_options(self, name, *args, **kwargs):
        """Associates encoder-specific options with an encoder.

        After calling set_encoder_options, any calls to jsonpickle's
        encode method will pass the supplied args and kwargs along to
        the appropriate backend's encode method.

        For example,
            set_encoder_options('simplejson', sort_keys=True, indent=4)
            set_encoder_options('demjson', compactly=False)

        See the appropriate encoder's documentation for details about
        the supported arguments and keyword arguments.
        """
        self._encoder_options[name] = (args, kwargs)

# Initialize a JSONPluginMgr
json = JSONPluginMgr()

# Export specific JSONPluginMgr methods into the jsonpickle namespace
set_preferred_backend = json.set_preferred_backend
set_encoder_options = json.set_encoder_options
load_backend = json.load_backend


def encode(value, unpicklable=True, max_depth=None, **kwargs):
    """Returns a JSON formatted representation of value, a Python object.

    The keyword argument 'unpicklable' defaults to True.
    If set to False, the output will not contain the information
    necessary to turn the JSON data back into Python objects.

    The keyword argument 'max_depth' defaults to None.
    If set to a non-negative integer then jsonpickle will not recurse
    deeper than 'max_depth' steps into the object.  Anything deeper
    than 'max_depth' is represented using a Python repr() of the object.

    >>> encode('my string')
    '"my string"'
    >>> encode(36)
    '36'

    >>> encode({'foo': True})
    '{"foo": true}'

    >>> encode({'foo': True}, max_depth=0)
    '"{\\'foo\\': True}"'

    >>> encode({'foo': True}, max_depth=1)
    '{"foo": "True"}'


    """
    j = Pickler(unpicklable=unpicklable,
                max_depth=max_depth)
    return json.encode(j.flatten(value))

def decode(string):
    """Converts the JSON string into a Python object.

    >>> str(decode('"my string"'))
    'my string'
    >>> decode('36')
    36
    """
    j = Unpickler()
    return j.restore(json.decode(string))
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

"""Helper functions for pickling and unpickling.  Most functions assist in 
determining the type of an object.
"""
import time
import types
import datetime

COLLECTIONS = set, list, tuple
PRIMITIVES = str, unicode, int, float, bool, long
NEEDS_REPR = (datetime.datetime, datetime.time, datetime.date, 
              datetime.timedelta)

def is_type(obj):
    """Returns True is obj is a reference to a type.

    >>> is_type(1)
    False

    >>> is_type(object)
    True

    >>> class Klass: pass
    >>> is_type(Klass)
    True
    """
    return type(obj) is types.TypeType or repr(obj).startswith('<class')

def is_object(obj):
    """Returns True is obj is a reference to an object instance.

    >>> is_object(1)
    True

    >>> is_object(object())
    True

    >>> is_object(lambda x: 1)
    False
    """
    return (isinstance(obj, object) and
            type(obj) is not types.TypeType and
            type(obj) is not types.FunctionType)

def is_primitive(obj):
    """Helper method to see if the object is a basic data type. Strings, 
    integers, longs, floats, booleans, and None are considered primitive 
    and will return True when passed into *is_primitive()*
    
    >>> is_primitive(3)
    True
    >>> is_primitive([4,4])
    False
    """
    if obj is None:
        return True
    elif type(obj) in PRIMITIVES:
        return True
    return False

def is_dictionary(obj):
    """Helper method for testing if the object is a dictionary.
    
    >>> is_dictionary({'key':'value'})
    True
    """   
    return type(obj) is dict

def is_collection(obj):
    """Helper method to see if the object is a Python collection (list, 
    set, or tuple).
    >>> is_collection([4])
    True
    """
    return type(obj) in COLLECTIONS

def is_list(obj):
    """Helper method to see if the object is a Python list.
    
    >>> is_list([4])
    True
    """
    return type(obj) is list

def is_set(obj):
    """Helper method to see if the object is a Python set.
    
    >>> is_set(set())
    True
    """
    return type(obj) is set

def is_tuple(obj):
    """Helper method to see if the object is a Python tuple.
    
    >>> is_tuple((1,))
    True
    """
    return type(obj) is tuple

def is_dictionary_subclass(obj):
    """Returns True if *obj* is a subclass of the dict type. *obj* must be 
    a subclass and not the actual builtin dict.
    
    >>> class Temp(dict): pass
    >>> is_dictionary_subclass(Temp())
    True
    """
    return (hasattr(obj, '__class__') and
            issubclass(obj.__class__, dict) and not is_dictionary(obj))
 
def is_collection_subclass(obj):
    """Returns True if *obj* is a subclass of a collection type, such as list
    set, tuple, etc.. *obj* must be a subclass and not the actual builtin, such
    as list, set, tuple, etc..
    
    >>> class Temp(list): pass
    >>> is_collection_subclass(Temp())
    True
    """
    #TODO add UserDict
    return issubclass(obj.__class__, COLLECTIONS) and not is_collection(obj)

def is_noncomplex(obj):
    """Returns True if *obj* is a special (weird) class, that is complex than 
    primitive data types, but is not a full object. Including:
    
        * :class:`~time.struct_time`
    """
    if type(obj) is time.struct_time:
        return True
    return False

def is_repr(obj):
    """Returns True if the *obj* must be encoded and decoded using the 
    :func:`repr` function. Including:
        
        * :class:`~datetime.datetime`
        * :class:`~datetime.date`
        * :class:`~datetime.time`
        * :class:`~datetime.timedelta`
    """
    return isinstance(obj, NEEDS_REPR)

def is_function(obj):
    """Returns true if passed a function

    >>> is_function(lambda x: 1)
    True

    >>> is_function(locals)
    True

    >>> def method(): pass
    >>> is_function(method)
    True

    >>> is_function(1)
    False
    """
    if type(obj) is types.FunctionType:
        return True
    if not is_object(obj):
        return False
    if not hasattr(obj, '__class__'):
        return False
    module = obj.__class__.__module__
    name = obj.__class__.__name__
    return (module == '__builtin__' and
            name in ('function', 'builtin_function_or_method'))
"""The jsonpickle.tags module provides the custom tags
used for pickling and unpickling Python objects.

These tags are keys into the flattened dictionaries
created by the Pickler class.  The Unpickler uses
these custom key names to identify dictionaries
that need to be specially handled.
"""
OBJECT = 'py/object'
TYPE   = 'py/type'
REPR   = 'py/repr'
REF    = 'py/ref'
TUPLE  = 'py/tuple'
SET    = 'py/set'

# All reserved tag names
RESERVED = set([OBJECT, TYPE, REPR, REF, TUPLE, SET])
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
import types




class Pickler(object):
    """Converts a Python object to a JSON representation.
    
    Setting unpicklable to False removes the ability to regenerate
    the objects into object types beyond what the standard simplejson
    library supports.

    Setting max_depth to a negative number means there is no
    limit to the depth jsonpickle should recurse into an
    object.  Setting it to zero or higher places a hard limit
    on how deep jsonpickle recurses into objects, dictionaries, etc.

    >>> p = Pickler()
    >>> p.flatten('hello world')
    'hello world'
    """
    
    def __init__(self, unpicklable=True, max_depth=None):
        self.unpicklable = unpicklable
        ## The current recursion depth
        self._depth = -1
        ## The maximal recursion depth
        self._max_depth = max_depth
        ## Maps id(obj) to reference names
        self._objs = {}
        ## The namestack grows whenever we recurse into a child object
        self._namestack = []

    def _reset(self):
        self._objs = {}
        self._namestack = []

    def _push(self):
        """Steps down one level in the namespace.
        """
        self._depth += 1

    def _pop(self, value):
        """Step up one level in the namespace and return the value.
        If we're at the root, reset the pickler's state.
        """
        self._depth -= 1
        if self._depth == -1:
            self._reset()
        return value

    def _mkref(self, obj):
        objid = id(obj)
        if objid not in self._objs:
            self._objs[objid] = '/' + '/'.join(self._namestack)
            return True
        return False

    def _getref(self, obj):
        return {REF: self._objs.get(id(obj))}

    def flatten(self, obj):
        """Takes an object and returns a JSON-safe representation of it.
        
        Simply returns any of the basic builtin datatypes
        
        >>> p = Pickler()
        >>> p.flatten('hello world')
        'hello world'
        >>> p.flatten(u'hello world')
        u'hello world'
        >>> p.flatten(49)
        49
        >>> p.flatten(350.0)
        350.0
        >>> p.flatten(True)
        True
        >>> p.flatten(False)
        False
        >>> r = p.flatten(None)
        >>> r is None
        True
        >>> p.flatten(False)
        False
        >>> p.flatten([1, 2, 3, 4])
        [1, 2, 3, 4]
        >>> p.flatten((1,2,))[TUPLE]
        [1, 2]
        >>> p.flatten({'key': 'value'})
        {'key': 'value'}
        """

        self._push()
        
        if self._depth == self._max_depth:
            return self._pop(repr(obj))

        if is_primitive(obj):
            return self._pop(obj)

        if is_list(obj):
            return self._pop([ self.flatten(v) for v in obj ])

        # We handle tuples and sets by encoding them in a "(tuple|set)dict"
        if is_tuple(obj):
            return self._pop({TUPLE: [ self.flatten(v) for v in obj ]})

        if is_set(obj):
            return self._pop({SET: [ self.flatten(v) for v in obj ]})

        if is_dictionary(obj):
            return self._pop(self._flatten_dict_obj(obj, obj.__class__()))

        if is_type(obj):
            return self._pop(_mktyperef(obj))

        if is_object(obj):
            data = {}
            data['_'] = repr(obj)
            has_class = hasattr(obj, '__class__')
            has_dict = hasattr(obj, '__dict__')
            if self._mkref(obj):
                if has_class and not is_repr(obj):
                    module, name = _getclassdetail(obj)
                    if self.unpicklable is True:
                        data[OBJECT] = '%s.%s' % (module, name)

                if is_repr(obj):
                    if self.unpicklable is True:
                        data[REPR] = '%s/%s' % (obj.__class__.__module__,
                                                     repr(obj))
                    else:
                        data = unicode(obj)
                    return self._pop(data)

                if is_dictionary_subclass(obj):
                    return self._pop(self._flatten_dict_obj(obj, data))

                if is_noncomplex(obj):
                    return self._pop([self.flatten(v) for v in obj])

                if has_dict:
                    return self._pop(self._flatten_dict_obj(obj.__dict__, data))
            else:
                # We've seen this object before so place an object
                # reference tag in the data. This avoids infinite recursion
                # when processing cyclical objects.
                return self._pop(self._getref(obj))

            return self._pop(data)
        # else, what else? (methods, functions, old style classes...)

    def _flatten_dict_obj(self, obj, data):
        """_flatten_dict_obj recursively calls to flatten() on a dictionary's values.
        and places them into data.
        """
        for k, v in obj.iteritems():
            if is_function(v):
                continue
            if type(k) not in types.StringTypes:
                k = repr(k)
            self._namestack.append(k)
            data[k] = self.flatten(v)
            self._namestack.pop()
        return data

def _mktyperef(obj):
    """Returns a typeref dictionary.  This is used to implement referencing.

    >>> from jsonpickle import tags
    >>> _mktyperef(AssertionError)[TYPE].rsplit('.', 1)[0]
    'exceptions'

    >>> _mktyperef(AssertionError)[TYPE].rsplit('.', 1)[-1]
    'AssertionError'
    """
    return {TYPE: '%s.%s' % (obj.__module__, obj.__name__)}

def _getclassdetail(obj):
    """Helper class to return the class of an object.
    
    >>> class Klass(object): pass
    >>> _getclassdetail(Klass())
    ('jsonpickle.pickler', 'Klass')
    >>> _getclassdetail(25)
    ('__builtin__', 'int')
    >>> _getclassdetail(None)
    ('__builtin__', 'NoneType')
    >>> _getclassdetail(False)
    ('__builtin__', 'bool')
    """
    cls = obj.__class__
    module = getattr(cls, '__module__')
    name = getattr(cls, '__name__')
    return module, name
# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

import sys




class Unpickler(object):
    def __init__(self):
        ## The current recursion depth
        self._depth = 0
        ## Maps reference names to object instances
        self._namedict = {}
        ## The namestack grows whenever we recurse into a child object
        self._namestack = []

    def _reset(self):
        """Resets the object's internal state.
        """
        self._namedict = {}
        self._namestack = []

    def _push(self):
        """Steps down one level in the namespace.
        """
        self._depth += 1

    def _pop(self, value):
        """Step up one level in the namespace and return the value.
        If we're at the root, reset the unpickler's state.
        """
        self._depth -= 1
        if self._depth == 0:
            self._reset()
        return value

    def restore(self, obj):
        """Restores a flattened object to its original python state.
        
        Simply returns any of the basic builtin types
        
        >>> u = Unpickler()
        >>> u.restore('hello world')
        'hello world'
        >>> u.restore({'key': 'value'})
        {'key': 'value'}
        """
        self._push()

        if has_tag(obj, REF):
            return self._pop(self._namedict.get(obj[REF]))

        if has_tag(obj, TYPE):
            typeref = loadclass(obj[TYPE])
            if not typeref:
                return self._pop(obj)
            return self._pop(typeref)

        if has_tag(obj, REPR):
            return self._pop(loadrepr(obj[REPR]))

        if has_tag(obj, OBJECT):

            cls = loadclass(obj[OBJECT])
            if not cls:
                return self._pop(obj)
            try:
                instance = object.__new__(cls)
            except TypeError:
                # old-style classes
                try:
                    instance = cls()
                except TypeError:
                    # fail gracefully if the constructor requires arguments
                    self._mkref(obj)
                    return self._pop(obj)
            
            # keep a obj->name mapping for use in the _isobjref() case
            self._mkref(instance)

            for k, v in obj.iteritems():
                # ignore the reserved attribute
                if k in RESERVED:
                    continue
                self._namestack.append(k)
                # step into the namespace
                value = self.restore(v)
                if (is_noncomplex(instance) or
                        is_dictionary_subclass(instance)):
                    instance[k] = value
                else:
                    instance.__dict__[k] = value
                # step out
                self._namestack.pop()
            return self._pop(instance)

        if is_list(obj):
            return self._pop([self.restore(v) for v in obj])

        if has_tag(obj, TUPLE):
            return self._pop(tuple([self.restore(v) for v in obj[TUPLE]]))

        if has_tag(obj, SET):
            return self._pop(set([self.restore(v) for v in obj[SET]]))

        if is_dictionary(obj):
            data = {}
            for k, v in obj.iteritems():
                self._namestack.append(k)
                data[k] = self.restore(v)
                self._namestack.pop()
            return self._pop(data)

        return self._pop(obj)

    def _refname(self):
        """Calculates the name of the current location in the JSON stack.

        This is called as jsonpickle traverses the object structure to
        create references to previously-traversed objects.  This allows
        cyclical data structures such as doubly-linked lists.
        jsonpickle ensures that duplicate python references to the same
        object results in only a single JSON object definition and
        special reference tags to represent each reference.

        >>> u = Unpickler()
        >>> u._namestack = []
        >>> u._refname()
        '/'

        >>> u._namestack = ['a']
        >>> u._refname()
        '/a'

        >>> u._namestack = ['a', 'b']
        >>> u._refname()
        '/a/b'

        """
        return '/' + '/'.join(self._namestack)

    def _mkref(self, obj):
        """
        >>> from jsonpickle.tests.classes import Thing
        >>> thing = Thing('referenced-thing')
        >>> u = Unpickler()
        >>> u._mkref(thing)
        '/'
        >>> u._namedict['/']
        jsonpickle.tests.classes.Thing("referenced-thing")

        """
        name = self._refname()
        if name not in self._namedict:
            self._namedict[name] = obj
        return name

def loadclass(module_and_name):
    """Loads the module and returns the class.
    
    >>> loadclass('jsonpickle.tests.classes.Thing')
    <class 'jsonpickle.tests.classes.Thing'>

    >>> loadclass('example.module.does.not.exist.Missing')
    

    >>> loadclass('jsonpickle.tests.classes.MissingThing')
    

    """
    try:
        module, name = module_and_name.rsplit('.', 1)
        __import__(module)
        return getattr(sys.modules[module], name)
    except:
        return None

def loadrepr(reprstr):
    """Returns an instance of the object from the object's repr() string. It
    involves the dynamic specification of code.
    
    >>> from jsonpickle import tags
    >>> loadrepr('jsonpickle.tests.classes/jsonpickle.tests.classes.Thing("json")')
    jsonpickle.tests.classes.Thing("json")

    """
    module, evalstr = reprstr.split('/')
    mylocals = locals()
    localname = module
    if '.' in localname:
        localname = module.split('.', 1)[0]
    mylocals[localname] = __import__(module)
    return eval(evalstr)

def has_tag(obj, tag):
    """Helper class that tests to see if the obj is a dictionary
    and contains a particular key/tag.

    >>> obj = {'test': 1}
    >>> has_tag(obj, 'test')
    True
    >>> has_tag(obj, 'fail')
    False

    >>> has_tag(42, 'fail')
    False

    """
    return type(obj) is dict and tag in obj
