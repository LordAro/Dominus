import const
import base_player
from random import randint

class Player(base_player.BasePlayer):

    
    def __init__(self):
        base_player.BasePlayer.__init__(self)
        self._playerName = "Dominus"
        self._playerYear = "1"
        self._version = "1.0"
        self._playerDescription = "\"Dominus\" is Latin for Master. Good luck."

    def getRandPiece(self):
        """
        Get a random piece on the board.
        """
        row = randint(0,11)
        # Board is a weird L shape
        if row < 6:
            col = randint(0,5)
        else:
            col = randint(0,11)
        # Return move in row (letter) + col (number) grid reference
        # e.g. A3 is represented as 0,2
        return row, col

    # Distribute the fleet onto your board
    def deployFleet(self):
        """
        Decide where you want your fleet to be deployed, then return your board.
        The attribute to be modified is _playerBoard. You can see how it is defined
        in the _initBoards method in the file base_player.py
        """
        self._initBoards()
        # Simple example which always positions the ships in the same place
        # This is a very bad idea! You will want to do something random
        # Destroyer (2 squares)
        self._playerBoard[0][5]=const.OCCUPIED
        self._playerBoard[1][5]=const.OCCUPIED
        # Cruiser (3 squares)
        self._playerBoard[1][1:4]=[const.OCCUPIED]*3
        # Battleship (4 squares)
        self._playerBoard[6][6]=const.OCCUPIED
        self._playerBoard[6][7]=const.OCCUPIED
        self._playerBoard[6][8]=const.OCCUPIED
        self._playerBoard[6][9]=const.OCCUPIED
        # Hovercraft (6 squares)
        self._playerBoard[8][2]=const.OCCUPIED
        self._playerBoard[9][1:4]=[const.OCCUPIED]*3
        self._playerBoard[10][1:4:2]=[const.OCCUPIED]*2
        # Aircraft carrier (6 squares)
        self._playerBoard[9][5:9]=[const.OCCUPIED]*4
        self._playerBoard[8][5]=const.OCCUPIED
        self._playerBoard[10][5]=const.OCCUPIED
        return self._playerBoard

    # Decide what move to make based on current state of opponent's board and print it out
    def chooseMove(self):
        """
        Decide what move to make based on current state of opponent's board and return it 
        # Completely random strategy
        # Knowledge about opponent's board is completely ignored
        """
        return self.getRandPiece()

    def setOutcome(self, entry, row, col):
        """
        entry: the outcome of your shot onto your opponent,
               expected value is const.HIT for hit and const.MISSED for missed.
        row: (int) the board row number (e.g. row A is 0)
        col: (int) the board column (e.g. col 2 is represented by  value 3) so A3 case is (0,2)
        """

        if entry == const.HIT:
            Outcome = const.HIT
        elif entry == const.MISSED:
            Outcome = const.MISSED
        else:
            raise Exception("Invalid input!")
        self._opponenBoard[row][col]=Outcome

    def getOpponentMove(self, row, col):
        """ You might like to keep track of where your opponent
        has missed, but here we just acknowledge it. Note case A3 is
        represented as row = 0, col = 2.
        """
        if ((self._playerBoard[row][col]==const.OCCUPIED)
            or (self._playerBoard[row][col]==const.HIT)):
            # They may (stupidly) hit the same square twice so we check for occupied or hit
            self._playerBoard[row][col]=const.HIT
            result =const.HIT
        else:
            # You might like to keep track of where your opponent has missed, but here we just acknowledge it
            result = const.MISSED
        return result



def getPlayer():
    """ MUST NOT be changed, used to get a instance of your class."""
    return Player()
