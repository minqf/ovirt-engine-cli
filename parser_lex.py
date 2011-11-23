# cli.parser_lex.py. This file automatically created by PLY (version 3.4). Don't edit!
_tabversion   = '3.4'
_lextokens    = {'GT': 1, 'LTLT': 1, 'STRING': 1, 'HEREDOC': 1, 'NEWLINE': 1, 'BANG': 1, 'PIPE': 1, 'LT': 1, 'SHELL': 1, 'MARKER': 1, 'WORD': 1, 'GTGT': 1, 'OPTION': 1}
_lexreflags   = 0
_lexliterals  = '=;'
_lexstateinfo = {'heredoc1': 'inclusive', 'heredoc2': 'exclusive', 'INITIAL': 'inclusive', 'shell': 'exclusive'}
_lexstatere   = {'heredoc1': [('(?P<t_heredoc1_MARKER>[a-zA-Z0-9_-]+)|(?P<t_heredoc1_NEWLINE>\\n)', [None, ('t_heredoc1_MARKER', 'MARKER'), ('t_heredoc1_NEWLINE', 'NEWLINE')]), ('(?P<t_STRING>(?s)("([^"\\\\]|\\\\.)*"|\'[^\']\'))|(?P<t_LTLT><<)|(?P<t_BANG>!)|(?P<t_PIPE>\\|)|(?P<t_NEWLINE>\\n)|(?P<t_OPTION>-(-[a-zA-Z_][a-zA-Z0-9_]*)+)|(?P<t_WORD>[^ \\n\\t"\\\'<>|!\\\\#;]+)|(?P<t_ignore_quoted_newline>\\\\\\n)|(?P<t_ignore_comment>\\#.*)|(?P<t_GTGT>>>)|(?P<t_LT><)|(?P<t_GT>>)', [None, ('t_STRING', 'STRING'), None, None, ('t_LTLT', 'LTLT'), ('t_BANG', 'BANG'), ('t_PIPE', 'PIPE'), ('t_NEWLINE', 'NEWLINE'), (None, 'OPTION'), None, (None, 'WORD'), (None, None), (None, None), (None, 'GTGT'), (None, 'LT'), (None, 'GT')])], 'heredoc2': [('(?P<t_heredoc2_HEREDOC>.*\\n)', [None, ('t_heredoc2_HEREDOC', 'HEREDOC')])], 'INITIAL': [('(?P<t_STRING>(?s)("([^"\\\\]|\\\\.)*"|\'[^\']\'))|(?P<t_LTLT><<)|(?P<t_BANG>!)|(?P<t_PIPE>\\|)|(?P<t_NEWLINE>\\n)|(?P<t_OPTION>-(-[a-zA-Z_][a-zA-Z0-9_]*)+)|(?P<t_WORD>[^ \\n\\t"\\\'<>|!\\\\#;]+)|(?P<t_ignore_quoted_newline>\\\\\\n)|(?P<t_ignore_comment>\\#.*)|(?P<t_GTGT>>>)|(?P<t_LT><)|(?P<t_GT>>)', [None, ('t_STRING', 'STRING'), None, None, ('t_LTLT', 'LTLT'), ('t_BANG', 'BANG'), ('t_PIPE', 'PIPE'), ('t_NEWLINE', 'NEWLINE'), (None, 'OPTION'), None, (None, 'WORD'), (None, None), (None, None), (None, 'GTGT'), (None, 'LT'), (None, 'GT')])], 'shell': [('(?P<t_shell_SHELL>.*(?<!\\\\)\\n)', [None, ('t_shell_SHELL', 'SHELL')])]}
_lexstateignore = {'shell': ' \t', 'heredoc2': ' \t', 'INITIAL': ' \t', 'heredoc1': ' \t'}
_lexstateerrorf = {'heredoc1': 't_error', 'heredoc2': 't_error', 'shell': 't_error', 'INITIAL': 't_error'}
