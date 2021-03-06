import const
import base_player
from random import randint

class Player(base_player.BasePlayer):

    def __init__(self):
        base_player.BasePlayer.__init__(self)
        self._playerName = "DominusFloodFill"
        self._playerYear = "1"
        self._version = "Alpha"
        self._playerDescription = "\"Dominus\" is Latin for Master. Good luck.\nBy Charles Pigott and Nathan van Doorn"

        self._moves = [] # Our previous moves

    def getRandPiece(self):
        """
        Get a random piece on the board.
        """

        row = randint(0, 11)
        # Board is a weird L shape
        col = randint(0, 5 if row < 6 else 11)
        # Return move in row (letter) + col (number) grid reference
        # e.g. A3 is represented as 0,2
        return (row, col)

    def isValidCell(self, cell):
        """
        Check that a generated cell is valid on the board.
        """

        assert(type(cell) == tuple)
        if cell[0] < 0  or cell[1] < 0:  return False
        if cell[0] > 11 or cell[1] > 11: return False
        if cell[0] < 6 and cell[1] > 5:  return False
        return True

    def getRotationFactor(self, rotation, i):
        if rotation == 0:
            return i
        if rotation == 1:
            return (i[1], i[0])
        if rotation == 2:
            return (-i[0], -i[1])
        if rotation == 3:
            return (i[1], -i[0])
        raise IndexError # It's sort of an index error

    def circleCell(self, piece):
        """
        Rotate around a particular cell on the board.
        """
        assert(type(piece) == tuple)
        rotate = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        return [(piece[0] + offset[0], piece[1] + offset[1]) for offset in rotate]

    def makeShip(self, base, shape):
        rotation = randint(0, 3)
        successful = []
        for coord in shape:
            rotFact = self.getRotationFactor(rotation, coord)
            actual = (rotFact[0] + base[0], rotFact[1] + base[1])
            success = True
            success = success and self.isValidCell(actual)
            success = success and self._playerBoard[actual[0]][actual[1]] == const.EMPTY
            if not success: return False

            # Try not to connect ships together
            count = 0
            for cell in self.circleCell(actual):
                success = success and (not self.isValidCell(cell) or
                                       cell in successful or
                                       self._playerBoard[cell[0]][cell[1]] == const.EMPTY)
                count += 1

            # Don't bother trying to separate ships if it's too hard
            if not success and count < 200: return False

            successful.append(actual)
        for coord in successful:
            self._playerBoard[coord[0]][coord[1]] = const.OCCUPIED
        return True

 

    def deployFleet(self):
        """
        Decide where you want your fleet to be deployed, then return your board.
        The attribute to be modified is _playerBoard. You can see how it is defined
        in the _initBoards method in the file base_player.py
        """
        self._initBoards()

        # Reset moves each game
        self._moves = []

        self.shapes = [
            frozenset([(-1,  0), (0,  0), (0, -1), (0, 1), (1, -1), (1, 1)]), # Hovercraft
            frozenset([(-1, -1), (1, -1), (0, -1), (0, 0), (0,  1), (0, 2)]), # Aircraft Carrier
            frozenset([( 0,  0), (0,  1), (0,  2), (0, 3)]), # Battleship
            frozenset([( 0,  0), (0,  1), (0,  2)]), # Cruiser
            frozenset([( 0,  0), (1,  0)]) # Destroyer
        ]

        for ship in self.shapes:
            while True:
                sp = self.getRandPiece()
                if self.makeShip(sp, ship):
                    break

        return self._playerBoard

    def countPossibilities(self, coord, shape, isEmpty):
        """
        Count the number of possible ways the given shape could overlap with
        the given coordinate
        """
        count = 0
        for rotation in xrange(4):
            for offset in [self.getRotationFactor(rotation, cell) for cell in shape]:
                valid = True
                for cell in shape:
                    x = coord[0] - offset[0] + cell[0]
                    y = coord[1] - offset[1] + cell[1]
                    valid = valid and (self.isValidCell((x, y)) and
                            isEmpty(self._opponenBoard[x][y]))
                    if not valid:
                        break
                if valid:
                    count += 1
        return count

    def analyzeHitRegion(self, ps):
        def findAnswer(remPoints, toTestShips, toDelShips):
            if toTestShips and remPoints:
                thisShip0 = toTestShips.pop()

                res = [(remPoints, toTestShips[:], toDelShips[:])]
                    
                for direction in range(4):
                    thisShip = {self.getRotationFactor(direction, toRot) for toRot in thisShip0}

                    for point in remPoints:
                        for offset in thisShip:
                            willBeTaken = {(point[0] - offset[0] + p[0], point[1] - offset[1] + p[1]) for p in thisShip}

                            if willBeTaken <= remPoints:
                                nextToDelShips = toDelShips[:]
                                nextToDelShips.append(thisShip0)
                                res.append((remPoints - willBeTaken, toTestShips, nextToDelShips))
                return [fin for n in res for fin in findAnswer(n[0], n[1], n[2])]

            elif toTestShips and not remPoints:
                return [toDelShips]

            elif not toTestShips and remPoints:
                return []
            else:
                return [toDelShips]

        ans = findAnswer(ps, self.shapes[:], [])
        return ans[0]

    def chooseMove(self):
        """
        Decide what move to make based on current state of opponent's board and return it
        """
        decMv = (-1, -1)

        hitRegion = {x[0] for x in reversed(self._moves) if x[1] == const.HIT}

        if hitRegion:
            # Check previous moves for unchecked cells
            for decMv in [c for x in hitRegion for c in self.circleCell(x)]:
                if self.isValidCell(decMv) and self._opponenBoard[decMv[0]][decMv[1]] == const.EMPTY:
                    return decMv

            # Otherwise stop looking for those shapes
            for toDel in self.analyzeHitRegion(hitRegion):
                self.shapes.remove(toDel)

            # Reset _moves because we've checked all the hits we care about.
            self._moves = []

        # Failing that, it's probability distribution time.
        bestProb = 0
        for x in range(12):
            for y in range(len(self._opponenBoard[x])):
                thisProb = 0
                for shape in self.shapes:
                    thisProb += self.countPossibilities((x, y), shape,
                            lambda x: x == const.EMPTY)
                if thisProb > bestProb:
                    bestProb = thisProb
                    decMv = (x, y)


        # Failing that, get a random cell (in a diagonal pattern)
        count = 0
        while (not self.isValidCell(decMv) or
                self._opponenBoard[decMv[0]][decMv[1]] != const.EMPTY):
            decMv = self.getRandPiece()
            if count < 50 and (decMv[0] + decMv[1]) % 2 != 0:
                decMv = (-1, -1)

        assert(self.isValidCell(decMv) and
                self._opponenBoard[decMv[0]][decMv[1]] == const.EMPTY)
        return decMv

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
        self._opponenBoard[row][col] = Outcome
        self._moves.append(((row, col), Outcome))

    def getOpponentMove(self, row, col):
        """
        You might like to keep track of where your opponent
        has missed, but here we just acknowledge it. Note case A3 is
        represented as row = 0, col = 2.
        """
        if ((self._playerBoard[row][col] == const.OCCUPIED)
            or (self._playerBoard[row][col] == const.HIT)):
            # They may (stupidly) hit the same square twice so we check for occupied or hit
            self._playerBoard[row][col] = const.HIT
            result = const.HIT
        else:
            # You might like to keep track of where your opponent has missed, but here we just acknowledge it
            result = const.MISSED
        return result


def getPlayer():
    """ MUST NOT be changed, used to get a instance of your class."""
    return Player()
