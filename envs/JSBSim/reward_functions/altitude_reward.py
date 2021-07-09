import numpy as np
from .reward_function_base import BaseRewardFunction


class AltitudeReward(BaseRewardFunction):
    """
    AltitudeReward
    Punish if current fighter doesn't satisfy some constraints. Typically negative.
    - Punishment of velocity when lower than safe altitude   (range: [-1, 0])
    - Punishment of altitude when lower than danger altitude (range: [-1, 0])

    NOTE:
    - env must implement `self.features` property
    """
    def __init__(self, config, is_potential=False, render=False):
        super().__init__(config, is_potential, render)
        self.reward_scale = getattr(self.config, 'altitude_reward_scale', 1.0)
        self.safe_altitude = getattr(self.config, 'safe_altitude', 4.0)         # km
        self.danger_altitude = getattr(self.config, 'danger_altitude', 3.5)     # km
        self.Kv = getattr(self.config, 'Kv', 0.2)     # mh

        self.reward_item_names = [self.__class__.__name__ + item for item in ['', '_Pv', '_PH']]

    def get_reward(self, task, env, agent_id):
        """
        Reward is the sum of all the punishments.

        Args:
            task: task instance
            env: environment instance

        Returns:
            (float): reward
        """
        ego_feature = env.features[env.agent_names[agent_id]]
        ego_x, ego_y, ego_z, ego_vx, ego_vy, ego_vz = ego_feature
        Pv = 0.
        if ego_z <= self.safe_altitude:
            Pv = -np.clip(ego_vz / self.Kv * (self.safe_altitude - ego_z) / self.safe_altitude, 0., 1.)
        PH = 0.
        if ego_z <= self.danger_altitude:
            PH = np.clip(ego_z / self.danger_altitude, 0., 1.) - 1. - 1.
        new_reward = Pv + PH
        return self._process(new_reward, render_items=(Pv, PH))