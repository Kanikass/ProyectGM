#Snake con sensor de movimiento
#Snake with motion sensor
# Importar las bibliotecas necesarias
import math
import random
import pygame
import tkinter as tk
from tkinter import messagebox
import mediapipe as mp
import cv2

# Configurar detección de manos de Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Definir la clase "cube" que representa una celda en el juego
class cube(object):
    rows = 20  # Número de filas en la cuadrícula
    w = 500   # Ancho de la ventana
    def __init__(self,start,dirnx=1,dirny=0,color=(255,0,0)):
        self.pos = start
        self.dirnx = 1
        self.dirny = 0
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]

        # Dibujar un cuadrado en la posición de la celda
        pygame.draw.rect(surface, self.color, (i*dis+1,j*dis+1, dis-2, dis-2))
        if eyes:
            centre = dis//2
            radius = 3
            circleMiddle = (i*dis+centre-radius,j*dis+8)
            circleMiddle2 = (i*dis + dis -radius*2, j*dis+8)

            # Dibujar los "ojos" del cubo
            pygame.draw.circle(surface, (0,0,0), circleMiddle, radius)
            pygame.draw.circle(surface, (0,0,0), circleMiddle2, radius)

# Definir la clase "snake" que representa a la serpiente en el juego
class snake(object):
    body = []  # Lista para almacenar las partes del cuerpo de la serpiente
    turns = {}  # Diccionario para almacenar giros
    def __init__(self, color, pos):
        self.color = color
        self.head = cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1

    def move(self, cam):
        #keys = pygame.key.get_pressed()  # Obtener las teclas presionadas

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Capturar la imagen de la cámara y procesarla para detectar manos
        success, img = cam.read()
        imgg = cv2.flip(img, 1)

    # Convertir el fotograma de BGR a RGB
        image_rgb = cv2.cvtColor(imgg, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

    # Obtener las coordenadas de la mano
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
            # Get the size of the hand tracking window
                image_height, image_width, _ = imgg.shape

            # Draw circles for all the landmarks in red
                for landmark in hand_landmarks.landmark:
                    x = int(landmark.x * image_width)
                    y = int(landmark.y * image_height)
                    cv2.circle(imgg, (x, y), 5, (0, 0, 255), -1)

            # Calculate the average coordinates of all the landmarks
                total_x = 0
                total_y = 0
                num_landmarks = len(hand_landmarks.landmark)
                for landmark in hand_landmarks.landmark:
                    total_x += landmark.x
                    total_y += landmark.y

                average_x = total_x / num_landmarks
                average_y = total_y / num_landmarks

            # Dibujar un círculo en la posición del centro de la mano (verde)
                center_x = int(average_x * image_width)
                center_y = int(average_y * image_height)
                cv2.circle(imgg, (center_x, center_y), 10, (0, 255, 0), -1)

            # Mapear las coordenadas del centro de la mano al movimiento de snake
                self.dirnx = int((average_x * cube.rows) - self.head.pos[0])
                self.dirny = int((average_y * cube.rows) - self.head.pos[1])

                # Limitar la velocidad de movimiento
                self.dirnx = max(-1, min(self.dirnx, 1))
                self.dirny = max(-1, min(self.dirny, 1))
            # Guardar la posición anterior de la cabeza
            
                prev_head_pos = self.head.pos
                
                 #Mover la serpiente
                self.head.move(self.dirnx, self.dirny)
                cv2.imshow("Seguimientos de manos", imgg)

                #mover resto del cuerpo
                for i, c in enumerate(self.body[1:], start=1):
                    temp_pos = c.pos
                    c.pos = prev_head_pos
                    prev_head_pos = temp_pos
                    
            # Asegurarse de que las posiciones estén dentro de los límites de la ventana
                    c.pos = (c.pos[0] % cube.rows, c.pos[1] % cube.rows)
                    
    def reset(self, pos):
        self.head = cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1
        
 
 
    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny
 
        if dx == 1 and dy == 0:
            self.body.append(cube((tail.pos[0]-1,tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0]+1,tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0],tail.pos[1]-1)))
        elif dx == 0 and dy == -1:
            self.body.append(cube((tail.pos[0],tail.pos[1]+1)))
 
        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy
 
 
    def draw(self, surface):
        for i, c in enumerate(self.body):
            c.draw(surface, i == 0)
 
 
def drawGrid(w, rows, surface):
    sizeBtwn = w // rows
 
    x = 0
    y = 0
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn
 
        pygame.draw.line(surface, (255,255,255), (x,0),(x,w))
        pygame.draw.line(surface, (255,255,255), (0,y),(w,y))
 
 
def redrawWindow(surface):
    global rows, width, s, snack
    surface.fill((0,0,0))
    s.draw(surface)
    snack.draw(surface)
    drawGrid(width,rows, surface)
    pygame.display.update()
 
 
def randomSnack(rows, item):
 
    positions = item.body
 
    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z:z.pos == (x,y), positions))) > 0:
            continue
        else:
            break
 
    return (x,y)
 
 
def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except:
        pass
 
 
def main():
    global width, rows, s, snack
    width = 500
    rows = 20
    win = pygame.display.set_mode((width, width))
    s = snake((255,0,0), (10,10))
    snack = cube(randomSnack(rows, s), color=(0,255,0))
    cam = cv2.VideoCapture(0)
    flag = True
    pygame.init() 
 
    clock = pygame.time.Clock()
 
    while flag:
        pygame.time.delay(50)
        clock.tick(10)
        s.move(cam)
        print("Snake position:", s.head.pos) 
        print("Snack position:", snack.pos)
        if s.head.pos == snack.pos:
            s.addCube()
            snack = cube(randomSnack(rows, s), color=(0,255,0))
            print("Snack eaten! New snack position:", snack.pos) 

        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z:z.pos, s.body[x+1:])):
                print('Score: ', len(s.body))
                message_box('You Lost!', 'Play again...')
                s.reset((10,10))
                break
 
 
        redrawWindow(win)
 
 
    pass
 
 
pygame.quit() 
main()
