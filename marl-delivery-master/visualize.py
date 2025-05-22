import pygame
import os
import numpy as np
from pygame import mixer

class VisualRenderer:
    def __init__(self, cell_size=40):
        # Khởi tạo Pygame
        pygame.init()
        pygame.mixer.init()
        
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

        # Biến để theo dõi trạng thái âm thanh
        self.sound_playing = False
        self.delivery_sound = None
        
        # Biến để theo dõi robot đang giao hàng
        self.robots_delivering = set()
        
    def load_images(self, images_dir='images'):
        """Tải các hình ảnh từ thư mục"""
        # Lấy đường dẫn tuyệt đối của thư mục hiện tại
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Tạo đường dẫn tuyệt đối đến thư mục hình ảnh và âm thanh
        images_path = os.path.join(current_dir, images_dir)
        sounds_path = os.path.join(current_dir, '../sounds')
        
        print(f"Tìm hình ảnh tại: {images_path}")
        
        try:
            self.images = {
                'robot': pygame.transform.scale(pygame.image.load(os.path.join(images_path, 'robot.png')), (self.cell_size, self.cell_size)),
                'package': pygame.transform.scale(pygame.image.load(os.path.join(images_path, 'waiting.png')), (self.cell_size, self.cell_size)),
                'delivered': pygame.transform.scale(pygame.image.load(os.path.join(images_path, 'delivered.png')), (self.cell_size, self.cell_size)),
                'obstacle': pygame.transform.scale(pygame.image.load(os.path.join(images_path, 'brick.png')), (self.cell_size, self.cell_size)),
                'empty': pygame.transform.scale(pygame.image.load(os.path.join(images_path, 'line.png')), (self.cell_size, self.cell_size)),
                'delivering': pygame.transform.scale(pygame.image.load(os.path.join(images_path, 'delivering.png')), (self.cell_size, self.cell_size)),
                'delivered_robot': pygame.transform.scale(pygame.image.load(os.path.join(images_path, 'delivered_robot.png')), (self.cell_size, self.cell_size)),
            }
        except Exception as e:
            print(f"Lỗi khi tải hình ảnh: {e}")
        
        # Tải âm thanh giao hàng
        try:
            # Đường dẫn đầy đủ tới file âm thanh
            delivering_path = os.path.join(sounds_path, 'delivering.mp3')
            
            pygame.mixer.init()
            self.delivery_sound = pygame.mixer.Sound(delivering_path)
            print(f"Âm thanh được tải từ: {delivering_path}")
        except Exception as e:
            print(f"Không thể tải âm thanh: {e}")
            self.delivery_sound = None
    
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
        
        # Vẽ lưới và nền
        for r in range(env.n_rows):
            for c in range(env.n_cols):
                # Vẽ nền trống cho mỗi ô
                self.screen.blit(self.images['empty'], (c * self.cell_size, r * self.cell_size))
                
                # Vẽ chướng ngại vật
                if env.grid[r][c] == 1:
                    self.screen.blit(self.images['obstacle'], (c * self.cell_size, r * self.cell_size))
        
        # Vẽ gói hàng
        for package in env.packages:
            if package.status == 'waiting':
                # Gói hàng đang chờ
                r, c = package.start
                self.screen.blit(self.images['package'], (c * self.cell_size, r * self.cell_size))
                # Hiển thị ID gói hàng
                text = self.font.render(f'P{package.package_id}', True, (0, 0, 0))
                self.screen.blit(text, (c * self.cell_size + 10, r * self.cell_size + 10))
            
            elif package.status == 'delivered':
                # Gói hàng đã giao
                r, c = package.target
                self.screen.blit(self.images['delivered'], (c * self.cell_size, r * self.cell_size))
                # Hiển thị ID gói hàng
                text = self.font.render(f'E{package.package_id}', True, (0, 0, 0))
                self.screen.blit(text, (c * self.cell_size + 10, r * self.cell_size + 10))
        
        # Kiểm tra xem có robot nào đang giao hàng không
        current_delivering = set()
        # Vẽ robot
        for i, robot in enumerate(env.robots):
            r, c = robot.position
            
            # Kiểm tra xem robot có đứng ở ô đã giao hàng không
            standing_on_delivered_package = False
            for package in env.packages:
                if package.status == 'delivered' and package.target == robot.position:
                    standing_on_delivered_package = True
                    break
            
            # Nếu robot đang mang gói hàng
            if robot.carrying > 0:
                text = self.font.render(f'P{robot.carrying}', True, (0, 0, 0))
                #vẽ robot dang giao hàng
                self.screen.blit(self.images['delivering'], (c * self.cell_size, r * self.cell_size))
                self.screen.blit(text, (c * self.cell_size + self.cell_size // 2 - 5, r * self.cell_size + self.cell_size // 2 + 5))
                # Thêm robot vào danh sách đang giao hàng
                current_delivering.add(i)
            # Nếu robot đang đứng trên ô đã giao hàng
            elif standing_on_delivered_package:
                self.screen.blit(self.images['delivered_robot'], (c * self.cell_size, r * self.cell_size))
            # Trường hợp robot bình thường
            else:
                self.screen.blit(self.images['robot'], (c * self.cell_size, r * self.cell_size))
            
            # Hiển thị ID robot
            text = self.font.render(f'R{i}', True, (255, 255, 255))
            self.screen.blit(text, (c * self.cell_size + self.cell_size // 2 - 5, r * self.cell_size + self.cell_size // 2 - 5))
        
        # Xử lý âm thanh giao hàng
        if self.delivery_sound:
            # Nếu có robot đang giao hàng và âm thanh chưa phát
            if current_delivering and not self.sound_playing:
                self.delivery_sound.play(-1)  # -1 cho phép lặp âm thanh liên tục
                self.sound_playing = True
            # Nếu không có robot nào giao hàng nhưng âm thanh đang phát
            elif not current_delivering and self.sound_playing:
                self.delivery_sound.stop()
                self.sound_playing = False
        
        # Cập nhật danh sách robot đang giao hàng
        self.robots_delivering = current_delivering
        info_font = pygame.font.SysFont('Arial', 16, bold=True)
        reward_text = info_font.render(f'Rewards: {env.total_reward:.2f}', True, (255, 255, 255))
        time_text = info_font.render(f'Time: {env.t}', True, (255, 255, 255))
        
        # Đếm số gói hàng đã giao
        delivered_count = sum(1 for package in env.packages if package.status == 'delivered')
        delivered_text = info_font.render(f'Delivered: {delivered_count}/{len(env.packages)}', True, (255, 255, 255))
        # Vẽ nền đen mờ để chữ dễ đọc
        overlay = pygame.Surface((env.n_cols * self.cell_size, 30))
        overlay.set_alpha(180)  # độ mờ
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Vẽ chữ
        self.screen.blit(reward_text, (10, 5))
        self.screen.blit(delivered_text, (env.n_cols * self.cell_size // 2 - 30, 5))
        self.screen.blit(time_text, (env.n_cols * self.cell_size - 70, 5))
        
        # Cập nhật màn hình
        pygame.display.flip()
        
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()