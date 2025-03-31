from panda3d.core import Quat, lookAt, Vec3
from game_object import GameObject
from pubsub import pub

class Teleporter(GameObject):
    def __init__(self, position, kind, id, size, physics):
        super().__init__(position, kind, id, size, physics)

    def collision(self, other):
        # TODO: this is moving the camera attached to the player, but not the physics object
        # used in the kcc
        current = other.position
        other.position = (current[0], current[1]-5, current[2])

