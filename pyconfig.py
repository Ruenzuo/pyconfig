#!/usr/bin/python

# Copyright (c) 2016, Samantha Marshall (http://pewpewthespells.com)
# All rights reserved.
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

import argparse
import pyparsing

# build setting Word definition
setting_body = pyparsing.alphanums + '_'
setting_start = pyparsing.alphas
build_setting_name = pyparsing.Word(setting_start, setting_body)

# build configuration Word definition
configutation_body = pyparsing.alphanums + '_'
configuration_start = pyparsing.alphas
build_configuration_name = pyparsing.Word(configuration_start, configutation_body) ^ pyparsing.Word("*")

# parsing conditional statement expressions
conditional_expr = pyparsing.Group(pyparsing.Word(pyparsing.alphas) + pyparsing.Suppress('=') + pyparsing.Word(pyparsing.alphanums+'*\"\'_-'))
conditional_name = pyparsing.Group(pyparsing.delimitedList(conditional_expr, 'and'))

# keywords
setting_keyword = 'setting'
use_keyword = 'use'
for_keyword = 'for'
if_keyword = 'if'
include_keyword = 'include'
inherits_keyword = 'inherits'
open_brace = '{'
close_brace = '}'

def processFile(should_lint=True, pyconfig_contents="", output_file=None, scheme_name=None):

    # by default we want to suppress keywords, except when linting a file, then we want to make sure they are correctly placed
    ParseMethod = pyparsing.Suppress
    if should_lint == True:
        ParseMethod = pyparsing.Keyword

    # Parser Definitions

    # include "other.xcconfig" # with optional trailing comment
    include_parser = ParseMethod(include_keyword) + pyparsing.dblQuotedString + pyparsing.Suppress(pyparsing.ZeroOrMore(pyparsing.pythonStyleComment))

    # group( comma, separated, values, to be used as assignment, for build configurations )
    bc_value_parser = pyparsing.Group(pyparsing.Optional(pyparsing.commaSeparatedList))

    # 
    if_value_parser = pyparsing.Word(pyparsing.alphanums)

    #
    if_cond_parser = pyparsing.Keyword(if_keyword) + conditional_name + pyparsing.Optional(ParseMethod(open_brace) + if_value_parser + ParseMethod(close_brace))

    #
    for_bc_parser = pyparsing.Keyword(for_keyword) + build_configuration_name + pyparsing.Optional(ParseMethod(open_brace) 
        + bc_value_parser 
        + ParseMethod(close_brace))

    #
    values_parser = pyparsing.delimitedList(pyparsing.Group(for_bc_parser), pyparsing.Empty()) ^ pyparsing.delimitedList(pyparsing.Group(if_cond_parser), pyparsing.Empty())

    #
    setting_parser = pyparsing.Group(pyparsing.Suppress(pyparsing.ZeroOrMore(pyparsing.pythonStyleComment)) + ParseMethod(setting_keyword)
        + build_setting_name 
        + pyparsing.Group(pyparsing.Optional(pyparsing.Keyword(use_keyword) + build_setting_name) + pyparsing.Optional(pyparsing.Keyword(inherits_keyword)))
        + ParseMethod(open_brace) 
        + pyparsing.Group(values_parser) 
        + ParseMethod(close_brace))

    #
    config_parser = pyparsing.Suppress(pyparsing.ZeroOrMore(pyparsing.pythonStyleComment)) + pyparsing.Optional(pyparsing.delimitedList(include_parser, pyparsing.Empty())) + pyparsing.delimitedList(setting_parser, pyparsing.Empty())

    # now parse the file's contents
    results = config_parser.parseString(pyconfig_contents)

    if should_lint == False:
        output_file.write('// Generated by pyconfig\n')
        
        # if the scheme name was defined as part of the passed arguments then declare a new variable with that name as part of the xcconfig
        if scheme_name != None:
            output_file.write('SCHEME_NAME = ' + scheme_name + '\n')
        
        for setting in results:
            # if the resulting object is a plain string, then this was one of the parsed include statements
            if type(setting) == str:
                output_file.write('#include ' + setting + '\n')
            
            # if the resulting object is a parsed result from pyparsing, this is one of the build setting definitions
            if type(setting) == pyparsing.ParseResults:
                inherited_settings = ''
                base_setting_name = setting[0]
                uses_configuration_specific_settings = False
                substitution_variable_name = 'CONFIGURATION'
                configurations = setting[2]
                if len(setting[1]) > 0:
                    modifiers = setting[1]
                    if modifiers[0] == use_keyword:
                        substitution_variable_name = modifiers[1]
                    if modifiers[0] == inherits_keyword:
                        inherited_settings = '$(inherited) '
                    if len(modifiers) == 3:
                        if modifiers[2] == inherits_keyword:
                            inherited_settings = '$(inherited) '
                for configuration in configurations:
                    configuration_type = configuration[0]
                    if configuration_type == for_keyword:
                        configuration_name = configuration[1]
                        configuration_value_string = ''
                        if len(configuration) > 2:
                            configuration_value_string = ' '.join(configuration[2])
                        if configuration_name.startswith('*', 0, 1):
                            configuration_name = ''
                        else:
                            uses_configuration_specific_settings = True
                            configuration_name = '_'+configuration_name
                        output_file.write(base_setting_name + configuration_name + ' = ' + inherited_settings + configuration_value_string + '\n')
                    if configuration_type == if_keyword:
                        conditions = configuration[1]
                        assignment_value = configuration[2]
                        conditional_key_value_list = list()
                        for condition in conditions:
                            conditional_key_value_list.append('='.join(condition))
                        conditional_key_value_string = ','.join(conditional_key_value_list)
                        output_file.write(base_setting_name + '[' + conditional_key_value_string + '] = ' + inherited_settings + assignment_value + '\n')
                if uses_configuration_specific_settings:
                    output_file.write(base_setting_name + ' = ' + inherited_settings + '$(' + base_setting_name + '_$(' + substitution_variable_name + '))' + '\n')

# Main
parser = argparse.ArgumentParser(description='pyconfig is a tool to generate xcconfig files from a simple DSL that makes ')
parser.add_argument('file', help='Path to the pyconfig file to use to generate a xcconfig file', type=argparse.FileType('r'))
parser.add_argument('-o', '--output', metavar='file', help='Path to output xcconfig file to write', type=argparse.FileType('w'))
parser.add_argument('-l', '--lint', help='Validate the syntax of a pyconfig file', action='store_true')
parser.add_argument('-s', '--scheme', metavar='name', help='Optional argument to supply the scheme name')
args = parser.parse_args()
	
pyconfig_contents = args.file.read()

processFile(args.lint, pyconfig_contents, args.output, args.scheme)
	
args.file.close()
	
if args.output != None:
    args.output.close()