import omni.kit.commands
import omni.usd
import omni.timeline
import omni.physx
import carb
import random
import json
import uuid
import asyncio
from pxr import Gf, UsdGeom, UsdPhysics, Usd, Sdf
from omni.physx import acquire_physx_interface

class PhysicsDataGenerator:
    def __init__(self, num_scenarios=10, timesteps=100, dt=0.01):
        self.num_scenarios = num_scenarios
        self.timesteps = timesteps
        self.dt = dt
        self.stage = omni.usd.get_context().get_stage()
        self.timeline = omni.timeline.get_timeline_interface()
        self.physx = acquire_physx_interface()

    def create_primitive(self, prim_type, position, size):
        prim_path = f"/World/{prim_type}_{uuid.uuid4().hex[:8]}"
        omni.kit.commands.execute('CreatePrimCommand',
            prim_type=prim_type,
            prim_path=prim_path)
        
        prim = self.stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        
        # Get existing xform ops
        xform_ops = xformable.GetOrderedXformOps()
        
        # Set translate
        translate_op = next((op for op in xform_ops if op.GetOpType() == UsdGeom.XformOp.TypeTranslate), None)
        if translate_op:
            translate_op.Set(position)
        
        # Set scale
        scale_op = next((op for op in xform_ops if op.GetOpType() == UsdGeom.XformOp.TypeScale), None)
        if scale_op:
            scale_op.Set(Gf.Vec3d(size[0], size[1], size[2]))
        
        return prim_path

    def add_physics(self, prim_path, mass, is_kinematic=False):
        prim = self.stage.GetPrimAtPath(prim_path)
        
        # Add RigidBody
        rigid_body = UsdPhysics.RigidBodyAPI.Apply(prim)
        if is_kinematic:
            rigid_body.CreateKinematicEnabledAttr().Set(True)
        else:
            # Set mass using MassAPI
            mass_api = UsdPhysics.MassAPI.Apply(prim)
            mass_api.CreateMassAttr().Set(mass)
        
        # Add CollisionAPI
        UsdPhysics.CollisionAPI.Apply(prim)
        
        # Set the collision approximation based on prim type
        prim_type = prim.GetTypeName()
        if prim_type == "Cube":
            prim.CreateAttribute("physics:approximation", Sdf.ValueTypeNames.Token).Set("box")
        elif prim_type == "Sphere":
            prim.CreateAttribute("physics:approximation", Sdf.ValueTypeNames.Token).Set("sphere")
        elif prim_type == "Cylinder":
            prim.CreateAttribute("physics:approximation", Sdf.ValueTypeNames.Token).Set("capsule")

    def generate_scenario(self):
        # Clear existing prims
        omni.kit.commands.execute('DeletePrims',
            paths=["/World"],
            destructive=False)

        # Create ground cube (large and lowered)
        ground = self.create_primitive("Cube", Gf.Vec3d(0, -10, 0), Gf.Vec3d(100, 1, 100))
        self.add_physics(ground, 0, is_kinematic=True)  # Static and kinematic ground

        # Create random objects
        objects = []
        for _ in range(random.randint(2, 5)):
            prim_type = random.choice(["Sphere", "Cube", "Cylinder"])
            position = Gf.Vec3d(random.uniform(-5, 5), random.uniform(5, 10), random.uniform(-5, 5))
            size = random.uniform(0.5, 2)
            prim_path = self.create_primitive(prim_type, position, Gf.Vec3d(size, size, size))
            self.add_physics(prim_path, random.uniform(1, 10))
            objects.append(prim_path)

        return objects

    def get_object_state(self, prim_path):
        prim = self.stage.GetPrimAtPath(prim_path)
        xformable = UsdGeom.Xformable(prim)
        
        world_transform = xformable.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        position = world_transform.ExtractTranslation()
        rotation = world_transform.ExtractRotation().GetQuaternion()

        return {
            "id": prim_path.split('/')[-1],
            "type": prim.GetTypeName().lower(),
            "position": [float(position[0]), float(position[1]), float(position[2])],
            "rotation": [float(rotation.GetReal()), float(rotation.GetImaginary()[0]), float(rotation.GetImaginary()[1]), float(rotation.GetImaginary()[2])]
        }

    async def run_simulation(self, progress_callback=None, status_callback=None):
        scenarios_data = []

        for scenario in range(self.num_scenarios):
            if status_callback:
                status_callback(f"Generating scenario {scenario + 1}/{self.num_scenarios}")
            
            objects = self.generate_scenario()
            scenario_data = {
                "scenario_id": str(uuid.uuid4()),
                "timesteps": []
            }

            self.timeline.play()
            
            start_time = self.timeline.get_current_time()
            end_time = start_time + self.timesteps * self.dt

            for step in range(self.timesteps):
                current_time = self.timeline.get_current_time()
                self.timeline.set_current_time(current_time + self.dt)
                
                timestep_data = {
                    "time": float(current_time - start_time),
                    "objects": [self.get_object_state(obj) for obj in objects]
                }
                scenario_data["timesteps"].append(timestep_data)

                # Update progress
                if progress_callback:
                    progress = (scenario * self.timesteps + step) / (self.num_scenarios * self.timesteps)
                    progress_callback(progress)

                # Yield control to allow UI updates
                await asyncio.sleep(0)

            self.timeline.stop()
            scenarios_data.append(scenario_data)
            
            # Print progress
            if status_callback:
                status_callback(f"Scenario {scenario + 1}/{self.num_scenarios} complete")

        return scenarios_data

    async def save_data(self, data, filename="physics_data.json"):
        def write_to_file():
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
        
        # Run the file writing in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, write_to_file)
