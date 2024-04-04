import time
import pygame
try:
    import cupy
except (Exception) as E:
    pass
from colors import *
from jsonReader import JsonReader
import time

SettingReader = JsonReader("settings.json")
SettingsData = SettingReader.Read()

CudaEnabled = SettingsData["cuda-enabled"]

class Game:
    def __init__(self):
        pygame.init()
        ResX = SettingsData["resX"]
        ResY = SettingsData["resY"]
        CellScale = SettingsData["cellScale"]
        self.Screen = pygame.display.set_mode((ResX,ResY))
        self.Screen.fill(COLOR_GRID)
        self.Running = False
        self.Progressing = False
        self.Cells = numpy.zeros((int(ResY/CellScale),int(ResX/CellScale)))
        self.Size = SettingsData["size"]
        pygame.display.flip()
        pygame.display.update()
        self.Update()
        while True:
            for Event in pygame.event.get():
                if Event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif Event.type == pygame.KEYDOWN:
                    if Event.key == pygame.K_SPACE:
                        self.Running = not self.Running
                        self.Update()
                        pygame.display.update()
                if pygame.mouse.get_pressed()[0]:
                    Pos = pygame.mouse.get_pos()
                    self.Cells[Pos[1] // 10, Pos[0] // 10] = not self.Cells[Pos[1] // 10, Pos[0] // 10]
                    self.Update()
                    pygame.display.update()
            if self.Running:
                self.Progressing = True
                self.Update()
                self.Cells = self.UpdatedCells
                pygame.display.update()
                self.Progressing = False
            time.sleep(SettingsData["delay"])

    def Update(self):
        self.UpdatedCells = self.Cells
        if CudaEnabled:
            self.UpdatedCells = cupy.zeros((self.Cells.shape[0], self.Cells.shape[1]))
            self.NDI = cupy.ndindex(self.Cells.shape)
        else:
            self.UpdatedCells = numpy.zeros((self.Cells.shape[0], self.Cells.shape[1]))
            self.NDI = numpy.ndindex(self.Cells.shape)
        for Row, Collum in self.NDI:
            if CudaEnabled:
                self.Alive = cupy.sum(self.Cells[Row-1:Row+2, Collum-1:Collum+2]) - self.Cells[Row,Collum]
            else:
                self.Alive = numpy.sum(self.Cells[Row-1:Row+2, Collum-1:Collum+2]) - self.Cells[Row,Collum]
            Color = COLOR_BG if self.Cells[Row,Collum] == 0 else COLOR_ALIVE
            if self.Cells[Row,Collum] == 1:
                if self.Alive < 2 or self.Alive > 3:
                    if self.Progressing:
                        Color = COLOR_DN
                elif 2 <= self.Alive <= 3:
                    self.UpdatedCells[Row,Collum] = 1
                    if self.Progressing:
                        Color = COLOR_ALIVE
            else:
                if self.Alive == 3:
                    self.UpdatedCells[Row, Collum] = 1
                    if self.Progressing:
                        Color = COLOR_ALIVE
            pygame.draw.rect(self.Screen,Color,(Collum*self.Size,Row*self.Size,self.Size-1,self.Size-1))   
        
if __name__ == "__main__":
    GameClass = Game()