from screeninfo import get_monitors

monitor = get_monitors()[0]  # Lấy màn hình chính (có thể là [1] nếu muốn lấy màn hình khác)
screen_width = monitor.width
screen_height = monitor.height
print(screen_width, screen_height)