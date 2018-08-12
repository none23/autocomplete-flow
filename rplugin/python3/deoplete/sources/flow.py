#!/usr/bin/env python
# coding: utf-8

import os
import re
from .base import Base

CONFIG_FILE = '.flowconfig'

import_re = r'=?\s*require\(["\'"][@?\w\./-]*$|\s+from\s+["\'][@?\w\./-]*$'
import_pattern = re.compile(import_re)


# Find closest configuration directory recursively.
# Borrows from https://github.com/steelsojka/deoplete-flow/pull/9/files
def find_config_dir(dir):
    if CONFIG_FILE in os.listdir(dir):
        return dir
    elif dir == '/':
        return None
    else:
        return find_config_dir(os.path.dirname(dir))


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = 'flow'
        self.mark = '[flow]'
        self.filetypes = ['javascript']
        self.min_pattern_length = 2
        self.rank = 10000
        # self.input_pattern = '((?:\.|(?:,|:|->)\s+)\w*|\()'
        self.input_pattern = (r'\.\w*$|^\s*@\w*$|' + import_re)
        self._relatives = {}
        self._config_dirs = {}
        self.__completer = Completer(vim)

    def on_event(self, context):
        if context['event'] == 'BufRead' or context['event'] == 'BufNewFile':
            try:
                # Cache relative path from closest configuration directory.
                self.relative()
                pass
            except Exception:
                pass

    def get_complete_position(self, context):
        return self.__completer.get_complete_position(context)

    def gather_candidates(self, context):
        rel, cfg_dir = self.relative()
        return self.__completer.find_candidates(context, rel, cfg_dir)

    def relative(self):
        filename = self.vim.eval("expand('%:p')")
        if filename in self._relatives:
            return (self._relatives[filename], self._config_dirs[filename])
        config_dir = find_config_dir(os.path.dirname(filename))
        if not config_dir:
            return (None, None)
        self._relatives[filename] = os.path.relpath(filename, config_dir)
        self._config_dirs[filename] = config_dir
        return (filename, config_dir)


class Completer(object):
    def __init__(self, vim):
        self.__vim = vim

    def on_init(self, context):
        vars = context['vars']
        self.__flowbin = vars.get('autocomplete_flow#flowbin', 'flow')

    def get_complete_position(self, context):
        m = import_pattern.search(context['input'])
        if m:
            # need to tell from what position autocomplete as
            # needs to autocomplete from start quote return that
            return re.search(r'["\']', context['input']).start()

        m = re.search(r'\w*$', context['input'])
        return m.start() if m else -1

    def buildCompletionWord(self, json):

        # If not a function
        if not json['func_details']:
            return json['name']

        return json['name']

        def buildArgumentList(arg):
            index, paramDesc = arg
            return '<`' + str(index) + ':' + paramDesc['name'] + '`>'

            params = map(buildArgumentList, enumerate(json['func_details']['params']))
            return json['name'] + '(' + ', '.join(params) + ')'

    def find_candidates(self, context, relative, config_dir):
        from subprocess import Popen, PIPE
        import json

        line = context['position'][1]
        col = context['complete_position']

        if relative:
            command = [self.__flowbin, 'autocomplete', '--json', relative, line, col]
        else:
            command = [self.__flowbin, 'autocomplete', '--json', line, col]

        buf = '\n'.join(self.__vim.current.buffer[:])

        try:
            process = Popen(command, cwd=config_dir, stdout=PIPE, stdin=PIPE)
            command_results = process.communicate(input=str.encode(buf))[0]

            if process.returncode != 0:
                return []

            results = json.loads(command_results.decode('utf-8'))

            return [{
                'word': self.buildCompletionWord(x),
                'abbr': x['name'],
                'info': x['type'],
                'kind': x['type']} for x in results['result']]
        except FileNotFoundError:
            pass
