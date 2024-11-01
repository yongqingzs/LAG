#!/bin/sh
env="MultipleCombat"
scenario="2v2/NoWeapon/HierarchySelfplay"
algo="mappo"
exp="v1"
seed=0
user_name="cc"
use_wandb=true  # 设置为 true 或 false 以启用或禁用 wandb
wandb_name="fh_jsbsim"
num_env_steps=1e8
outdir="/workspace/outputs/"  # "./results"

echo "env is ${env}, scenario is ${scenario}, algo is ${algo}, exp is ${exp}, seed is ${seed}"
cmd=CUDA_VISIBLE_DEVICES=0 python train/train_jsbsim.py \
    --env-name ${env} --algorithm-name ${algo} --scenario-name ${scenario} --experiment-name ${exp} \
    --seed ${seed} --n-training-threads 1 --n-rollout-threads 32 --cuda --log-interval 1 --save-interval 1 \
    --num-mini-batch 5 --buffer-size 3000 --num-env-steps ${num_env_steps} \
    --lr 3e-4 --gamma 0.99 --ppo-epoch 4 --clip-params 0.2 --max-grad-norm 2 --entropy-coef 1e-3 \
    --hidden-size "128 128" --act-hidden-size "128 128" --recurrent-hidden-size 128 --recurrent-hidden-layers 1 --data-chunk-length 8 \
    --use-selfplay --selfplay-algorithm "fsp" --n-choose-opponents 1 \
    --use-eval --n-eval-rollout-threads 1 --eval-interval 1 --eval-episodes 1 \
    --user-name ${user_name} \
    --outdir ${outdir}

if [ "$use_wandb" = true ]; then
    cmd="$cmd --use-wandb --wandb-name ${wandb_name}"
fi

eval $cmd