from datetime import datetime
import sqlite3
from functools import partial
import os.path

from kivy.utils import get_color_from_hex
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.graphics import SmoothLine
from kivy.graphics import InstructionGroup
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, BooleanProperty
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.button import MDIconButton
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

from kivymd.snackbar import Snackbar
from kivymd.list import MDList, ContainerSupport, TwoLineListItem


conn = sqlite3.connect('res/db/lyrics.db')
conn_cursor = conn.cursor()
query_result = []
retrieved_data = []

def get_current_time_string():
    date_time_now = datetime.isoformat(datetime.now())
    return " ".join(date_time_now.split('T')).split('.')[0]


def copy_to_clipboard(data):
        Clipboard.copy(data)
    
def notify(notify_widget, text_to_display, attach_to):
    notify_widget.center_x = attach_to.center_x
    notify_widget.center_y = attach_to.center_y
    attach_to.bind(center_x=lambda inst, center_x: bind_cb(inst, 'center_x', center_x, notify_widget))
    attach_to.bind(center_y=lambda inst, center_y: bind_cb(inst, 'center_y', center_y, notify_widget))
    notify_widget.text = text_to_display
    show_notification = Animation(opacity=1, duration=1.2) + Animation(opacity=1, duration=1.5)+ Animation(opacity=0, duration=1.2)
    show_notification.start(notify_widget)

def bind_cb(widget, prop, new_val_of_prop, to):
    setattr(to, prop, new_val_of_prop)

class EditLyricsWindow(Popup):
    update_lyrics_btn = ObjectProperty(None)
    cancel_edit_btn = ObjectProperty(None)
    lyrics_title = ObjectProperty(None)
    lyrics_body = ObjectProperty(None)
    data_id = NumericProperty(0)
    notification_widget = ObjectProperty(None)
    update_was_done = BooleanProperty(False)

    def on_update_lyrics_btn(self, widget_attached_to, btn_inst):
        btn_inst.bind(on_release=self.update_lyrics_db)
    
    def update_lyrics_db(self, btn_inst):
        global conn
        global conn_cursor
        if self.update_was_done:
            self.update_was_done = False
        new_title = self.lyrics_title.text
        new_content = self.lyrics_body.text
        rowid = self.data_id
        conn_cursor.execute("UPDATE Lyrics SET content=?, title=? WHERE id=?", (new_content, new_title, rowid))
        conn.commit()
        self.dismiss()
        if self.notification_widget:
            notify(self.notification_widget, 'Update was successful', self)
            self.update_was_done = True



class DeleteLyricsWindow(Popup):
    delete_lyrics_btn = ObjectProperty(None)
    cancel_btn = ObjectProperty(None)
    data_idx = NumericProperty(0)
    widget_to_delete = ObjectProperty(None)
    data = None
    widget_to_delete_from = ObjectProperty(None)
    title_= StringProperty('')


    def __init__(self, **kwargs):
        super(DeleteLyricsWindow, self).__init__()
        self.data_idx = kwargs.get('data_idx')
        self.widget_to_delete = kwargs.get('widget')
        self.title_ = kwargs.get('title')
        self.widget_to_delete_from = kwargs.get('container_widget')
    
    def delete(self):
        global retrieved_data 
        global conn_cursor
        self.widget_to_delete_from.remove_widget(self.widget_to_delete)
        rowid = retrieved_data[self.data_idx][0]
        retrieved_data[self.data_idx] = None
        delete_stmt = "DELETE FROM Lyrics WHERE id = ?;"
        conn_cursor.execute(delete_stmt, (rowid,))
        conn.commit()
        self.dismiss()


class RetrievedDataItemStyling(Label):
    colors = lambda x,y: get_color_from_hex(y)
    
    def on_text(self, widget, text_value):
        self.text = widget.text.replace('\n', ' ')

class ThContainer(BoxLayout):
    colors = lambda x,y: get_color_from_hex(y)


