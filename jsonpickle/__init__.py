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
    {"classname__": "Thing", "child": null, "name": "A String", "classmodule__": "jsonpickle.tests.classes"}

Use jsonpickle to recreate a Python object from a JSON string
    
    >>> unpickled = jsonpickle.decode(pickled)
    >>> print unpickled.name
    A String

The new object has the same type and data, but essentially is now a copy of the original.
    
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
__all__ = [
    'encode', 'decode'
]


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
            mod = __import__(name)
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

json = JSONPluginMgr()


def encode(value, **kwargs):
    """Returns a JSON formatted representation of value, a Python object.

    Optionally takes a keyword argument unpicklable.  If set to False,
    the output does not contain the information necessary to turn
    the json back into Python.

    >>> encode('my string')
    '"my string"'
    >>> encode(36)
    '36'
    """
    j = Pickler(unpicklable=__isunpicklable(kwargs))
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

def __isunpicklable(kw):
    """Utility function for finding keyword unpicklable and returning value.
    Default is assumed to be True.

    >>> __isunpicklable({})
    True
    >>> __isunpicklable({'unpicklable':True})
    True
    >>> __isunpicklable({'unpicklable':False})
    False

    """
    if 'unpicklable' in kw and not kw['unpicklable']:
        return False
    return True
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

COLLECTIONS = set, list, tuple
PRIMITIVES = str, unicode, int, float, bool, long

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
    if type(obj) is dict:
        return True
    return False

def is_collection(obj):
    """Helper method to see if the object is a Python collection (list, 
    set, or tuple).
    
    >>> is_collection([4])
    True
    """
    if type(obj) in COLLECTIONS:
        return True
    return False

def is_dictionary_subclass(obj):
    """Returns True if *obj* is a subclass of the dict type. *obj* must be 
    a subclass and not the actual builtin dict.
    
    >>> class Temp(dict): pass
    >>> is_dictionary_subclass(Temp())
    True
    """
    #TODO add UserDict
    if issubclass(obj.__class__, dict) and not is_dictionary(obj):
        return True
    return False

def is_collection_subclass(obj):
    """Returns True if *obj* is a subclass of a collection type, such as list
    set, tuple, etc.. *obj* must be a subclass and not the actual builtin, such
    as list, set, tuple, etc..
    
    >>> class Temp(list): pass
    >>> is_collection_subclass(Temp())
    True
    """
    #TODO add UserDict
    if issubclass(obj.__class__, COLLECTIONS) and not is_collection(obj):
        return True
    return False

def is_noncomplex(obj):
    """Returns True if *obj* is a special (weird) class, that is complex than 
    primitive data types, but is not a full object. Including:
    
        * :class:`~time.struct_time`
    """
    if type(obj) is time.struct_time:
        return True
    return False

# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 John Paulett (john -at- 7oars.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.



class Pickler(object):
    """Converts a Python object to a JSON representation.
    
    Setting unpicklable to False removes the ability to regenerate
    the objects into object types beyond what the standard simplejson
    library supports.

    >>> p = Pickler()
    >>> p.flatten('hello world')
    'hello world'
    """
    
    def __init__(self, unpicklable=True):
        self.unpicklable = unpicklable
    
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
        >>> p.flatten((1,))
        (1,)
        >>> p.flatten({'key': 'value'})
        {'key': 'value'}
        """
        
        if is_primitive(obj):
            return obj
        elif is_collection(obj):
            data = [] # obj.__class__()
            for v in obj:
                data.append(self.flatten(v))
            return obj.__class__(data)
            #TODO handle tuple and sets
        elif is_dictionary(obj):
            data = obj.__class__()
            for k, v in obj.iteritems():
                data[k] = self.flatten(v)
            return data
        elif isinstance(obj, object):
            data = {}
            module, name = _getclassdetail(obj)
            if self.unpicklable is True:
                data['classmodule__'] = module
                data['classname__'] = name 
            if is_dictionary_subclass(obj):
                for k, v in obj.iteritems():
                    data[k] = self.flatten(v)
            elif is_noncomplex(obj):
                data = [] # obj.__class__()
                for v in obj:
                    data.append(self.flatten(v))
            else:
                for k, v in obj.__dict__.iteritems():
                    data[str(k)] = self.flatten(v)
            return data
        # else, what else? (classes, methods, functions, old style classes...)
        
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
    cls = getattr(obj, '__class__')
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
    def restore(self, obj):
        """Restores a flattened object to its original python state.
        
        Simply returns any of the basic builtin types
        
        >>> u = Unpickler()
        >>> u.restore('hello world')
        'hello world'
        >>> u.restore({'key': 'value'})
        {'key': 'value'}
        """
        if self._isclassdict(obj):
            cls = self._loadclass(obj['classmodule__'], obj['classname__'])
            
            try:
                instance = object.__new__(cls)
            except TypeError:
                # old-style classes
                instance = cls()
            
            for k, v in obj.iteritems():
                # ignore the fake attribute
                if k in ('classmodule__', 'classname__'):
                    continue
                value = self.restore(v)
                if (is_noncomplex(instance) or
                        is_dictionary_subclass(instance)):
                    instance[k] = value
                else:
                    instance.__dict__[k] = value
            return instance
        elif is_collection(obj):
            # currently restores all collections to lists, even sets and tuples
            data = []
            for v in obj:
                data.append(self.restore(v))
            return data
        elif is_dictionary(obj):
            data = {}
            for k, v in obj.iteritems():
                data[k] = self.restore(v)
            return data
        else:
            return obj
        
    def _loadclass(self, module, name):
        """Loads the module and returns the class.
        
        >>> u = Unpickler()
        >>> u._loadclass('jsonpickle.tests.classes','Thing')
        <class 'jsonpickle.tests.classes.Thing'>
        """
        __import__(module)
        mod = sys.modules[module]
        cls = getattr(mod, name)
        return cls
    
    def _isclassdict(self, obj):
        """Helper class that tests to see if the obj is a flattened object
        
        >>> u = Unpickler()
        >>> u._isclassdict({'classmodule__':'__builtin__', 'classname__':'int'})
        True
        >>> u._isclassdict({'key':'value'})    
        False
        >>> u._isclassdict(25)    
        False
        """
        if type(obj) is dict and 'classmodule__' in obj and 'classname__' in obj:
            return True
        return False
