from .termination_condition_base import BaseTerminationCondition


class Timeout(BaseTerminationCondition):
    """
    Timeout
    Episode terminates if max_step steps have passed.
    """

    def __init__(self, config):
        super().__init__(config)
        self.max_steps = getattr(self.config, 'max_steps', 500)

    def get_termination(self, task, env, agent_id=0, info={}):
        """
        Return whether the episode should terminate.
        Terminate if max_step steps have passed

        Args:
            task: task instance
            env: environment instance

        Returns:
            (tuple): (done, success, info)
        """
        done = env.current_step >= self.max_steps
        if done:
            print(f"INFO: [{env.agent_names[agent_id]}] step limits!")
            info[f'{env.agent_names[agent_id]}_end_reason'] = 0  # normal
        success = False
        return done, success, info