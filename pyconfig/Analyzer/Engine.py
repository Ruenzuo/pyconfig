# Copyright (c) 2016, Samantha Marshall (http://pewpewthespells.com)
# All rights reserved.
#
# https://github.com/samdmarshall/pyconfig
# 
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
# 
# 1. Redistributions of source code must retain the above copyright notice, this 
# list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
# 
# 3. Neither the name of Samantha Marshall nor the names of its contributors may 
# be used to endorse or promote products derived from this software without 
# specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
# OF THE POSSIBILITY OF SUCH DAMAGE.

from ..Settings import TypeConstants
from ..Settings import Builtin
from ..Settings import Runtime
from ..Keyword import SettingKeyword
from ..Helpers.Logger import Logger

def findPreviousDefinition(kv_array, index, setting_key):
    previous_definition_indexes = []
    for idx, (key, value) in kv_array[:index]:
        setting_values = list(value.keys())
        if setting_key in setting_values:
            previous_definition_indexes.append(idx)
        
    return previous_defintion_indexes

def findDuplicates(dictionary):
    results = {}
    
    settings_set = set()
    snapshot_of_dict = list(dictionary.items())
    for key, value in snapshot_of_dict:
        setting_values = list(value.keys())
        duplicates = settings_set.intersection(setting_values)
        if len(duplicates):
            current_index = snapshot_of_dict.index((key, value))
            for item in duplicates:
                previous_definitions = findPreviousDefinition(snapshot_of_dict, current_index, item)
                previous_definitions.append(current_index)
                results[item] = previous_definitions
    snapshot_of_results = list(results.items())
    for key, value in snapshot_of_results:
        file_names = []
        for index in value:
            configuration = snapshot_of_dict[index]
            file_names.append(configuration.name)
        results[key] = file_names
    return results

class Engine(object):
    
    def __init__(self):
        # accessing the lookup tables
        self.__type_table = TypeConstants.ConstantLookupTable
        self.__builtin_table = Builtin.BuiltinLookupTable
        self.__runtime_table = Runtime.RuntimeLookupTable
        self.__namespace_table = {}
    
    def process(self, configuration):
        Logger.write().info('Analyzing %s ...' % configuration.name)
        self.__namespace_table[configuration.name] = {}
        for item in configuration.config:
            if type(item) is SettingKeyword.SettingKeyword:
                self.__namespace_table[configuration.name][item.build_setting_name] = item
        duplicate_results = findDuplicates(self.__namespace_table)
        for key, value in list(duplicate_results.items()):
            Logger.write().warning('Found duplicate defintion for "%s" in files: %s' % (key, str(value)))