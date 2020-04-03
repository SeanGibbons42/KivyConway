from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget

from kivy.graphics import Rectangle, Color
from kivy.clock import Clock

from functools import partial
import sys

from models import Naive_CGoL, List_CGoL

Config.set("graphics", "width", 2500)
Config.set("graphics", "height", 1250)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

Builder.load_file("main.kv")

class RootWidget(BoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.model = List_CGoL()

class RoundedButtonHead(Button):
    pass

class RoundedButton(RoundedButtonHead):
    def color_change_click(self):
        self.bcolor = self.active_color

    def color_change_release(self):
        self.bcolor = self.inactive_color

class CGol_Square_Head(Button):
    pass

class CGoL_Square(CGol_Square_Head):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.clicked = False

    def click(self):
        self.icolor = self.offcolor if self.clicked else self.oncolor
        self.clicked = not self.clicked
        self.command()

    def command(self):
        print(sys.getsizeof(self))

class CGoL_Board(GridLayout):

    def __init__(self, *args, **kwargs):
        """Class CGoL_Board represents the simulation grid"""
        super().__init__(**kwargs)
        self.boxes = []
        self.app = App.get_running_app()
        #delay some of the setup until the UI has been initialized and dimensions finalized
        Clock.schedule_once(self.setup_grid, 1)

    def setup_grid(self, time):
        box_size = ( self.width/self.cols, self.height/self.rows )
        if not self.boxes:
            self.boxes = self.reset_grid(self.rows, self.cols, box_size)
            self.bind(height=partial(self.resize_grid, self.rows, self.cols))
            self.bind(width=partial(self.resize_grid, self.rows, self.cols))

        self.app.root.model.set_board(self)

    def on_touch_down(self, touch):
        """Event Handler for click event"""
        #rpos is the click position relative to the widget's 0,0 point
        rpos = ( touch.pos[0] - self.pos[0], touch.pos[1] - self.pos[1])

        #check if the click occured inside the board
        if rpos[0] >= 0 and rpos[0] <= self.width and rpos[1] >= 0 and rpos[1]<=self.height:
            box_size = ( self.width/self.cols, self.height/self.rows )
            box_clicked = ( int(rpos[0]//box_size[0]), int(rpos[1]//box_size[1]) )
            #manipulate the data clicked box
            self.get_box(box_clicked).toggle()
            #make a call to the data model and business logic
            self.app.root.model.button_clicked((box_clicked[1], box_clicked[0]))

    def get_box(self, *args):
        """ returns a reference to a specific block """
        if len(args) == 1:
            col, row = args[0]
            return self.boxes[row][col]
        elif len(args) == 2:
            row, col = args[0], args[1]
            return self.boxes[row][col]
        else:
            raise Exception("Too many args!")


    def reset_grid(self, rows, cols, box_size):
        """ Reset Grid is called when the board is reset """
        boxes = []
        self.canvas.clear()
        with self.canvas:

            for row in range(rows):
                nrow = []
                for col in range(cols):
                    nc = Color()
                    nc.rgba = self.offcolor
                    x = col*box_size[0] + self.x
                    y = row*box_size[1] + self.y
                    nsquare = CGoL_Box( size = box_size, pos = (x, y), color = nc,
                                        oncolor=self.oncolor, offcolor = self.offcolor)
                    nrow.append(nsquare)
                boxes.append(nrow)
        return boxes

    def resize_grid(self, *args):
        """ This function is called to re-draw the squares when
            parent widget dimensions change."""
        box_size = ( self.width/self.cols, self.height/self.rows )
        for row in range(self.rows):
            for col in range(self.cols):
                x = col*box_size[0] + self.x
                y = row*box_size[1] + self.y
                self.boxes[row][col].size = box_size
                self.boxes[row][col].pos = (x, y)

class CGoL_Box(Rectangle):
    def __init__(self, *args, **kwargs):
        """ Parameters: Size, Pos, color reference, "on" color and "off" color """
        super().__init__(*args, **kwargs)
        self.state = False
        self.newstate = False

        self.color = kwargs["color"]
        self.oncolor = kwargs["oncolor"]
        self.offcolor = kwargs["offcolor"]


    def toggle(self):
        """ Swap the state and color of the box. Called by the board class during the setup phase. """
        self.newstate = not self.state
        self.display()

    def display(self):
        """ Transfers the buffered state to the state variable. """
        # if self.state != self.newstate:
        self.state = self.newstate
        self.color.rgba = self.oncolor if self.state else self.offcolor

class Controls(BoxLayout):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.model = None
        self.speed = 10
        self.duration = 10
        Clock.schedule_once(self.register, 1)

    def register(self, delay):
        self.model = self.app.root.model
        self.model.set_controls(self)

    def start(self):
        self.model.duration = int(self.ids['duration'].inputtext)
        self.model.speed =  float(self.ids['speed'].inputtext)
        self.model.start()

    def pause(self):
        self.model.pause()

    def reset(self):
        self.model.clear()

class Conway(App):
    def build(self):
        return RootWidget()


if __name__=="__main__":
    Conway().run()