class LyricsDatabaseSubScreen(Screen):
    colors = lambda x,y: get_color_from_hex(y)
    container = ObjectProperty(None)
    scrollview = ObjectProperty(None)
    notification_widget = ObjectProperty(None)
    trigger_db_retrieval = BooleanProperty(False)

    def __init__(self, **kw):
        super(LyricsDatabaseSubScreen, self).__init__(**kw)
        self.delete_modal = None
        if not os.path.isfile('res/db/lyrics.db'):
            self.get_lyrics_db()
        Window.bind(on_keyboard=self.on_keyboard_pressed)

    def on_keyboard_pressed(self, *args, **kwargs):
        # 274 81 None []
        if args[1]==273 and args[2]==82 and args[3]==None and not args[4]:
            if self.scrollview and self.scrollview.scroll_y >= 0 and self.scrollview.scroll_y <1:
                self.scrollview.scroll_y+=0.4 

        # 273, 82, None, []
        if args[1]==274 and args[2]==81 and args[3]==None and not args[4]:
            if self.scrollview and self.scrollview.scroll_y > 0 and self.scrollview.scroll_y <=1:
                self.scrollview.scroll_y-=0.4

    def get_lyrics_db(self):
        Window.set_system_cursor('wait')
        query_stmt = "SELECT id, title, content FROM  Lyrics "
        global retrieved_data
        if (self.container and not retrieved_data) or self.trigger_db_retrieval is True:
            conn_cursor.execute(query_stmt)
            returned_data = conn_cursor.fetchall()
            retrieved_data = returned_data
            self.container.clear_widgets()
            self.trigger_db_retrieval = False
            for idx in range(len(retrieved_data)):
                if retrieved_data[idx]:
                    Box = GridLayout(cols=4, size_hint_y=None, height=dp(46), spacing=2)
                    title = RetrievedDataItemStyling(text=
                        retrieved_data[idx][1][:20]+'...' if len(
                                retrieved_data[idx][1])>=20 else
                        retrieved_data[idx][1], size_hint_x=0.3)
                    content = RetrievedDataItemStyling(text = retrieved_data[idx][2][:50] +'...', size_hint_x=0.6)
                    edit_button = MDIconButton(icon='pencil')
                    edit_button.bind(on_release=partial(self.show_popup, idx, retrieved_data))
                    edit_button_box = ThContainer(size_hint_x=0.1)
                    edit_button_box.add_widget(edit_button)
                    delete_button = MDIconButton(icon='delete')
                    delete_button.bind(on_release=partial(self.confirm_delete, idx, retrieved_data, Box, self.container))
                    delete_button_box = ThContainer(size_hint_x=0.1)
                    delete_button_box.add_widget(delete_button)
                    Box.add_widget(title)
                    Box.add_widget(content)
                    Box.add_widget(edit_button_box)
                    Box.add_widget(delete_button_box)
                    self.container.add_widget(Box)
        Window.set_system_cursor('arrow')

    def confirm_delete(self, idx, retrieved_data, widget_to_delete, from_widget, *args):
        self.delete_modal = DeleteLyricsWindow(data_idx=idx, data=retrieved_data, 
            title =retrieved_data[idx][1][:30]+'...' if len(retrieved_data[idx][1][:30])>=30 else retrieved_data[idx][1] , widget=widget_to_delete, container_widget = from_widget)
        self.delete_modal.open()

    def show_popup(self, idx, database, *args):
        self.modal = EditLyricsWindow()
        self.modal.data_id = database[idx][0]
        self.modal.lyrics_title.text = database[idx][1]
        self.modal.lyrics_body.text = database[idx][2]
        self.modal.notification_widget = self.notification_widget
        self.modal.bind(update_was_done=self.update_db_result)
        self.modal.open()

    def update_db_result(self, obj, obj_val):
        if obj_val is True:
            self.trigger_db_retrieval = True

    def on_trigger_db_retrieval(self, obj, obj_val):
        if obj_val is True:
            self.get_lyrics_db()

