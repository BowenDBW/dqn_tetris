# run_model.py
import sys
import torch
import pygame
from tetris import Tetris
from dqn_agent import DQNAgent
import time


def test_model(model_path, render_delay=0.05, num_episodes=5):
    """Test trained model with visualization"""
    # Initialize
    env = Tetris(tick_rate=10000)

    # 修复后的Agent初始化
    agent = DQNAgent(
        state_size=env.get_state_size(),
        n_neurons=[32, 32, 32],
        epsilon_stop_episode=1,
        mem_size=1,
        epsilon_min=0.1,
        epsilon=0.0
    )
    agent.model.load_state_dict(
        torch.load(model_path, map_location=torch.device('cpu')))
    agent.epsilon = 0.0
    agent.epsilon_decay = 0.0

    pygame.init()
    font = pygame.font.SysFont('Arial', 25)

    for episode in range(1, num_episodes + 1):
        state = env.reset()
        done = False
        total_reward = 0
        start_time = time.time()

        while not done:
            # 处理退出事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # 渲染当前状态（包括正在下落的方块）
            env.render()
            score_text = font.render(f'Ep {episode} | Score: {total_reward}', True, (255, 255, 255))
            pygame.display.get_surface().blit(score_text, (10, 10))
            pygame.display.flip()

            # 获取动作
            next_states = env.get_next_states()
            if not next_states:
                done = True
                break

            states = [torch.FloatTensor(s) for s in next_states.values()]
            best_idx = agent.best_state(states)
            best_action = list(next_states.keys())[best_idx]

            # 执行动作并启用渲染
            reward, done = env.play(best_action[0], best_action[1], render=True, render_delay=render_delay)
            total_reward += reward

    pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_model.py path_to_model.pth [render_delay] [num_episodes]")
        sys.exit(1)

    model_path = sys.argv[1]
    render_delay = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
    num_episodes = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    test_model(model_path, render_delay, num_episodes)