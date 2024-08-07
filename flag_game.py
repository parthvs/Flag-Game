import cv2
import numpy as np
import pygame
import os
import random

GAME_LENGTH = int(input("Enter no of flags(less than 250)"))
current_directory = os.getcwd()
folder = os.path.join(current_directory, "FLAGS")
flag_list = []

for i in os.scandir(folder):
    if i.is_file():
        temp=[]
        temp.append(i.name[:-4])
        temp.append(folder + '\\' + i.name)
        flag_list.append(temp)
def resize_image(img, scale_factor):
    """Resize the image by the given scale factor."""
    original_height, original_width = img.shape[:2]
    new_height = int(original_height * scale_factor)
    new_width = int(original_width * scale_factor)
    return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LINEAR)#, (original_width, original_height)


def pixelate(image_path, pixel_size):
    img = cv2.imread(image_path)

    img = resize_image(img, 0.2)
    height, width, channels = img.shape

    # Pad the image to ensure the dimensions are divisible by pixel_size
    pad_x = (pixel_size - width % pixel_size) % pixel_size
    pad_y = (pixel_size - height % pixel_size) % pixel_size
    img = np.pad(img, ((0, pad_y), (0, pad_x), (0, 0)), mode='constant', constant_values=0)

    # Calculate the mean of each block
    h, w, c = img.shape
    blocks = np.mean(img.reshape(h // pixel_size, pixel_size, -1, pixel_size, c), axis=(1, 3))

    # Repeat each block to create the pixelated effect
    output = np.repeat(np.repeat(blocks, pixel_size, axis=1), pixel_size, axis=0)

    # Crop the image to the original size
    output = convert_to_pygame(output[:height, :width].astype("uint8"))
    
    return output

def convert_to_pygame(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR (OpenCV) to RGB (Pygame)
    return pygame.image.frombuffer(img.tobytes(), img.shape[1::-1], "RGB")


game_list = random.sample(flag_list,GAME_LENGTH)


pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
font = pygame.font.Font(None, 30)  # None uses the default font; you can specify a font file

text_color = (255, 255, 255)  # White color

running = True
iterations = 0

start = pygame.time.get_ticks()

while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    pixel_size = (iterations // 2) * 5
    if pixel_size == 0:
        pixel_size = 1  

    flag_surface = pixelate(game_list[iterations][1], pixel_size)
    rect = flag_surface.get_rect(center=(width//2, height//2 - 100))

    text_surface = font.render(game_list[iterations][0], True, text_color)
    text_rect = text_surface.get_rect(center=(width // 2, height // 2 + 200))
    
    duration = (pygame.time.get_ticks() - start)/1000
    if duration < 3:
        screen.blit(flag_surface, rect)
    if duration > 3 and duration < 5:
        screen.blit(flag_surface, rect)
        screen.blit(text_surface, text_rect)
    if duration > 6:
        start = pygame.time.get_ticks()
        iterations += 1
                
    
    pygame.display.flip()

    if(iterations == GAME_LENGTH):
        running = False

pygame.quit()
