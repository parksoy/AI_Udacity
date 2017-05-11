#still one set of twins left.
#Working pieces. Need to add Diagonal and nakedTwins

rows = 'ABCDEFGHI'
cols = '123456789'

assignments = []

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]


#Adding diagonal sudoku
diagonal1_units = [[rows[i]+cols[i] for i in range(len(rows))]]
diagonal2_units = [[rows[i]+cols[::-1][i] for i in range(len(rows))]]

isDiagonal = 1 #0 for non-diagonal sudoku, 1 for diagonal sudoku
if isDiagonal == 1:
    unitlist = row_units + column_units + square_units + diagonal1_units + diagonal2_units
else:
    unitlist = row_units + column_units + square_units

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args: grid(string) - A grid in string form.
    Returns: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    values = []
    all_digits = '123456789'
    for c in grid:
        if c == '.':
            values.append(all_digits)
        elif c in all_digits:
            values.append(c)
    assert len(values) == 81
    return dict(zip(boxes, values))

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.
    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.
    Args:values: Sudoku in dictionary form.
    Returns:Resulting Sudoku in dictionary form after eliminating values.
    """
    solved_values=[box for box in values.keys() if len(values[box])==1]
    for box in solved_values:
        digit=values[box]
        for peer in peers[box]:
            values[peer]=values[peer].replace(digit,'')
    return values

def only_choice(values):
    '''Finalize all values that are the only choice for a unit.
    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.
    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    '''
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    all_two = set([box for box in values.keys() if len(values[box]) == 2])
    naked_twins = [[box1,box2] for box1 in all_two \
                               for box2 in peers[box1] \
                    if set(values[box1])==set(values[box2]) ]

    #print("len(naked_twins)=",len(naked_twins))
    #print("naked_twins=",naked_twins)
    if len(naked_twins)!=0:
        #display(values)
        # Eliminate the naked twins as possibilities for their peers
        for i in range(len(naked_twins)):
            box1 = naked_twins[i][0]
            box2 = naked_twins[i][1]
            #print("box1",box1,values[box1],"\nbox2",box2,values[box2])
            if box1[0]==box2[0]:
                common_unit=box1[0]
                common_unit_peers= set(cross(common_unit, cols))-set(naked_twins[i])
            elif box1[1]==box2[1]:
                common_unit=box1[1]
                common_unit_peers= set(cross(rows, common_unit))-set(naked_twins[i])
            elif box1 in diagonal1_units[0] and box2 in diagonal1_units[0]:
                common_unit_peers=set(diagonal1_units[0])-set(naked_twins[i])
            elif box1 in diagonal2_units[0] and box2 in diagonal2_units[0]:
                common_unit_peers=set(diagonal2_units[0])-set(naked_twins[i])
            elif len([sunit for sunit in square_units if box1 in sunit and box2 in sunit])!=0:
                sunit=[sunit for sunit in square_units if box1 in sunit and box2 in sunit]
                common_unit_peers=set(sunit[0])-set(naked_twins[i])

            #print("common_unit_peers",sorted(common_unit_peers))

            # Delete the two digits in naked twins from all common peers.
            for peer_val in common_unit_peers:
                if len(values[peer_val])>2:
                    for rm_val in values[box1]:
                        values = assign_value(values, peer_val, values[peer_val].replace(rm_val,''))

    else : return values

    return values

def reduce_puzzle(values):
    '''Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    '''
    stalled=False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    "Using depth-first search and propagation, try all possible values."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def solve(grid):
    """Find the solution to a Sudoku grid.
    Args: grid(string): a string representing a sudoku grid.
        Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns: The dictionary representation of the final sudoku grid.
            False if no solution exists.
    """
    values=grid_values(grid)

    print("Given sudoku:")
    display(values)

    '''
    values=eliminate(values)
    print("\nAfter eliminate:")
    display(values)
    print("\nAfter onlychoice:")
    values= only_choice(values)
    display(values)
    print("\nAfter nakedtwins:")
    values= naked_twins(values)
    display(values)
    '''
    '''
    print("\nAfter reduce:")
    values=reduce_puzzle(values) # eliminate, only_choice, naked_twins
    display(values)
    '''

    values=search(values)
    #print("\nAfter search:")
    #display(values)
    #print("\n")

    return values

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    reducegrid= '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
    searchneededgrid = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    testgrid='9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    testgrid2='5.....87.....5.4..9.....25....895....5....9..1.......5...5..............3..1.....'

    display(solve(testgrid2))


    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
