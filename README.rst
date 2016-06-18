==========
PGN Parser
==========

A simple python PGN parser.

PGN (Portable Game Notation) is computer-processible format for recording chess
games, both the moves and related data. 

This module is based on features of others python parser modules (such json and 
yaml). The basic usage::

    import pgn

    pgn_text = open('morphy.pgn').read()
    pgn_game = pgn.PGNGame()

    print pgn.loads(pgn_text) # Returns a list of PGNGame
    print pgn.dumps(pgn_game) # Returns a string with a pgn game

**Note**:

The above basic example doesn't work properly with huge files (hundreds of
megabytes and more): reading the whole file at once is slow and uses much
memory, pgn.loads(big_string) uses even more memory.

To process huge PGN files, do it like this::

    import pgn

    for game in pgn.GameIterator("bigfile.pgn"):
        print game  # or do something else with it

**Features**:

- Required tags: "Event", "Site", "Date", "Round", "White", "Black", and
  "Result".
- Optional tags: "Annotator", "PlyCount", "TimeControl", "Time", "Termination", 
  "Mode", and "FEN".
- Commentaries: "**;**" (a comment that continues to the end of the line) and 
  "**{**" (which continues until a matching "**}**"). The last one just in 
  moves list.


**PGN example**::

    [Event "F/S Return Match"]
    [Site "Belgrade, Serbia Yugoslavia|JUG"]
    [Date "1992.11.04"]
    [Round "29"]
    [White "Fischer, Robert J."]
    [Black "Spassky, Boris V."]
    [Result "1/2-1/2"]
     
    1. e4 e5 2. Nf3 Nc6 3. Bb5 {This opening is called the Ruy Lopez.} 3... a6
    4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8  10. d4 Nbd7
    11. c4 c6 12. cxb5 axb5 13. Nc3 Bb7 14. Bg5 b4 15. Nb1 h6 16. Bh4 c5 17. dxe5
    Nxe4 18. Bxe7 Qxe7 19. exd6 Qf6 20. Nbd2 Nxd6 21. Nc4 Nxc4 22. Bxc4 Nb6
    23. Ne5 Rae8 24. Bxf7+ Rxf7 25. Nxf7 Rxe1+ 26. Qxe1 Kxf7 27. Qe3 Qg5 28. Qxg5
    hxg5 29. b3 Ke6 30. a3 Kd6 31. axb4 cxb4 32. Ra5 Nd5 33. f3 Bc8 34. Kf2 Bf5
    35. Ra7 g6 36. Ra6+ Kc5 37. Ke1 Nf4 38. g3 Nxh3 39. Kd2 Kb5 40. Rd6 Kc5 41. Ra6
    Nf2 42. g4 Bd3 43. Re6 1/2-1/2
