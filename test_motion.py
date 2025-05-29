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

    delta_t = 0.4

    wheel_angles = [60, 135, 225, 300]

    wheel_radius = 0.027
    
    robot_radius = 0.09

    poses = [
        Pose2D(0.0, 0.0, 0.0),        # Início, voltado para a frente (Eixo X+)
        Pose2D(0.2, 0.1, 0.5),        # Começa curva para a esquerda
        Pose2D(0.3, 0.3, 1.0),        # Continua a curvar
        Pose2D(0.2, 0.5, 1.5),        # Passando do ponto médio
        Pose2D(0.0, 0.6, 3.14)        # Final: voltado para trás (180°)
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

