import pyglet
from pyglet import clock
import time
from pprint import pprint
import os, glob
from player import Player
from mob import Mob
import bulletml
#import bulletml.bulletyaml
import random
import math
from bulletml.collision import collides_all, collides

pyglet.options['debug_gl'] = False
FPS = 60
BADDIEMINSPEED = 1
BADDIEMAXSPEED = 8
ADDNEWBADDIERATE = 50
red = (1, 0, 0, 1)
blue = (0, 0, 1, 1)
black = (0, 0, 0 , 1)

class Game(pyglet.window.Window):
    is_event_handler = True
    def __init__(self, *args, **kwargs):
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()
        template = pyglet.gl.Config(double_buffer=True)
        config = screen.get_best_config(template)
        context = config.create_context(None)
        super(Game, self).__init__(resizable=True, width=800, height=600, caption="Bullets OMG:" , context=context)
        #pyglet.window.Window.__init__(self, )
        self.mouse_pos = (0, 0)
        self.paused = False
        pyglet.clock.schedule_interval(self.update, 1.0/FPS)
        self.sprite_batch = pyglet.graphics.Batch()
        self.mobs = []
        image = pyglet.image.load('player.png')
        image.anchor_x = image.width/2
        image.anchor_y = image.height/2
        
        self.player = Player(image, self.mouse_pos[1], self.mouse_pos[1], self.sprite_batch)
        
        self.target = bulletml.Bullet()
        self.player_target = bulletml.Bullet()
        self.mob_bullets_active = set([])
        self.player_bullets_active = set([])
        self.filenames = []
        for myfile in glob.glob(os.path.join('patterns/', "*.xml")):
            self.filenames.append(myfile)
        filename = self.filenames[1]
        mob_filename = self.filenames[0]
        self.doc = bulletml.BulletML.FromDocument(open(filename, "rU"))
        self.mob_doc = bulletml.BulletML.FromDocument(open(mob_filename, "rU"))
        self.sprites = []

    def on_key_press(self, symbol, modifier):
        if symbol == pyglet.window.key.SPACE:
            print "You pressed space"
            self.paused ^= True
        elif symbol == pyglet.window.key.LEFT:
            pass
        elif symbol == pyglet.window.key.RIGHT:
            pass
        elif symbol == pyglet.window.key.ESCAPE:
            import sys
            sys.exit()

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_pos = (x, y)
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.mouse_pos = (x, y)
        if buttons & pyglet.window.mouse.LEFT:
            self.player.shooting = True
            source = bulletml.Bullet.FromDocument(self.doc, x=x/2, y=y/2+10, target=self.target, rank=0.5, speed=10)
            source.vanished = True
            self.player_bullets_active.add(source)

    def on_mouse_release(self, x, y, button, modifiers):
        self.player.shooting = False

    def on_mouse_press(self, x, y, button, modifiers):
        self.player.shooting = True
        source = bulletml.Bullet.FromDocument(self.doc, x=x/2, y=y/2, target=self.target, rank=0.5)
        #source.speed = 120
        source.vanished = True
        self.player_bullets_active.add(source)
        return


    def update(self, dt):
        #self.player.update(dt)
        self.player.x, self.player.y = self.mouse_pos
        if self.player.shooting:
            source = bulletml.Bullet.FromDocument(self.doc, x=self.player.x/2, y=self.player.y/2+10, target=self.target, rank=0.5)
            source.vanished = True
            self.player_bullets_active.add(source)
        
        self.target.x, self.target.y = self.mouse_pos[0]/2, self.height
        self.target.px, self.target.py = self.target.x, self.target.y
        self.player_target.px , self.player_target.py = self.target.x, self.player_target.y 
        self.player_target.x, self.player_target.y = self.mouse_pos[0]/2, self.mouse_pos[1]/2
        
        for s in self.sprites[:]:
            s.update(dt)
            if s.shot_timer == 5 and not s.offscreen:
                    s.bullets = bulletml.Bullet.FromDocument(self.mob_doc, x=s.x/2, y=s.y/2, target=self.player_target, rank=0.5)
                    s.bullets.vanished = True
                    self.mob_bullets_active.add(s.bullets)
            if s.offscreen:
                self.sprites.remove(s)

        m_active = list(self.mob_bullets_active)
        for obj in m_active:
            new = obj.step()
            self.mob_bullets_active.update(new)
            if (obj.finished 
                or not (0 < obj.x < self.width)
                or not (0 < obj.y < self.height)):
                self.mob_bullets_active.remove(obj)
                
        p_active = list(self.player_bullets_active)
        for obj in p_active:
            new = obj.step()
            self.player_bullets_active.update(new)
            if (obj.finished 
                or not (0 < obj.x < self.width)
                or not (0 < obj.y < self.height)):
                self.player_bullets_active.remove(obj)

        mob_collides = False
        player_collides = False

        if m_active:
            mob_collides = collides_all(self.player_target, m_active)

        if p_active:
            for m in self.sprites:
                for p in p_active:
                    if distance(m, p) < (m.width/2 + 1):
                        m.offscreen = True
                        p.vanished = True

        if player_collides:
            pyglet.gl.glClearColor(*red)
        elif mob_collides:
            pyglet.gl.glClearColor(*blue)
        else:
            pyglet.gl.glClearColor(*black)

    def main(self):
        red = (1, 0, 0, 1)
        blue = (0, 0, 1, 1)
        black = (0, 0, 0 , 1)
        baddieAddCounter = 0
        #fps_display = pyglet.clock.ClockDisplay()
        mob_image = pyglet.image.load('baddie.png')
        mob_image.anchor_x = mob_image.width/2
        mob_image.anchor_y = mob_image.height/2
        self.set_mouse_visible(False)
        while not self.has_exit:
            pyglet.clock.tick()
            self.dispatch_events()
            baddieAddCounter += 1
            if baddieAddCounter == ADDNEWBADDIERATE:
                baddieAddCounter = 0
                newBaddie = Mob(mob_image, random.randint(0, self.width),self.height, self.sprite_batch )
                #newBaddie = Mob(mob_image, self.width/2,self.height, self.sprite_batch )
                newBaddie.bullets = bulletml.Bullet.FromDocument(self.mob_doc, x=newBaddie.x/2, y=newBaddie.y/2, target=self.player_target, rank=0.5)
                newBaddie.bullets.vanished = True
                self.mob_bullets_active.add(newBaddie.bullets)
                self.sprites.append(newBaddie)

            bullet_batch = pyglet.graphics.Batch()
            vert_l = []
            c = []
            for obj in self.mob_bullets_active:
                try:
                    x, y = obj.x, obj.y
                except AttributeError:
                    pass
                else:
                    if not obj.vanished:
                        x *= 2
                        y *= 2
                        x -= 1
                        y -= 1
                        vert_l.append(x)
                        vert_l.append(y)
                        c.append(255)
                        c.append(255)
                        c.append(0)
            vl = pyglet.graphics.vertex_list(len(vert_l)/2, 
                                             ('v2f\static', vert_l), 
                                             ('c3B\static', c) 
                                             )
            bullet_batch.add(len(vert_l)/2, pyglet.gl.GL_POINTS, None, ('v2f\static', vert_l ) , ('c3B\static', c))
            c = []
            vert_l = []
            for obj in self.player_bullets_active:
                try:
                    x, y = obj.x, obj.y
                except AttributeError:
                    pass
                else:
                    if not obj.vanished:
                        x *= 2
                        y *= 2
                        x -= 1
                        y -= 1
                        vert_l.append(x)
                        vert_l.append(y)
                        c.append(255)
                        c.append(0)
                        c.append(255)
            vl = pyglet.graphics.vertex_list(len(vert_l)/2, 'v2f' )
            vl.vertices = vert_l
            pyglet.gl.glPointSize(4.0)
            bullet_batch.add(len(vert_l)/2, pyglet.gl.GL_POINTS, None, ('v2f\static', vert_l ), ('c3B\static', c))
            self.clear()
            bullet_batch.draw()
            self.sprite_batch.draw()
            self.flip()
def distance(a, b):
    return math.sqrt((a.x/2-b.x)**2 + (a.y/2-b.y)**2)
if __name__ == "__main__":
    g = Game()
    g.main()