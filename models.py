import time
from threading import Thread
import inspect
class CGoL():
    def __init__(self):
        self.board = None
        self.controls = None

    def set_board(self, nboard):
        self.board = nboard
        self.reset(self.board, self.controls)

    def set_controls(self, ncontrol):
        self.controls = ncontrol
        self.reset(self.board, self.controls)

    def reset(self, nboard, controls):
        if not (nboard and controls):
            return None

        #save the board array, and its dimensions
        self.board = nboard
        self.width = len(self.board.boxes[0])
        self.height = len(self.board.boxes)

        #set simulation parameters
        self.duration = controls.duration
        self.speed = controls.speed
        self.step = 0

        self.started = False
        self.paused = False

    def start(self):
        if not self.started:
            self.started = True
            gamethread = Thread(target = self.game, daemon=True)
            gamethread.start()
        elif self.paused:
            self.paused = False

    def pause(self):
        self.paused = True

    def game(self):
        while self.step < self.duration:
            self.move()
            # self.updateview()
            self.step += 1

            #if the game is paused, hold the thread in a loop until it is un-paused
            if self.paused:
                while True:
                    if not self.paused:
                        break
                    time.sleep(0.2)
            #if we're running as normal, wait and loop again
            elif not self.paused:
                time.sleep(self.speed)
        self.reset(self.board, self.controls)


class Naive_CGoL(CGoL):
    """ Basic implementation that uses a brute force approach to updating cells. """
    def __init__(self):
        super().__init__()

    def button_clicked(self, pos):
        """ Action handler for button clicked, which is called by the UI class.
        Unimplemented in this version of CGoL. """
        pass

    def move(self):
        for row in range(len(self.board.boxes)):
            for col in range(len(self.board.boxes[0])):
                n = self.count_neighbors(row, col)
                box = self.board.get_box(row, col)
                box.newstate = (n == 3) or (n == 2 and box.state)

        for row in range(len(self.board.boxes)):
            for col in range(len(self.board.boxes[0])):
                box = self.board.get_box(row, col)
                box.display()

    def count_neighbors(self, row, col):
        """  """
        count = 0
        row_range = range(row - 1, row + 2)
        col_range = range(col - 1, col + 2)
        for i in row_range:
            for j in col_range:
                if i < 0 or j < 0 or i >= self.height or j >= self.width:
                    pass
                elif i == row and j == col:
                    pass
                elif self.board.get_box(i, j).state:
                    count += 1
        return count

    def clear(self):
        pass

class List_CGoL(CGoL):
    """ Implementation that keeps a linked list containing all living cells.
    The idea is that we only check the live cells and their immediate neigbors
    rather than every cell in the grid.
    """
    def __init__(self):
        super().__init__()
        #initialize the linked list
        self.listhead = HeadNode()

    def button_clicked(self, pos):
        """ action handler for when a button is clicked. removes element if it already
            exists, but deletes it if it does not."""
        node = self.search_list(pos)

        if node:
            node.delete()
        else:
            self.listhead.add(pos)

    def search_list(self, target):
        """ Function to search a linked list for a target value and return the
            corresponding node if found. Otherwise returns None """
        node = self.listhead

        while node:
            if target == node.value:
                return node
            else:
                node = node.next
        return None

    def printlist(self):
        print("\nLinked List:")
        node = self.listhead.next
        while node:
            print("\t",node.value)
            node = node.next

    def move(self):
        """ Compute a CGoL single generation """
        node = self.listhead
        while node:
            # skip the head node
            if type(node) is HeadNode:
                node = node.next
                continue
            #check cell and its neigbors that are off
            row, col = node.value
            n = self.check_neighbors(row, col)
            box = self.board.get_box(row, col)
            box.newstate = (n == 3) or (n == 2 and box.state)
            if not box.newstate:
                node.deletetag = True
            node = node.next

        node = self.listhead
        while node:
            if type(node) is HeadNode:
                node = node.next
                continue
            row, col = node.value
            self.board.get_box(row, col).display()
            if node.next and node.deletetag:
                node = node.next
                node.prev.delete()
            elif node.deletetag:
                node.delete()
                node = None
            else:
                node = node.next
        # self.printlist()

    def check_neighbors(self, row, col):
        """ looks at each neighboring cell and determines if it lives. """
        sum = 0
        sum += self.check_cell(row-1, col-1)
        sum += self.check_cell(row  , col-1)
        sum += self.check_cell(row+1, col-1)
        sum += self.check_cell(row-1, col  )
        sum += self.check_cell(row+1, col  )
        sum += self.check_cell(row-1, col+1)
        sum += self.check_cell(row  , col+1)
        sum += self.check_cell(row+1, col+1)
        return sum

    def count_neighbors(self, row, col):
        """ use a brute-force method to count the number of active neigboring cells """
        sum = 0
        sum += self.count_cell(row-1, col-1) #lower left
        sum += self.count_cell(row  , col-1) #left
        sum += self.count_cell(row+1, col-1) #upper-left
        sum += self.count_cell(row-1, col  ) #below
        sum += self.count_cell(row+1, col  ) #above
        sum += self.count_cell(row-1, col+1) #lower-right
        sum += self.count_cell(row  , col+1) #right
        sum += self.count_cell(row+1, col+1) #upper-right
        return sum

    def count_cell(self, row, col):
        if self.inbounds(row, col) and self.board.get_box(row, col).state:
            return 1
        else:
            return 0

    def check_cell(self, row, col):
        """ function to count cells around """
        if not self.inbounds(row,col):
            #If out of bounds, don't check
            return 0

        elif self.board.get_box(row, col).state:
            #If the box is alive, don't check it, but do count it
            return 1

        else:
            #check an empty box
            box = self.board.get_box(row, col)
            if box.newstate != box.state:
                return 0
            n = self.count_neighbors(row, col)
            box.newstate = (n == 3) or (n == 2 and box.state)
            if box.newstate:
                self.listhead.add((row, col))
                # box.changed = True

            return 0


    def inbounds(self, row, col):
        return row != 0 and col != 0 and row < self.height and col < self.width

    def clear(self):
        #iterate through and delete all living boxes.
        while self.listhead.next:
            location = self.listhead.next.value
            box = self.board.get_box(location[0], location[1])
            box.newstate = False
            box.display()
            self.listhead.next.delete()

class Node():
    """ Parent Class for a doubly-linked-list node. """
    def __init__(self, next, prev, value):
        self.prev  = prev
        self.value = value
        self.next  = next

        self.deletetag = False

class HeadNode(Node):
    """ Linked list head node. """
    def __init__(self):
        super().__init__(None, None, None)

    def add(self, value):
        """ creates a new node to be added after the head. """
        #initialize the new node and place it after the head.
        if self.next:
            node = BodyNode(self.next, self, value)
            #Update the previous node's next property to point to the new node
            self.next.prev = node
            self.next = node
            # curframe = inspect.currentframe()
            # calframe = inspect.getouterframes(curframe, 2)
            # print("adding", value, "Caller", calframe[1][3])
        else:
            self.next = BodyNode(None, self, value)

class BodyNode(Node):
    """ Body node for a linked list. """
    def __init__(self, next, prev, value):
        super().__init__(next, prev, value)

    def delete(self):
        """ removes a node from the list """
        if self.next:
            self.prev.next = self.next
            self.next.prev = self.prev
        else:
            self.prev.next = None

    def convert_to_end(self):
        self.next = None
        self.__class__ = EndNode
