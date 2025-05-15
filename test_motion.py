from motion.without_ball_motion import WithoutBallMotionMode
from motion.with_ball_motion import WithBallMotionMode
from motion.trajectory_to_velocities import TrajectoryToVelocities
from motion.inverse_kinematics import InverseKinematics
from utils.pose2D import Pose2D

def run_test(mode_name, motion_mode):
    print(f"\n-- Testand o {mode_name} --")

    poses = [
        Pose2D(0.0, 0.0, 0.0),
        Pose2D(0.1, 0.2, 0.1),      #trajetoria de teste
        Pose2D(0.2, 0.3, 0.15),
        Pose2D(0.3, 0.35, 0.15),
    ]

if __name__ == "__main__":
    run_test("Without Ball", WithoutBallMotionMode())
    run_test("with Ball", WithBallMotionMode())

