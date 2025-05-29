from motion.without_ball_motion import WithoutBallMotionMode
from motion.with_ball_motion import WithBallMotionMode
from motion.trajectory_to_velocities import TrajectoryToVelocities
from motion.inverse_kinematics import InverseKinematics
from motion.motion_pipeline import MotionPipeline
from communication.command_builder import CommandBuilder
from communication.command_sender_sim import CommandSenderSim
from utils.pose2D import Pose2D
import time

def run_test(mode_name, motion_mode):
    print(f"\n-- Testand o {mode_name} --")

    # ---------------------- tudo do pipeline do calculo das velocidades ----------------------

    delta_t = 0.5

    wheel_angles = [60, 135, 225, 300]

    wheel_radius = 0.027
    
    robot_radius = 0.09

    poses = [
        Pose2D(0.0, 0.0,),
        Pose2D(0.5, 0.0,)
    ]

    pipeline = MotionPipeline(
        motion_mode, 
        delta_t, 
        wheel_angles,
        wheel_radius,
        robot_radius
    )

    # ---------------------- tudo do command sender ----------------------

    builder = CommandBuilder(team_color = "blue")

    builder.replace_robots(
        x = 0.0,
        y = 0.0,
        dir = 0.0,
        id = 1,
        yellowTeam = False,
        turnon = True
    )

    sender = CommandSenderSim()

    start_time = time.time()

    

if __name__ == "__main__":
    run_test("Without Ball", WithoutBallMotionMode())
    #run_test("with Ball", WithBallMotionMode())

