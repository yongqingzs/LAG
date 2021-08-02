from envs.JSBSim.envs.selfplay_env import SelfPlayEnv
from envs.env_wrappers import DummyVecEnv
from algorithms.ppo_data_collectors import SelfPlayDataCollector
from algorithms.ppo_training_agent import Trainer
from algorithms.ppo_AC import ActorCritic
from algorithms.ppo_args import Config
import torch
import os
import argparse
import signal
import random
import numpy as np

def make_train_env(num_env):
    return DummyVecEnv([SelfPlayEnv for _ in range(num_env)])

def main():
    signal.signal(signal.SIGINT, exit)
    signal.signal(signal.SIGTERM, exit)
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="JSBSim")
    parser.add_argument("--task", default="selfplay")
    parser.add_argument("--version", default='v0')
    parser.add_argument("--gpu-id", default=None, type=int)
    parser.add_argument("--seed", default=1, type=int)
    args = parser.parse_args()

    np.random.seed(args.seed)
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = True
    rootpath = f'./results/{args.env}_{args.task}_{args.version}'
    if not os.path.exists(rootpath):
        os.makedirs(f'{rootpath}/models')

    args_ppo = Config(env=SelfPlayEnv())
    if args.gpu_id is None:
        args_ppo.device = torch.device('cpu')
    else:
        args_ppo.device = torch.device(f'cuda:{args.gpu_id}')
    hyper_params = dict()
    hyper_params['reward_hyper'] = [0.]
    hyper_params['ppo_hyper'] = [1., 1.]
    collector = SelfPlayDataCollector(args_ppo)
    trainer = Trainer(args_ppo)
    agent = ActorCritic(args_ppo, agent_idx=0)
    agent.save_model(rootpath, None, epoch_t=0, args=args)
    rewards_list = []
    for itr in range(1000):
        res = collector.collect_data(ego_net_params=torch.load(f"{rootpath}/models/agent{0}_latest.pt")['model_state_dict'],
                                     enm_net_params=torch.load(f"{rootpath}/models/agent{0}_latest.pt")['model_state_dict'],
                                     hyper_params=hyper_params,
                                     agent_id=0)
        status, sample_data = res
        params = trainer.update_agent(agent_id=0,
                                      agent_params=torch.load(f"{rootpath}/models/agent{0}_latest.pt"),
                                      buffer_data_lists=[sample_data], hyper_params=hyper_params)
        torch.save(params, f"{rootpath}/models/agent{0}_latest.pt")
        torch.save(params, f"{rootpath}/models/agent{0}_history{itr + 1}.pt")
        rewards = collector.evaluate_with_baseline(ego_net_params=torch.load(f"{rootpath}/models/agent{0}_latest.pt"),
                                                   enm_net_params=torch.load(f"{rootpath}/models/agent{0}_latest.pt"),
                                                   eval_num=10,
                                                   )
        rewards_list.append(rewards)
        np.save(f'{rootpath}/learning_reward_{args.version}', np.asarray(rewards_list))


if __name__ == '__main__':
    main()