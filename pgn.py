# -*- coding:utf-8 -*-
# Copyright (c) 2011 Renato de Pontes Pereira, renato.ppontes at gmail dot com
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE.

import re

'''
A simple PGN parser.

PGN (Portable Game Notation) is computer-processible format for recording chess
games, both the moves and related data. 

This module is based on features of others parser modules (such json and yaml).
The basic usage::

    import pgn

    pgn_text = open('morphy.pgn).read()
    pgn_game = pgn.PGNGame()

    print pgn.loads(pgn_text) # Returns a list of PGNGame
    print pgn.dumps(pgn_game) # Returns a string with a pgn game

'''

class PGNGame(object):
    '''
    Describes a single chess game in PGN format.
    '''

    TAG_ORDER = ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Result',
                 'Annotator', 'PlyCount', 'TimeControl', 'Time', 'Termination',
                 'Mode', 'FEN']

    def __init__(self, event=None, site=None, date=None, round=None, 
                                                         white=None,
                                                         black=None,
                                                         result=None):
        '''
        Initializes the PGNGame, receiving the requireds tags.
        '''
        self.event = event
        self.site = site
        self.date = date
        self.round = round
        self.white = white
        self.black = black
        self.result = result
        self.annotator = None
        self.plycount = None
        self.timecontrol = None
        self.time = None
        self.termination = None
        self.mode = None
        self.fen = None

        self.moves = []
    
    def dumps(self):
        return dumps(self)

    def __repr__(self):
        return '<PGNGame "%s" vs "%s">' % (self.white, self.black)

class GameStringIterator(object):
    """
        Iterator containing multiline strings
        that represent games from a PGN file
    """

    def __init__(self, file_name):
        """
            Args:
                file_name (str): PGN file name
        """
        self.file_name = file_name
        self.file_iter = iter(open(self.file_name))
        self.game_lines = []
        self.end = False

    def __iter__(self):
        """doc"""
        return self

    def next(self):
        """doc"""
        if self.end is True:
            raise StopIteration
        try:
            while True:
                line = self.file_iter.next()
                if line.startswith("[Event"):
                    if len(self.game_lines) == 0:
                        self.game_lines.append(line)
                        continue
                    else:
                        game_lines = self.game_lines[:]
                        self.game_lines = []
                        self.game_lines.append(line)
                        game_str = "".join(game_lines)
                        return game_str
                else:
                    self.game_lines.append(line)
        except StopIteration:
            game_lines = self.game_lines[:]
            game_str = "".join(game_lines)
            self.end = True
            return game_str

class GameIterator(object):
    """
        Iterator containing games from a PGN file
    """

    def __init__(self, file_name):
        """
            Args:
                file_name (str): PGN file name
        """
        self.game_str_iterator = GameStringIterator(file_name)

    def __iter__(self):
        """doc"""
        return self

    def next(self):
        """doc"""
        for game_str in self.game_str_iterator:
            game = loads(game_str)[0]
            return game

def _pre_process_text(text):
    '''
    This function is responsible for removal of end line commentarys 
    (;commentary), blank lines and aditional spaces. Also, it converts 
    ``\\r\\n`` to ``\\n``.
    '''
    text = re.sub(r'\s*(\\r)?\\n\s*', '\n', text.strip())
    lines = []
    for line in text.split('\n'):
        line = re.sub(r'(\s*;.*|^\s*)', '', line)
        if line:
            lines.append(line)
    
    return lines

def _next_token(lines):
    '''
    Get the next token from lines (list of text pgn file lines).

    There is 2 kind of tokens: tags and moves. Tags tokens starts with ``[``
    char, e.g. ``[TagName "Tag Value"]``. Moves tags follows the example: 
    ``1. e4 e5 2. d4``.
    '''
    if not lines:
        return None

    token = lines.pop(0).strip() 
    if token.startswith('['):
        return token

    while lines and not lines[0].startswith('['):
        token += ' '+lines.pop(0).strip()
    
    return token.strip()

def _parse_tag(token):
    '''
    Parse a tag token and returns a tuple with (tagName, tagValue).
    '''
    tag, value = re.match(r'\[(\w*)\s*(.+)', token).groups()
    return tag.lower(), value.strip('"[] ')

def _parse_moves(token):
    '''
    Parse a moves token and returns a list with moviments
    '''
    moves = []
    while token:
        token = re.sub(r'^\s*(\d+\.+\s*)?', '', token)

        if token.startswith('{'):
            pos = token.find('}')+1
        else:
            pos1 = token.find(' ')
            pos2 = token.find('{')
            if pos1 <= 0:
                pos = pos2
            elif pos2 <= 0:
                pos = pos1
            else:
                pos = min([pos1, pos2])

        if pos > 0:
            moves.append(token[:pos])
            token = token[pos:]
        else:
            moves.append(token)
            token = ''
    
    return moves

def loads(text):
    '''
    Converts a string ``text`` into a list of PNGGames
    '''
    games = []
    game = None
    lines = _pre_process_text(text)

    while True:
        token = _next_token(lines)

        if not token:
            break

        if token.startswith('['):
            tag, value = _parse_tag(token)
            if not game or (game and game.moves):
                game = PGNGame()
                games.append(game)

            setattr(game, tag, value)
        else:
            game.moves = _parse_moves(token)
    
    return games

def dumps(games):
    '''
    Serialize a list os PGNGames (or a single game) into text format.
    '''
    all_dumps = []

    if not isinstance(games, (list, tuple)):
        games = [games]

    for game in games:
        dump = ''
        for i, tag in enumerate(PGNGame.TAG_ORDER):
            if getattr(game, tag.lower()):
                dump += '[%s "%s"]\n' % (tag, getattr(game, tag.lower()))
            elif i <= 6:
                dump += '[%s "?"]\n' % tag

        
        dump += '\n'
        i = 0
        for move in game.moves:
            if not move.startswith('{'):
                if i%2 == 0:
                    dump += str(int(i/2)+1)+'. '
                
                i += 1

            dump += move + ' '
            
        all_dumps.append(dump.strip())
            
    return '\n\n\n'.join(all_dumps)
