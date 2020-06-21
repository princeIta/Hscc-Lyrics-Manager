from kivy.uix.textinput import TextInput
from kivy.base import EventLoop
from kivy.uix.textinput import TextInput


class BubbledTextInput(TextInput):   

    def on_touch_down(self, touch):

        super(BubbledTextInput,self).on_touch_down(touch)

        if touch.button == 'right':
            print("right mouse clicked")
            pos = self.to_local(*touch.pos, relative=True)

            self._show_cut_copy_paste(
                pos, EventLoop.window, mode='paste')