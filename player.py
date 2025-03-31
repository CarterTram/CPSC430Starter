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
        print(f"{self.kind} collides with {other.kind}")

    # Override these and don't defer to the physics object
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value