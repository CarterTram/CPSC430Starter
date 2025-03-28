from pubsub import pub
from panda3d.core import CollisionBox, CollisionNode


class ViewObject:
    # Define texture mapping as a class-level constant
    TEXTURE_MAP = {
        "fallingCrate": "Textures/cube_5.png",
        "default": "Textures/crate.png"
    }

    def __init__(self, game_object):
        self.game_object = game_object

        if self.game_object.physics:
            self.node_path = base.render.attachNewNode(self.game_object.physics)
        else:
            self.node_path = base.render.attachNewNode(self.game_object.kind)

        self.cube = base.loader.loadModel("Models/cube")
        self.cube.reparentTo(self.node_path)
        self.cube.setPos(*game_object.position)

        texture_path = self.TEXTURE_MAP.get(self.game_object.kind, self.TEXTURE_MAP["default"])
        self.cube_texture = base.loader.loadTexture(texture_path)
        self.cube.setTexture(self.cube_texture)

        bounds = self.cube.getTightBounds()
        bounds = bounds[1] - bounds[0]
        size = game_object.size

        x_scale = size[0] / bounds[0]
        y_scale = size[1] / bounds[1]
        z_scale = size[2] / bounds[2]

        self.cube.setScale(x_scale, y_scale, z_scale)

        self.texture_on = True
        self.toggle_texture_pressed = False
        pub.subscribe(self.toggle_texture, 'input')

    def deleted(self):
        pass

    def toggle_texture(self, events=None):
        if 'toggleTexture' in events:
            self.toggle_texture_pressed = True

    def tick(self):
        """Handles object updates."""
        if not self.game_object.physics:
            h = self.game_object.z_rotation
            p = self.game_object.x_rotation
            r = self.game_object.y_rotation
            self.cube.setHpr(h, p, r)
            self.cube.set_pos(*self.game_object.position)

        if self.toggle_texture_pressed and self.game_object.is_selected:
            if self.texture_on:
                self.texture_on = False
                self.cube.setTextureOff(1)
            else:
                self.texture_on = True
                self.cube.setTexture(self.cube_texture)

        self.toggle_texture_pressed = False
        self.game_object.is_selected = False