import pyglet
    
class Player(pyglet.sprite.Sprite):
    """Player class, will have the image, along with coords and abilities"""
    image = pyglet.image.load('player.png')
    image.anchor_x = image.width/2
    image.anchor_y = image.height/2
    def __init__(self, window, x, y, batch=None):
        super(Player, self).__init__(Player.image, x, y, batch=batch)
        self.window = window
        self.shooting = False
        self.bullets = None

    def update(self, dt):
        """ Make sure your not offscreen """
        pass
        #lt, rt, rb, lb = self.get_rect()
        #if lt[0] <= 0:
        #    self.x = 0
        #if lt[1] >= self.window.height:
        #    self.y = self.window.height
        #if rb[0] >= self.window.width:
        #    self.x = self.window.width
        #if rb[1] <= 0:
        #    self.y = 0

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


