class Board:
    # scanner for general use. not a variable
    # public static Scanner scan = System.in ();
    # private char first;
    # private char second;

    # private int rows;
    # private int cols;
    # first are rows, second are columns
    # private char[][] board;


    def __init__(self, first, second, row, col):

        self.__first = first
        self.__second = second
        char[][] board = char[row][col]
        self.board = board
        rows = row
        cols = col
        for i in range(rows):
            for  j in range(cols):
                board[i][j] = ' '

    def move(self, player, column):
        move = False
        while not move:
            for (int i = rows - 1; i >= 0; i--):
                if (getSpot(i, column) == ' '):
                    board[i][column] = player
                    return
        column = readInt("That column is full. Pick a different one.");



    def getSpot(row, column):
        if column >= cols or row >= rows or column < 0 or row < 0:
            return '?'
        return board[row][column]


    def getSpace(self, row, col):
        if self.board[row][col] == first:
            return "The First player has this space."

        elif self.board[row][col] == second:
            return "The Second player has this space."
        else:
            return "No-one has this space."



    def boardFull(self):
        taken = 0
        for i in range(cols):
            if board[0][i] != ' ':
                taken += 1;
        if taken == cols:
            return True
        else:
            return False

    def readLine(output):
        return input(output)


    public static int readInt(String output)
        System.out.println(output);
        return readInt();

    public static int readInt()
        int num = 0
        boolean parsed = false
        while (!parsed)
            boolean input = false
            String inp = readLine()

            while (inp.length() == 0)
                in = readLine()
            num = 0

            try:
            {
                num = Integer.parseInt(in)
                parsed = true
            catch(NumberFormatException ex)
            {
                print("Thats not a valid number! Try again!")
                parsed = False
        return num

    public int rows():
        return rows

    def cols():
        return cols

    def __str__(self):
        return "rows: " + str(rows) + " columns: " + str(cols)
