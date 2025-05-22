from env import Environment
from greedyagent import GreedyAgents as Agents
from visualize import VisualRenderer
import numpy as np
import time

if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Multi-Agent Reinforcement Learning for Delivery")
    parser.add_argument("--num_agents", type=int, default=5, help="Number of agents")
    parser.add_argument("--n_packages", type=int, default=10, help="Number of packages")
    parser.add_argument("--max_steps", type=int, default=100, help="Maximum number of steps per episode")
    parser.add_argument("--seed", type=int, default=2025, help="Random seed for reproducibility")
    parser.add_argument("--max_time_steps", type=int, default=1000, help="Maximum time steps for the environment")
    parser.add_argument("--map", type=str, default="map.txt", help="Map name")
    parser.add_argument("--visual", action="store_true", help="Use visual rendering")

    args = parser.parse_args()
    np.random.seed(args.seed)

    env = Environment(map_file=args.map, max_time_steps=args.max_time_steps,
                      n_robots=args.num_agents, n_packages=args.n_packages,
                      seed = args.seed)
    
    # Khởi tạo renderer nếu cần
    renderer = None
    if args.visual:
        renderer = VisualRenderer(cell_size=40)
        try:
            renderer.load_images(images_dir='E:/Năm 3 Kỳ II/Học tăng cường/Cuối Kỳ/marl-delivery(new)/delivery-robots/image')
            print("Images loaded successfully")
        except:
            print("Warning: Could not load images, using default shapes")
    
    state = env.reset()
    agents = Agents()
    agents.init_agents(state)
    print(state)
    
    # Hiển thị khung hình đầu tiên
    if renderer:
        renderer.render(env)
    else:
        env.render()  # Text-based rendering
    
    done = False
    t = 0
    while not done:
        actions = agents.get_actions(state)
        next_state, reward, done, infos = env.step(actions)
        state = next_state
        
        # Hiển thị khung hình hiện tại
        if renderer:
            renderer.render(env)
            time.sleep(0.5)  # Delay để người dùng có thể theo dõi
        else:
            env.render()  # Text-based rendering
        
        t += 1

    print("Episode finished")
    print("Total reward:", infos['total_reward'])
    print("Total time steps:", infos['total_time_steps'])
    
    # Giữ cửa sổ hiển thị cho đến khi người dùng đóng
    if renderer:
        import pygame
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
        pygame.quit()