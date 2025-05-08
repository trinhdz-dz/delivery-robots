import pygame
import os
import numpy as np

class VisualRenderer:
    def __init__(self, cell_size=40):
        # Khởi tạo Pygame
        pygame.init()
        
        # Kích thước ô
        self.cell_size = cell_size
        
        # Màu sắc
        self.colors = {
            'background': (255, 255, 255),  # Trắng
            'obstacle': (100, 100, 100),    # Xám
            'robot': (0, 0, 255),           # Xanh dương
            'package': (255, 0, 0),         # Đỏ
            'delivered': (0, 255, 0),       # Xanh lá
            'grid_line': (200, 200, 200)    # Xám nhạt
        }
        
        # Tạo font chữ
        self.font = pygame.font.SysFont('Arial', 12)
        
        # Bề mặt vẽ
        self.screen = None
        
    def load_images(self, images_dir='images'):
        """Tải các hình ảnh từ thư mục"""
        self.images = {
            'robot': pygame.transform.scale(pygame.image.load(os.path.join(images_dir, 'robot.png')), (self.cell_size, self.cell_size)),
            'package': pygame.transform.scale(pygame.image.load(os.path.join(images_dir, 'waiting.png')), (self.cell_size, self.cell_size)),
            'delivered': pygame.transform.scale(pygame.image.load(os.path.join(images_dir, 'delivered.png')), (self.cell_size, self.cell_size)),
            'obstacle': pygame.transform.scale(pygame.image.load(os.path.join(images_dir, 'brick.png')), (self.cell_size, self.cell_size)),
            'empty': pygame.transform.scale(pygame.image.load(os.path.join(images_dir, 'line.png')), (self.cell_size, self.cell_size)),
        }
    
    def init_display(self, grid):
        """Khởi tạo màn hình với kích thước dựa trên lưới"""
        n_rows = len(grid)
        n_cols = len(grid[0])
        
        # Kích thước màn hình
        screen_width = n_cols * self.cell_size
        screen_height = n_rows * self.cell_size
        
        # Tạo màn hình
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Multi-Agent Robot Delivery Simulation')
        
    def render(self, env):
        """Hiển thị môi trường bằng hình ảnh"""
        if self.screen is None:
            self.init_display(env.grid)
            
        # Xóa màn hình
        self.screen.fill(self.colors['background'])
        
        # Vẽ lưới
        for r in range(env.n_rows):
            for c in range(env.n_cols):
                # Vẽ đường lưới
                pygame.draw.rect(
                    self.screen, 
                    self.colors['grid_line'], 
                    (c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size), 
                    1
                )
                
                # Vẽ chướng ngại vật
                if env.grid[r][c] == 1:
                    pygame.draw.rect(
                        self.screen, 
                        self.colors['obstacle'], 
                        (c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                    )
        
        # Vẽ gói hàng
        for package in env.packages:
            if package.status == 'waiting':
                # Gói hàng đang chờ
                r, c = package.start
                pygame.draw.rect(
                    self.screen, 
                    self.colors['package'], 
                    (c * self.cell_size + 5, r * self.cell_size + 5, self.cell_size - 10, self.cell_size - 10)
                )
                # Hiển thị ID gói hàng
                text = self.font.render(f'P{package.package_id}', True, (0, 0, 0))
                self.screen.blit(text, (c * self.cell_size + 10, r * self.cell_size + 10))
            
            elif package.status == 'delivered':
                # Gói hàng đã giao
                r, c = package.target
                pygame.draw.rect(
                    self.screen, 
                    self.colors['delivered'], 
                    (c * self.cell_size + 5, r * self.cell_size + 5, self.cell_size - 10, self.cell_size - 10)
                )
                # Hiển thị ID gói hàng
                text = self.font.render(f'E{package.package_id}', True, (0, 0, 0))
                self.screen.blit(text, (c * self.cell_size + 10, r * self.cell_size + 10))
        
        # Vẽ robot
        for i, robot in enumerate(env.robots):
            r, c = robot.position
            
            # Đổi màu robot nếu đang mang gói hàng (màu vàng)
            robot_color = (255, 215, 0) if robot.carrying > 0 else self.colors['robot']
            
            # Vẽ robot
            pygame.draw.circle(
                self.screen,
                robot_color,
                (c * self.cell_size + self.cell_size // 2, r * self.cell_size + self.cell_size // 2),
                self.cell_size // 3
            )
            
            # Hiển thị ID robot
            text = self.font.render(f'R{i}', True, (255, 255, 255))
            self.screen.blit(text, (c * self.cell_size + self.cell_size // 2 - 5, r * self.cell_size + self.cell_size // 2 - 5))
            
            # Nếu robot đang mang gói hàng
            if robot.carrying > 0:
                text = self.font.render(f'P{robot.carrying}', True, (0, 0, 0))
                self.screen.blit(text, (c * self.cell_size + self.cell_size // 2 - 5, r * self.cell_size + self.cell_size // 2 + 5))
        # Hiển thị thông tin thời gian
        time_text = self.font.render(f'Time Step: {env.t}', True, (0, 0, 0))
        self.screen.blit(time_text, (10, 10))
        
        # Cập nhật màn hình
        pygame.display.flip()
        
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()