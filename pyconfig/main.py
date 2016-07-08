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

from .version import __version__ as PYCONFIG_VERSION
import os
import sys
import argparse
from .Interpreter import Consumer
from .Graph import Searcher
from .Graph import Grapher
from .Helpers.Logger import Logger
from .Serializer import Serializer
from .Analyzer import Engine

# Main
def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='pyconfig is a tool to generate xcconfig files from a simple DSL')
    parser.add_argument(
        '--version',
        help='Displays the version information',
        action='version',
        version=PYCONFIG_VERSION
    )
    parser.add_argument(
        'file',
        metavar='<path>', 
        help='Path to the pyconfig file to use to generate a xcconfig file',
    )
    parser.add_argument(
        '--no-analyze',
        help='Skips the step of analyzing the pyconfig files before writing to disk',
        default=False,
        action='store_true'
    )
    parser.add_argument(
        '--scheme', 
        metavar='name',
        action='store',
        help='Optional argument to supply the scheme name'
    )
    parser.add_argument(
        '--quiet',
        help='Silences all logging output',
        default=False,
        action='store_true'
    )
    parser.add_argument(
        '--dry-run',
        help='Runs normally except will not write out a file',
        default=False,
        action='store_true'
    )
    parser.add_argument(
        '--verbose',
        help='Adds verbosity to logging output',
        default=False,
        action='store_true'
    )
    args = parser.parse_args(argv)

    Logger.isVerbose(args.verbose)
    Logger.isSilent(args.quiet)
    
    found_pyconfig_files = Searcher.locateConfigs(args.file)
    
    parsed_configs = Consumer.CreateGraphNodes(found_pyconfig_files)
    
    for node in parsed_configs:
        node.resolvePaths(parsed_configs)
    mapped_nodes = Grapher.TraverseNodes(parsed_configs)
    
    analyzer_engine = Engine.Engine()
    for current_config in mapped_nodes:
        if not args.no_analyze:
            analyzer_engine.process(current_config)
        if not args.dry_run:
            Serializer.writeFile(current_config, args.scheme)

if __name__ == "__main__": # pragma: no cover
    main()