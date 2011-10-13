import unittest
import pgn

def game_fixture():
    game = pgn.PGNGame(
        'F/S Return Match',
        'Belgrade, Serbia Yugoslavia|JUG',
        '1992.11.04',
        '29',
        'Fischer, Robert J.',
        'Spassky, Boris V.',
        '1/2-1/2'
    )

    game.annotator = 'Renato'
    game.plycount = '3'
    game.timecontrol = '40/7200:3600'
    game.time = '12:32:43'
    game.termination = 'abandoned'
    game.mode = 'ICS'
    game.fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R1BQKBNR'

    game.moves = ['e4', 'e5', 'd4', 'd5', 'f3', '1/2-1/2']

    return game

PGN_TEXT = '''[Event "F/S Return Match"]
[Site "Belgrade, Serbia Yugoslavia|JUG"]
[Date "1992.11.04"]
[Round "29"]
[White "Fischer, Robert J."]
[Black "Spassky, Boris V."]
[Result "1/2-1/2"]
[Annotator "Renato"]
[PlyCount "3"]
[TimeControl "40/7200:3600"]
[Time "12:32:43"]
[Termination "abandoned"]
[Mode "ICS"]
[FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R1BQKBNR"]

1. e4 e5 2. d4 d5 3. f3 1/2-1/2'''

class PGNGame_Test(unittest.TestCase):
    def test_init(self):
        game = game_fixture()
        assert game.event == 'F/S Return Match'
        assert game.site == 'Belgrade, Serbia Yugoslavia|JUG'
        assert game.date == '1992.11.04'
        assert game.round == '29'
        assert game.white == 'Fischer, Robert J.'
        assert game.black == 'Spassky, Boris V.'
        assert game.result == '1/2-1/2'
        assert game.annotator == 'Renato'
        assert game.plycount == '3'
        assert game.timecontrol == '40/7200:3600'
        assert game.time == '12:32:43'
        assert game.termination == 'abandoned'
        assert game.mode == 'ICS'
        assert game.fen == 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R1BQKBNR'


class PGN_Test(unittest.TestCase):    
    def test_next_token(self):
        '''Tests ``_next_token`` function'''

        lines = [
            '[Site "Belgrade, Serbia Yugoslavia|JUG"]   ',
            '[Date "1234.32.32"]',
            '',
            '1. e4 e5 2. Nf3 Nc6 ',
            '3. Bb5 1-0',
            '   '
        ]

        token = pgn._next_token(lines)
        assert token == '[Site "Belgrade, Serbia Yugoslavia|JUG"]'
        assert len(lines) == 5

        token = pgn._next_token(lines)
        assert token == '[Date "1234.32.32"]'
        assert len(lines) == 4

        token = pgn._next_token(lines)
        assert token == '1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0'
        assert len(lines) == 0

        token = pgn._next_token(lines)
        assert not token
    
    def test_pre_process_text(self):
        '''Tests ``_pre_process_text`` function'''

        text = '''
        [tag "value"] ;comment

        ; commentary
        1. e4 e5 2. d4 d5 ;commentary
        3. f3 1/2-1/2'''

        lines = pgn._pre_process_text(text)
        expt = ['[tag "value"]', '1. e4 e5 2. d4 d5', '3. f3 1/2-1/2']
        assert lines == expt

    def test_parse_tag(self):
        '''Tests ``_parse_tag`` function'''

        token = '[Site "Belgrade, Serbia Yugoslavia|JUG"]'
        tag, value = pgn._parse_tag(token)
        assert tag == 'site'
        assert value == 'Belgrade, Serbia Yugoslavia|JUG'

    def test_parse_moves(self):
        '''Tests ``_parse_moves`` function'''

        token = '1. e4 e5 2. Nf3 Nc6 3. Bb5 1/2-1/2'
        moves = pgn._parse_moves(token)
        assert moves == ['e4', 'e5', 'Nf3', 'Nc6', 'Bb5', '1/2-1/2']

    def test_parse_moves_with_commentary(self):
        '''Tests ``_parse_moves`` function with commentary ({})'''

        token = '{start comment}1. e4{middlecomment}e5 2. {dunno}Nf3 Nc6' +\
                ' 3. Bb5 1/2-1/2{end}'

        moves = pgn._parse_moves(token)
        expected = ['{start comment}', 'e4', '{middlecomment}', 'e5', '{dunno}', 
                    'Nf3', 'Nc6', 'Bb5', '1/2-1/2', '{end}']
        
        assert moves ==  expected

    def test_loads(self):
        '''Tests ``loads`` function'''

        text = '''
        [Site "Belgrade, Serbia Yugoslavia|JUG"]
        [Date "1234.32.32"]

        1. e4 e5 2. Nf3 Nc6 
        3. Bb5 1-0'''

        games = pgn.loads(text)
        assert len(games) == 1

    def test_dumps_single(self):
        '''Tests ``dumps`` function for a single game'''
        game = game_fixture()
        dump = pgn.dumps(game)

        assert dump == PGN_TEXT

    def test_dumps_multi(self):
        '''Tests ``dumps`` function for a list of games'''
        games = [game_fixture(), game_fixture()]
        dump = pgn.dumps(games)

        assert dump == PGN_TEXT+'\n\n\n'+PGN_TEXT
    
    def test_dumps_special(self):
        '''Tests ``dumps`` function with move commentary and null tag'''
        game = pgn.PGNGame('XYZ')
        game.moves = ['{comment}', 'e4', 'e5', '{in}', 'd4', '{lol}', '1-0']

        dump = pgn.dumps(game)
        first_expected = '[Event "XYZ"]\n[Site "?"]'
        last_expected = '{comment} 1. e4 e5 {in} 2. d4 {lol} 1-0'
        
        assert dump.startswith(first_expected)
        assert dump.endswith(last_expected)

if __name__ == '__main__':
    unittest.main()
