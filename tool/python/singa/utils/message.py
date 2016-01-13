#!/usr/bin/env python

#/************************************************************
#*
#* Licensed to the Apache Software Foundation (ASF) under one
#* or more contributor license agreements.  See the NOTICE file
#* distributed with this work for additional information
#* regarding copyright ownership.  The ASF licenses this file
#* to you under the Apache License, Version 2.0 (the
#* "License"); you may not use this file except in compliance
#* with the License.  You may obtain a copy of the License at
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing,
#* software distributed under the License is distributed on an
#* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#* KIND, either express or implied.  See the License for the
#* specific language governing permissions and limitations
#* under the License.
#*
#*************************************************************/

import sys, os
from utility import *
sys.path.append(os.path.join(os.path.dirname(__file__), '../../pb2'))

'''
This script reads proto files in ../../pb2, generated by proto buffer compiler.
 - Message class creates an object for proto and sets initial vlaues for
   the fields, specified by kwargs
 - make_function method generates a method named enumInitMethod that returns
   enum values of given enum type, defined in the proto files
'''

MODULE_LIST = []

# import all modules in dir singa_root/tool/python/pb2
# except common, singa, and __init__
for f in os.listdir(os.path.join(os.path.dirname(__file__), '../../pb2')):
    if (f.endswith(".pyc")):
        continue
    if(f == "__init__.py" or f == "common_pb2.py" or f == "singa_pb2.py"):
        continue
    module_name = f.split('.')[0]
    module_obj = __import__(module_name)
    MODULE_LIST.append(module_obj)
    for func_name in dir(module_obj):
        if not func_name.startswith("__"):
            globals()[func_name] = getattr(module_obj, func_name)

class Message(object):
    def __init__(self, protoname, **kwargs):
        for module_obj in MODULE_LIST:
            if hasattr(module_obj, protoname+"Proto"):
                class_ = getattr(module_obj, protoname+"Proto")
                self.proto = class_()
                return setval(self.proto, **kwargs)
        raise Exception('invalid protoname')

enumDict_ = dict()

#get all enum type list in the modules
for module_obj in MODULE_LIST:
    for enumtype in module_obj.DESCRIPTOR.enum_types_by_name:
        tempDict = enumDict_[enumtype] = dict()
        for name in getattr(module_obj, enumtype).DESCRIPTOR.values_by_name:
            tempDict[name[1:].lower()] = getattr(module_obj, name)

def make_function(enumtype):
    def _function(key):
        return enumDict_[enumtype][key]
    return _function

current_module = sys.modules[__name__]

#def all the enumtypes
for module_obj in MODULE_LIST:
    for enumtype in module_obj.DESCRIPTOR.enum_types_by_name:
        setattr(current_module, "enum"+enumtype, make_function(enumtype))
