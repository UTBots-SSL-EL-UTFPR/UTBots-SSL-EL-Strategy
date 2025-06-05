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

    delta_t = 0.1

    wheel_angles = [60, 135, 225, 300]

    wheel_radius = 0.027
    
    robot_radius = 0.09

    poses = [
        Pose2D(0.0, 1.0, 0.0),
        Pose2D(0.032, 0.999, 0.064),
        Pose2D(0.064, 0.998, 0.128),
        Pose2D(0.096, 0.995, 0.192),
        Pose2D(0.129, 0.992, 0.256),
        Pose2D(0.161, 0.988, 0.321),
        Pose2D(0.192, 0.982, 0.385),
        Pose2D(0.224, 0.975, 0.449),
        Pose2D(0.255, 0.967, 0.513),
        Pose2D(0.286, 0.958, 0.577),
        Pose2D(0.316, 0.948, 0.641),
        Pose2D(0.346, 0.936, 0.705),
        Pose2D(0.376, 0.924, 0.769),
        Pose2D(0.406, 0.911, 0.833),
        Pose2D(0.434, 0.896, 0.897),
        Pose2D(0.462, 0.881, 0.962),
        Pose2D(0.490, 0.865, 1.026),
        Pose2D(0.517, 0.848, 1.090),
        Pose2D(0.543, 0.829, 1.154),
        Pose2D(0.568, 0.810, 1.218),
        Pose2D(0.593, 0.790, 1.282),
        Pose2D(0.617, 0.770, 1.346),
        Pose2D(0.641, 0.748, 1.410),
        Pose2D(0.664, 0.726, 1.474),
        Pose2D(0.686, 0.703, 1.538),
        Pose2D(0.707, 0.679, 1.603),
        Pose2D(0.728, 0.654, 1.667),
        Pose2D(0.748, 0.629, 1.731),
        Pose2D(0.767, 0.603, 1.795),
        Pose2D(0.785, 0.576, 1.859),
        Pose2D(0.803, 0.549, 1.923),
        Pose2D(0.819, 0.521, 1.987),
        Pose2D(0.835, 0.493, 2.051),
        Pose2D(0.850, 0.464, 2.115),
        Pose2D(0.864, 0.435, 2.180),
        Pose2D(0.878, 0.405, 2.244),
        Pose2D(0.891, 0.375, 2.308),
        Pose2D(0.902, 0.344, 2.372),
        Pose2D(0.913, 0.313, 2.436),
        Pose2D(0.923, 0.282, 2.500),
        Pose2D(0.933, 0.250, 2.564),
        Pose2D(0.941, 0.218, 2.628),
        Pose2D(0.949, 0.186, 2.692),
        Pose2D(0.956, 0.154, 2.756),
        Pose2D(0.962, 0.121, 2.821),
        Pose2D(0.967, 0.088, 2.885),
        Pose2D(0.972, 0.056, 2.949),
        Pose2D(0.976, 0.023, 3.013),
        Pose2D(0.980, 0.000, 3.141)
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


    sender = CommandSenderSim()

    wheel_velocities = pipeline.run(poses)

    # envia cada comando de roda com intervalo delta_t
    for wheel_cmd in wheel_velocities:

        print(f"Wheel Speeds: w1={wheel_cmd[0]:.2f}, w2={wheel_cmd[1]:.2f}, w3={wheel_cmd[2]:.2f}, w4={wheel_cmd[3]:.2f}")
        builder.command_robots(
            id = 1,
            wheelsspeed=True,
            wheel1 = wheel_cmd[0],
            wheel2 = wheel_cmd[1],
            wheel3 = wheel_cmd[2],
            wheel4 = wheel_cmd[3]
        )

        start_time = time.time()

        while time.time() - start_time < delta_t:
            packet = builder.build()
            sender.send(packet)
            time.sleep(0.016)


    

if __name__ == "__main__":
    run_test("Without Ball", WithBallMotionMode())
    #run_test("with Ball", WithBallMotionMode())

