import math

from panda3d.bullet import BulletWorld, BulletBoxShape, BulletRigidBodyNode, BulletCapsuleShape, ZUp
from panda3d.core import Vec3, VBase3, TransformState, Point3, TextNode
from direct.gui.OnscreenText import OnscreenText
from pubsub import pub
from game_object import GameObject
from player import Player

class GameWorld:
    def __init__(self, debugNode=None):
        self.properties = {}
        self.game_objects = {}
        self.next_id = 0
        self.physics_world = BulletWorld()
        self.physics_world.setGravity(Vec3(0, 0, -9.81))
        self.swing_time = 0

        if debugNode:
            self.physics_world.setDebugNode(debugNode)

        self.kind_to_shape = {
            "crate": self.create_box,
            "red_box": self.create_box,
            "enemy": self.create_capsule,
            "fallingCrate": self.create_box,
        }

        self.drop_timer = 0
        self.drop_interval = 3.0
        self.active_box = None
        self.score = 0
        self.game_over = False

        self.score_text = OnscreenText(
            text=f"Score: {self.score}",
            pos=(-1.3, 0.95),  # Top-left corner
            scale=0.07,
            fg=(1, 1, 1, 1),  # White text
            align=TextNode.ALeft
        )

    def create_capsule(self, position, size, kind, mass):
        radius = size[0]
        height = size[1]
        shape = BulletCapsuleShape(radius, height, ZUp)
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setTransform(TransformState.makePos(VBase3(position[0], position[1], position[2])))
        self.physics_world.attachRigidBody(node)
        return node

    def create_box(self, position, size, kind, mass):
        shape = BulletBoxShape(Vec3(size[0] / 2, size[1] / 2, size[2] / 2))
        node = BulletRigidBodyNode(kind)
        node.setMass(mass)
        node.addShape(shape)
        node.setTransform(TransformState.makePos(VBase3(position[0], position[1], position[2])))
        self.physics_world.attachRigidBody(node)
        return node

    def create_physics_object(self, position, kind, size, mass):
        if kind in self.kind_to_shape:
            return self.kind_to_shape[kind](position, size, kind, mass)
        return None

    def create_object(self, position, kind, size, mass, subclass):
        physics = self.create_physics_object(position, kind, size, mass)
        obj = subclass(position, kind, self.next_id, size, physics)
        self.next_id += 1
        self.game_objects[obj.id] = obj
        pub.sendMessage('create', game_object=obj)
        return obj

    def drop_box(self):
        position = [0, 0, 10]
        size = (1, 1, 1)
        mass = 5
        self.active_box = self.create_object(position, "fallingCrate", size, mass, GameObject)
        self.active_box.physics.setKinematic(True)
        self.swing_time = 0

    def move_active_box(self, dx):
        if self.active_box and not self.game_over:
            current_pos = self.active_box.physics.getTransform().getPos()
            new_x = current_pos.getX() + dx
            new_x = max(-5, min(5, new_x))
            self.active_box.physics.setTransform(
                TransformState.makePos(Vec3(new_x, current_pos.getY(), current_pos.getZ())))

    def release_box(self):
        if self.active_box and not self.game_over:
            current_pos = self.active_box.physics.getTransform().getPos()
            self.active_box.physics.setTransform(
                TransformState.makePos(Vec3(0, current_pos.getY(), current_pos.getZ()))
            )
            self.active_box.physics.setLinearVelocity(Vec3(0, 0, 0))
            self.active_box.physics.setAngularVelocity(Vec3(0, 0, 0))
            self.active_box.physics.setKinematic(False)
            self.active_box = None

    def tick(self, dt):
        if self.game_over:
            return

        for id in self.game_objects:
            self.game_objects[id].tick(dt)

        self.physics_world.do_physics(dt)

        if self.active_box and self.active_box.physics.isKinematic():
            self.swing_time += dt
            amplitude = 5
            period = 2.0
            swing_x = amplitude * math.sin(2 * math.pi * self.swing_time / period)
            self.active_box.physics.setTransform(
                TransformState.makePos(Vec3(swing_x, 0, 10))
            )

        if not self.active_box:
            self.drop_timer += dt
            if self.drop_timer >= self.drop_interval:
                self.drop_box()
                self.drop_timer = 0

        self.check_stack()

    def check_stack(self):
        for obj_id, obj in self.game_objects.items():
            if obj.kind == "fallingCrate" and not obj.physics.isKinematic():
                pos = obj.physics.getTransform().getPos()
                if pos.getZ() < -4 or abs(pos.getX()) > 6:
                    self.game_over = True
                    self.update_score_text()
                    print(f"Game Over! Final Score: {self.score}")
                    return
                if obj.physics.getLinearVelocity().length() < 0.1 and not obj.has_scored:
                    self.score += 1
                    obj.has_scored = True
                    self.update_score_text()
                    print(f"Score: {self.score}")

    def update_score_text(self):
        self.score_text.setText(f"Score: {self.score}")

    def load_world(self):
        self.create_object([0, 0, -3], "crate", (2, 4, 1), 10, GameObject)
        self.create_object([0, -20, 10], "player", (1, 0.5, 0.25, 0.5), 10, Player)
        self.create_object([0, 0, -5], "crate", (1000, 1000, 0.5), 0, GameObject)

    def get_property(self, key):
        if key in self.properties:
            return self.properties[key]

        return None

    def set_property(self, key, value):
        self.properties[key] = value

    def get_nearest(self, from_pt, to_pt):
        fx, fy, fz = from_pt
        tx, ty, tz = to_pt
        result = self.physics_world.rayTestClosest(Point3(fx, fy, fz), Point3(tx, ty, tz))
        return result

    def get_all_contacts(self, game_object):
        if game_object.physics:
            return self.physics_world.contactTest(game_object.physics).getContacts()
        return []
