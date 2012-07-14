import pyglet
    
class Mob(pyglet.sprite.Sprite):
    """Mob class, will have the image, along with coords and abilities"""
    image = pyglet.image.load('baddie.png')
    image.anchor_x = image.width/2
    image.anchor_y = image.height/2
    def __init__(self, window, x, y, batch=None):
        super(Mob, self).__init__(Mob.image, x, y, batch=batch)
        self.window = window
        self.bullets = None
        self.offscreen = False
        self.shot_timer = 0

    def update(self, dt):
        """ Make sure your not offscreen """
        if self.x < 0 or self.y < 0:
            self.offscreen = True
        if self.shot_timer == 500:
            self.shot_timer = 0
        self.shot_timer += 1
        self.y -= 3
        
    def get_rect(self):
        left = self.x - self.width/2
        right = self.x + self.width/2
        top = self.y + self.height/2
        bottom = self.y - self.height/2
        
        lt = (left, top)
        rt = (right, top)
        lb = (left, bottom)
        rb = (right, bottom)
        return lt, rt, rb, lb