class LyricsSearchSubScreen(Screen):
    lyrics_display_widget = ObjectProperty(None)
    search_result_container = ObjectProperty(None)
    colors = lambda x,y: get_color_from_hex(y)
    notification_widget = ObjectProperty(None)
    lyrics_display_widget_container = ObjectProperty(None)
    search_textfield = ObjectProperty(None)
    
    def __init__(self, **kw):
        super(LyricsSearchSubScreen, self).__init__(**kw)
        self.lessn_notify = 0

    def on_search_textfield(self, screen, wid_instance):
        self.search_textfield.bind(text=self.query_db_for_lyrics)
    
    def query_db_for_lyrics(self, instance, text):
        Window.set_system_cursor('wait')
        if os.path.isfile('res/db/lyrics.db'): 
            conn_cursor.execute("SELECT * FROM Lyrics_index WHERE Lyrics_index MATCH ?", (text,))
            conn.commit()
            
        global query_result

        query_result = conn_cursor.fetchall()
        if query_result and self.search_result_container:
            self.search_result_container.clear_widgets()
            lyrics = query_result[0][1]
            title = query_result[0][0] 
            self.lyrics_display_widget.text = lyrics
            copy_to_clipboard(lyrics)

            if not self.lessn_notify%5 and query_result:
                notify(self.notification_widget, title+" has been copied to clipboard", self.lyrics_display_widget_container)
            self.lessn_notify+=1
            if self.lessn_notify > 15:
                self.lessn_notify = 0
            
            for lyrics_idx in range(len(query_result)):
                result_item = SearchResultItem(text = query_result[lyrics_idx][0], secondary_text=query_result[lyrics_idx][1][:20])
                result_item.bind(on_touch_down=partial(self.result_item_touched, lyrics_idx, query_result))
                self.search_result_container.add_widget(result_item)            
        else: 
            if self.search_result_container:
                self.search_result_container.clear_widgets()
            if self.lyrics_display_widget:
                self.lyrics_display_widget.text = ''
        Window.set_system_cursor('arrow')

    def result_item_touched(self, lyrics_idx, query_result, *args):
        lyrics = query_result[lyrics_idx][1]
        title = query_result[lyrics_idx][0]
        if self.lyrics_display_widget:
            self.lyrics_display_widget.text = lyrics
            copy_to_clipboard(lyrics)
            notify(self.notification_widget, title+" has been copied to clipboard", self.lyrics_display_widget_container)

class CustomButton(Button):
    pass


class CustomDropdown(DropDown):
    dropdown_items = set()
    button_width = None
    selected_id = NumericProperty(0)

    def __init__(self, **kwargs):
        super(CustomDropdown, self).__init__(**kwargs)
        

    def build_list(self, list_items):
        new_items = set(list_items)
        if self.dropdown_items:
            new_items = new_items - self.dropdown_items
        self.dropdown_items = self.dropdown_items.union(new_items)
        for idx, name in new_items:
                btn = CustomButton(size_hint=(1, None), height=40, text=name)
                btn.bind(on_release= partial(self.selected, btn.text, idx))
                self.add_widget(btn)

    def selected(self, option, idx, *args):
        self.selected_id = idx
        self.select(option)

