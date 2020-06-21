from kivy.uix.screenmanager import  Screen, NoTransition
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import sqlite3

def init_db():
    
    conn = sqlite3.connect('res/db/lyrics.db')
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Lyrics_info (
        id integer PRIMARY KEY,
        date_added text NOT NULL,
        lyrics_id integer NOT NULL,
        FOREIGN KEY (lyrics_id) REFERENCES Lyrics (id)
        );

        CREATE TABLE IF NOT EXISTS Lyrics (
        id integer PRIMARY KEY,
        content text NOT NULL,
        title text NOT NULL,
        artist_id integer NOT NULL,
        FOREIGN KEY (artist_id) REFERENCES Artists (id)
        );

        CREATE VIRTUAL TABLE Lyrics_index USING fts3(title TEXT, body TEXT, tokenize=porter);

        CREATE TRIGGER after_update AFTER UPDATE ON Lyrics 
        WHEN old.content <> new.content
        OR old.title <> new.title
        BEGIN
            UPDATE Lyrics_index
            SET title = new.title,
            body = new.content
            WHERE
            rowid = old.id;
        END;

        CREATE TRIGGER after_lyrics_insert AFTER INSERT ON Lyrics 
        BEGIN
            INSERT INTO Lyrics_index (
                rowid,
                title,
                body
            )
            VALUES(
                new.id,
                new.title,
                new.content
            );
        END;

        CREATE TRIGGER after_delete AFTER DELETE ON Lyrics 
        BEGIN
            DELETE
            FROM 
                Lyrics_index 
            WHERE
                rowid = old.id;
            DELETE
            FROM
                Lyrics_info
            WHERE
                lyrics_id = old.id;
        END;      

        CREATE TABLE IF NOT EXISTS Artists (
        id integer PRIMARY KEY,
        name text NOT NULL
        );


        """)
    conn.commit()
    conn.close() 

import os.path
if not os.path.isfile('res/db/lyrics.db'):
    init_db()


class SplashScreen(Screen):

    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        self.anim_logo = Animation(opacity=1, size=(149, 174), duration=0.3)
        self.trigger_anim = Clock.create_trigger(self.animate_logo, 1)
        self.trigger_anim()


    def init_app(self):
        # animation done
        self.manager.transition = NoTransition()
        self.manager.current = 'home_screen'

    def animate_logo(self, dt):
        self.logo = self.ids._hscc_logo
        self.anim_logo.start(self.logo)
        self.anim_logo.bind(on_complete=lambda x,y: Clock.create_trigger(lambda x: self.init_app(), 2)())
