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

    delta_t = 0.1  # intervalo de tempo entre cada pose (em segundos)

    wheel_angles = [60, 135, 225, 300]

    wheel_radius = 0.027
    
    robot_radius = 0.09

    poses = [
Pose2D(-1.4300000000000002,-0.9,0),
Pose2D(-1.4300000000000002,-0.88,0),
Pose2D(-1.4300000000000002,-0.86,0),
Pose2D(-1.4300000000000002,-0.84,0),
Pose2D(-1.4300000000000002,-0.82,0),
Pose2D(-1.4300000000000002,-0.8,0),
Pose2D(-1.4100000000000001,-0.78,0),
Pose2D(-1.3900000000000001,-0.76,0),
Pose2D(-1.37,-0.74,0),
Pose2D(-1.37,-0.72,0),
Pose2D(-1.35,-0.7,0),
Pose2D(-1.35,-0.68,0),
Pose2D(-1.35,-0.66,0),
Pose2D(-1.35,-0.64,0),
Pose2D(-1.35,-0.62,0),
Pose2D(-1.35,-0.6,0),
Pose2D(-1.35,-0.58,0),
Pose2D(-1.35,-0.56,0),
Pose2D(-1.35,-0.54,0),
Pose2D(-1.35,-0.52,0),
Pose2D(-1.35,-0.5,0),
Pose2D(-1.35,-0.48,0),
Pose2D(-1.35,-0.45999999999999996,0),
Pose2D(-1.35,-0.43999999999999995,0),
Pose2D(-1.35,-0.41999999999999993,0),
Pose2D(-1.35,-0.3999999999999999,0),
Pose2D(-1.35,-0.3799999999999999,0),
Pose2D(-1.35,-0.3600000000000001,0),
Pose2D(-1.33,-0.3400000000000001,0),
Pose2D(-1.31,-0.32000000000000006,0),
Pose2D(-1.29,-0.30000000000000004,0),
Pose2D(-1.27,-0.28,0),
Pose2D(-1.25,-0.26,0),
Pose2D(-1.23,-0.24,0),
Pose2D(-1.21,-0.21999999999999997,0),
Pose2D(-1.19,-0.19999999999999996,0),
Pose2D(-1.17,-0.17999999999999994,0),
Pose2D(-1.15,-0.15999999999999992,0),
Pose2D(-1.13,-0.1399999999999999,0),
Pose2D(-1.11,-0.1200000000000001,0),
Pose2D(-1.09,-0.10000000000000009,0),
Pose2D(-1.07,-0.08000000000000007,0),
Pose2D(-1.05,-0.06000000000000005,0),
Pose2D(-1.03,-0.040000000000000036,0),
Pose2D(-1.01,-0.020000000000000018,0),
Pose2D(-0.99,0.0,0),
Pose2D(-0.97,0.020000000000000018,0),
Pose2D(-0.97,0.040000000000000036,0),
Pose2D(-0.97,0.06000000000000005,0),
Pose2D(-0.95,0.08000000000000007,0),
Pose2D(-0.95,0.10000000000000009,0),
Pose2D(-0.95,0.1200000000000001,0),
Pose2D(-0.95,0.1399999999999999,0),
Pose2D(-0.95,0.15999999999999992,0),
Pose2D(-0.95,0.17999999999999994,0),
Pose2D(-0.95,0.19999999999999996,0),
Pose2D(-0.95,0.21999999999999997,0),
Pose2D(-0.95,0.24,0),
Pose2D(-0.95,0.26,0),
Pose2D(-0.95,0.28,0),
Pose2D(-0.95,0.30000000000000004,0),
Pose2D(-0.95,0.32000000000000006,0),
Pose2D(-0.95,0.3400000000000001,0),
Pose2D(-0.9299999999999999,0.3600000000000001,0),
Pose2D(-0.9099999999999999,0.3799999999999999,0),
Pose2D(-0.8899999999999999,0.3999999999999999,0),
Pose2D(-0.8700000000000001,0.41999999999999993,0),
Pose2D(-0.8500000000000001,0.43999999999999995,0),
Pose2D(-0.8300000000000001,0.45999999999999996,0),
Pose2D(-0.81,0.48,0),
Pose2D(-0.79,0.5,0),
Pose2D(-0.79,0.52,0),
Pose2D(-0.79,0.54,0),
Pose2D(-0.77,0.56,0),
Pose2D(-0.77,0.5800000000000001,0),
Pose2D(-0.77,0.6000000000000001,0),
Pose2D(-0.75,0.6200000000000001,0),
Pose2D(-0.73,0.6400000000000001,0),
Pose2D(-0.71,0.6600000000000001,0),
Pose2D(-0.69,0.6800000000000002,0),
Pose2D(-0.6699999999999999,0.7000000000000002,0),
Pose2D(-0.6499999999999999,0.7200000000000002,0),
Pose2D(-0.6299999999999999,0.7400000000000002,0),
Pose2D(-0.6100000000000001,0.7599999999999998,0),
Pose2D(-0.5900000000000001,0.7799999999999998,0),
Pose2D(-0.5700000000000001,0.7999999999999998,0),
Pose2D(-0.55,0.8199999999999998,0),
Pose2D(-0.53,0.8399999999999999,0),
Pose2D(-0.51,0.8599999999999999,0),
Pose2D(-0.49,0.8799999999999999,0),
Pose2D(-0.47,0.8999999999999999,0),
Pose2D(-0.44999999999999996,0.9199999999999999,0),
Pose2D(-0.42999999999999994,0.94,0),
Pose2D(-0.4099999999999999,0.96,0),
Pose2D(-0.3899999999999999,0.98,0),
Pose2D(-0.3700000000000001,1.0,0),
Pose2D(-0.3500000000000001,1.02,0),
Pose2D(-0.33000000000000007,1.04,0),
Pose2D(-0.31000000000000005,1.06,0),
Pose2D(-0.29000000000000004,1.08,0),
Pose2D(-0.27,1.1,0),
Pose2D(-0.25,1.12,0),
Pose2D(-0.22999999999999998,1.1400000000000001,0),
Pose2D(-0.20999999999999996,1.1600000000000001,0),
Pose2D(-0.18999999999999995,1.1800000000000002,0),
Pose2D(-0.16999999999999993,1.2000000000000002,0),
Pose2D(-0.1499999999999999,1.2200000000000002,0),
Pose2D(-0.1299999999999999,1.2400000000000002,0),
Pose2D(-0.10999999999999988,1.2599999999999998,0),
Pose2D(-0.08999999999999986,1.2799999999999998,0)
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
    run_test("Without Ball", WithoutBallMotionMode())
    #run_test("with Ball", WithBallMotionMode())