class AddLyricsSubScreen(Screen):
    colors = lambda x,y: get_color_from_hex(y)
    song_title = ObjectProperty(None)
    lyrics = ObjectProperty(None)
    _artist = ObjectProperty(None)
    add_lyrics_container = ObjectProperty(None)
    notification_widget = ObjectProperty(None)
    trigger_db_retrieval = BooleanProperty(False)


    def __init__(self, **kw):
        super(AddLyricsSubScreen, self).__init__(**kw)
        self.custom_dropdown = CustomDropdown()
        self.artist_id = None
        Window.bind(on_keyboard=self.on_keyboard_pressed)

    def on_keyboard_pressed(self, *args, **kwargs):
        # 274 81 None []
        if args[1]==273 and args[2]==82 and args[3]==None and not args[4] and \
         self.song_title and self.lyrics and self._artist and  \
         not self.song_title.focus and not self.lyrics.focus and not self._artist.focus:
            if self.add_lyrics_container and self.add_lyrics_container.scroll_y >= 0 and self.add_lyrics_container.scroll_y <1:
                self.add_lyrics_container.scroll_y+=0.4 

        # 273, 82, None, []
        if args[1]==274 and args[2]==81 and args[3]==None and not args[4] and \
         self.song_title and self.lyrics and self._artist and  \
         not self.song_title.focus and not self.lyrics.focus and not self._artist.focus:
            if self.add_lyrics_container.scroll_y > 0 and self.add_lyrics_container.scroll_y <=1:
                self.add_lyrics_container.scroll_y-=0.4 
    
    def add_lyrics(self, **kwargs):
        song_title = kwargs.get('song_title')
        lyrics = kwargs.get('lyrics')
        artist_id = self.artist_id

        if not artist_id or not song_title or not lyrics:
            notify(self.notification_widget, "Please do not leave any field blank!", self)
        else: 
            sqlinsert_into_lyrics = "INSERT INTO Lyrics(content, title, artist_id) VALUES(?, ?, ?)"
            sqlinsert_into_lyrics_info = "INSERT INTO Lyrics_info(date_added, lyrics_id) VALUES(?, ?)"
            
            conn_cursor.execute(sqlinsert_into_lyrics, (lyrics, song_title, artist_id))
            lyrics_id = conn_cursor.lastrowid
            
            time_added = get_current_time_string()
            conn_cursor.execute(sqlinsert_into_lyrics_info, (time_added, lyrics_id))
            if conn_cursor.lastrowid:
                notify(self.notification_widget,'Lyrics added successfully', self)
                self.song_title.text = ''
                self.lyrics.text = ''
                del song_title
                del lyrics
                self.trigger_db_retrieval = False
                self.trigger_db_retrieval = True
            conn.commit()
    
    def add_artist(self, artist_name=None):
        if not artist_name:
            if self.notification_widget:
                notify(self.notification_widget, "Please do not leave the artist name field blank!", self)
        else:
            sqlinsert_into_artist = "INSERT INTO Artists(name) VALUES(?)"
            conn_cursor.execute(sqlinsert_into_artist, (artist_name,))
            if conn_cursor.lastrowid:
                notify(self.notification_widget,'Artist added successfully', self)
                self.ids._artist.text = ''
            conn.commit()
    
    def show_dropdown(self, btn):
        self.btn = btn
        # query db for list of artist and add to drop down
        sql_statement = "SELECT id, name FROM Artists"
        conn_cursor.execute(sql_statement)
        conn.commit()
        fetched_artists = conn_cursor.fetchall()
        self.custom_dropdown.bind(on_select=lambda instance, x: setattr(self.btn, 'text', x))
        self.custom_dropdown.bind(selected_id=self.set_selected_option)
        self.custom_dropdown.button_width = self.btn.width
        self.custom_dropdown.build_list(fetched_artists)
        self.custom_dropdown.open(btn)

    def set_selected_option(self, inst, idx):
        self.artist_id = idx


class SearchResultItem(TwoLineListItem, ContainerSupport):
    pass


class LineOverlay:
    """
        this class draws an underline over a navigation menu when a menu item is clicked on
    """
    def __init__(self, **kwargs):
        # widget that houses the nav menu item
        self.parent = None
        self.line_inst = InstructionGroup()
        self.line = None

        # nav menu item
        self.child = None
        self.update = None

    def render_line(self, **kwargs):
        self.update = lambda instance, prop: self.render_line(isupdate=True)

        child = kwargs.get('child')
        if child:
            self.child = child
            self.child.bind(pos=self.update)
        isupdate = kwargs.get('isupdate')

        if not self.parent: 
            self.parent = kwargs.get('parent')
            self.line = SmoothLine(points=(self.child.x, self.child.y+dp(6), self.child.x+self.child.width, self.child.y+dp(6)), width=2, cap='square')
            self.line_inst.add(self.line)
            self.parent.canvas.after.add(self.line_inst)
        else:
            if isupdate:
                anim = Animation(points=(self.child.x, self.child.y+dp(6), self.child.x+self.child.width, self.child.y+dp(6)), duration=0)
            else:
                anim = Animation(points=(self.child.x, self.child.y+dp(6), self.child.x+self.child.width, self.child.y+dp(6)), duration=0.2)

            anim.start(self.line)


class HomeScreen(Screen):
    bg_image = Image(source='res/images/main.jpg', keep_ratio=True)
    colors = lambda x,y: get_color_from_hex(y)
    custom_dropdown = None

    def __init__(self, **kwargs):
        super(HomeScreen, self).__init__(**kwargs)
        self.menu_marker = LineOverlay()

    