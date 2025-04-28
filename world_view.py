from panda3d.core import Vec3
from pubsub import pub
from view_object import ViewObject

class WorldView:
    def __init__(self, game_logic):
        self.game_logic = game_logic
        self.view_objects = {}
        pub.subscribe(self.handle_perfect_drop, "perfect_drop")
        pub.subscribe(self.new_game_object, 'create')

    def new_game_object(self, game_object):
        if game_object.kind == 'player':
            return

        view_object = ViewObject(game_object)
        self.view_objects[game_object.id] = view_object

    def handle_perfect_drop(self, obj_id, new_size):
        view_obj = self.view_objects.get(obj_id)
        if view_obj:
            bounds = view_obj.cube.getTightBounds()
            bounds = bounds[1] - bounds[0]
            size = new_size

            x_scale = size[0] / bounds[0]
            y_scale = size[1] / bounds[1]
            z_scale = 1

            view_obj.cube.setScale(x_scale/2, y_scale/2, z_scale/2)

    def tick(self):
        for key in self.view_objects:
            self.view_objects[key].tick()