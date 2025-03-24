from panda3d.core import Quat, lookAt, Vec3
from game_object import GameObject
from pubsub import pub

class Player(GameObject):
    def __init__(self, position, kind, id, size, physics):
        super().__init__(position, kind, id, size, physics)

        self.speed = 0.1

        pub.subscribe(self.input_event, 'input')

    def input_event(self, events=None):
        pass

    def collision(self, other):
        # TODO: the physics engine needs to detect the
        # collision and call this function
        pass

