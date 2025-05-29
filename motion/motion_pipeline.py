from motion.motion_mode import MotionMode
from motion.trajectory_to_velocities import TrajectoryToVelocities
from motion.inverse_kinematics import InverseKinematics
from utils.pose2D import Pose2D
from typing import List

class MotionPipeline:
    '''
    pipeline completo para converter uma tragetória definida
    como uma lista de pose2D em velocidades individuais para
    cada uma das 4 rodas do robo

    ainda precisa do delta_t entre cada pose 2d para calcular(SUJEITO A MUDANCAS!!!!!!!!!)
    '''

    def __init__(
            self,
            motion_mode: MotionMode,
            delta_t: float,
            wheel_angles: List[float],
            wheel_radius: float,
            robot_radius: float
    ):
        self.trajectory_converter = TrajectoryToVelocities(delta_t, motion_mode)
        self.inverse_kinematics = InverseKinematics(wheel_angles, wheel_radius, robot_radius)

    def run(self, poses: List[Pose2D]) -> List[List[float]]:
        #faz o pipeline completo do calculo 
        wheel_velocities = []
        robot_velocities = self.trajectory_converter.convert(poses)

        for vx, vy, omega in robot_velocities:
            wheel_velocities.append(self.inverse_kinematics.compute(vx, vy, omega))

        return wheel_velocities    
    
    '''
    cada wheel_velocities[i] representa a velocidade q o robo
    deve aplicar por delta_t segundos para ir da poses[i] ate 
    a poses[i+1]
    '''
    