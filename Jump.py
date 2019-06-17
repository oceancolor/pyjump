"""////////////////////////////////////////////////////
 benjamin - 2019-5-30
 benjamin@qq.com

 跳一跳小游戏 - FSM
///////////////////////////////////////////////////////
"""
import pygame
import sys
import time
from random import *
from pygame.locals import *

#游戏全局状态
STATE_GAMEOVER = 0
STATE_START = 1
STATE_PRESS = 2
STATE_RELEASE = 3
STATE_FLYING = 4
STATE_LANDING = 5
STATE_FORWARD = 6
STATE_FAIL = 7
STATE_WAIT = 8
STATE_READY = 9

#帧率
FPS = 70

#颜色表,马卡龙色系
white = (255,255,255)
strawberry = 0xF16D7A
milkpink = 0xF55066
chocolate = 0xCB8E85
vanilla = 0xF2DEBD
greentea = 0xB7D28D
purplepink = 0xD9B8F1
orange = 0xFF9B6A
yellowpink = 0xF1F1B8
oceanpink = 0xB8F1ED
greenpink = 0xB8F1CC
graypink = 0xE7DAC9
colors = [strawberry,milkpink,chocolate,vanilla,greentea,purplepink,orange,yellowpink,oceanpink,greenpink,graypink]

#尺寸标准
box_height = 100
box_width = 60
actor_height = 30
actor_width = 20
#起跳盒子基准位置
base_box_xpos = 100
base_box_ypos = 300
#角色起跳基准位置
base_actor_xpos = 120
base_actor_ypos = 270
#蓄力压程速度
press_speed = 1
#蓄力最大压程
pressed_max = 60
#计算弹道弹力因子
spring_factor = 1.3
#计算弹道重力因子
gravity_factor = 9

key_flag = False
score_flag = False
framerate = pygame.time.Clock()
__game_state__ = STATE_WAIT
score = 0
alltime_high = 0

def print_text(font, x, y, text, color=(255,255,255)):
    imgText = font.render(text, True, (128,128,128))
    screen.blit(imgText,(x-2,y+2))
    imgText = font.render(text, True, color)
    screen.blit(imgText, (x,y))

def print_normal_text(font, x, y, text, color=(255,255,255)):
    imgText = font.render(text, True, color)
    screen.blit(imgText, (x,y))

class BaseBox(object):
    def __init__(self, color):
        self.height = box_height
        self.width = box_width
        self.color = color
        self.xpos = base_box_xpos
        self.ypos = base_box_ypos
        self.end_xoffset  = box_width
        self.end_yoffset = box_height
        self.pressed_dist = 0
        self.rect = pygame.Rect((self.xpos, self.ypos), (self.end_xoffset, self.end_yoffset))
        
    def draw(self, screen):
        self.rect.x = self.xpos
        self.rect.y = self.ypos
        self.rect.width = self.end_xoffset
        self.rect.height = self.end_yoffset
        pygame.draw.rect(screen, self.color, self.rect)


    def press(self):
        global __game_state__
        self.pressed_dist += press_speed
        if(self.pressed_dist >= pressed_max):
            self.pressed_dist = pressed_max

        self.xpos = base_box_xpos
        self.ypos = base_box_ypos + self.pressed_dist
        self.end_xoffset = box_width
        self.end_yoffset = box_height - self.pressed_dist
   

    def release(self):
        global __game_state__
        self.pressed_dist = 0
        self.xpos = base_box_xpos
        self.ypos = base_box_ypos
        self.end_xoffset = box_width
        self.end_yoffset = box_height

class Actor(object):
    def __init__(self):
        self.width = actor_width
        self.height = actor_height
        self.xpos = base_actor_xpos
        self.ypos = base_actor_ypos
        self.press_dist = 0
        self.fly_dist = 0
        self.color = white
        self.stand = True
        self.rect = pygame.Rect((self.xpos, self.ypos), (actor_width, actor_height))

    def press(self):
        global press_speed
        global score_flag
        score_flag = False
        self.press_dist += press_speed
        self.xpos += 0
        if(self.press_dist >= pressed_max):
            self.press_dist = pressed_max
        self.ypos = base_actor_ypos + self.press_dist
        
    def release(self):
        global __game_state__
        actor.ypos = box_stand.ypos - actor_height - 10
        __game_state__ = STATE_FLYING
        
        
    def fly(self):
        global __game_state__
        global box_jumpto

        fly_long = (self.press_dist**2 * spring_factor)/gravity_factor
        x_per_frame = fly_long/FPS*0.8 #0.8是一个魔术数字,用于调手感

        #弹道公式 飞行距离=压程的平方*弹力因子/重力因子
        #一次跳跃用的时间为1秒,根据帧率分配每一帧移动的偏移
        if(self.fly_dist < fly_long - x_per_frame):
            self.fly_dist += x_per_frame
            self.xpos += x_per_frame
            if(self.fly_dist < fly_long/2 - x_per_frame):
                self.ypos -= 1.7
            else:
                self.ypos += 1.7
        else:
            __game_state__ = STATE_LANDING
            if(self.xpos  > (box_jumpto.xpos + (x_per_frame * 1.2) + box_width - actor_width/2)):
                __game_state__ = STATE_FAIL
                #飞过了
                self.fall(1)
                return

            if((self.xpos + actor_width) < box_jumpto.xpos - x_per_frame):
                #没飞到
                __game_state__ = STATE_FAIL
                self.fall(0)
                return
            return
        

    def landing(self):
        global __game_state__
        global box_jumpto
        global score_flag
        global score
        #计算着陆位置
        if not score_flag:
            score += 1
            score_flag = True
        
        self.ypos = box_jumpto.ypos - self.height
        __game_state__ = STATE_FORWARD
        

    def fall(self, direction):
        global __game_state__
        global box_jumpto
        self.stand = False
        self.ypos = base_box_ypos + box_height - actor_width
        if(direction == 0):
            #没飞到
            #self.xpos = box_jumpto.xpos - actor_height
            if(box_jumpto.xpos <= self.xpos):
                self.xpos = box_jumpto.xpos - actor_height
            else:
                self.xpos = self.xpos + 10
        else:
            #飞过了
            self.xpos = self.xpos + actor_height
        __game_state__ = STATE_GAMEOVER
        

    def reset(self, resetX=True, resetY=True):
        self.press_dist = 0
        self.fly_dist = 0
        if resetX:
            self.xpos = base_actor_xpos
        if resetY:
            self.ypos = base_actor_ypos
        self.width = actor_width
        self.height = actor_height
        self.stand = True
        
        
    def draw(self, screen):
        dead_blink_color = choice([(255,255,255), (255,0,0)])
        if self.stand:
            self.rect.x = self.xpos
            self.rect.y = self.ypos
            self.rect.width = actor_width
            self.rect.height = actor_height
            pygame.draw.rect(screen, self.color, self.rect)
        else:
            self.rect.x = self.xpos-5
            self.rect.y = base_box_ypos + box_height - self.width
            self.rect.width = actor_height
            self.rect.height = actor_width
            pygame.draw.rect(screen, dead_blink_color, self.rect)

        
class Scene(object):
    def __init__(self):
        self.count = 0

    def forward(self):
        global __game_state__
        global box_jumpto
        global box_stand
        global box_prepare
        global box_hidden
        global box_used
        global actor
        #移动场景和盒子
        if box_jumpto.xpos > base_box_xpos:
            box_stand.xpos -= 5
            box_jumpto.xpos -= 5
            box_prepare.xpos -= 5
            box_hidden.xpos -= 5
            actor.xpos -= 5
        else:
            actor.reset(False, True)
            box_used = box_stand#也许可见
            box_stand = box_jumpto#可见
            box_jumpto = box_prepare#可见
            box_prepare = box_hidden#也许可见
            box_prepare.xpos = box_jumpto.xpos + randint(100, 400)
            box_hidden = box_used#必须不可见
            box_hidden.color = choice(colors)
            box_hidden.xpos = box_prepare.xpos + randint(100, 400)
            __game_state__ = STATE_READY
            
        
    def start(self):
        global __game_state__
        global box_prepare
        global box_hidden
        global score
        score = 0
        box_jumpto.xpos = base_box_xpos + 300
        box_prepare.xpos = box_jumpto.xpos + randint(100, 400)
        box_hidden.color = choice(colors)
        box_hidden.xpos = box_prepare.xpos + randint(100, 400)
        actor.reset()
        __game_state__ = STATE_READY
                

    def getready(self):
        global __game_state__
        global box_prepare
        global box_hidden
        print_text(font1, 130, 170, "按住鼠标蓄力,放开就会弹跳")
        

    def gameover(self):
        global __game_state__
        global score
        global alltime_high
        print_text(font1, 260, 120, "GAME OVER!", (randint(0, 255),randint(0, 255),randint(0, 255)))
        print_text(font1, 270, 180, "你的得分:")
        print_text(font1, 460, 180, str(score), (255, 50, 128))
        if(score > alltime_high):
            alltime_high = score
        print_text(font1, 240, 230, "按回车键继续...")
        

    def wait(self):
        print_text(font1, 130, 170, "[回车]开始游戏,[ESC]退出游戏")
        

    def info(self, screen):
        global score
        global alltime_high
        print_normal_text(font2, 270, 10, "你的得分:")
        print_normal_text(font2, 460, 10, str(score), (255, 50, 128))
        print_normal_text(font2, 270, 35, "历史最高:")
        print_normal_text(font2, 460, 35, str(alltime_high), (32, 192, 48))
        

    def init(self):
        global __game_state__
        #把后面的几个盒子都放在看不到的位置,回车开始了之后再决定可显示位置
        box_jumpto.xpos = 900
        box_prepare.xpos = 900
        box_hidden.xpos = 900
        __game_state__ = STATE_WAIT
        
        
def updateState():
    global __game_state__
    if __game_state__ == STATE_START:
        scene.start()
    elif __game_state__ == STATE_PRESS:
        box_stand.press()
        actor.press()
    elif __game_state__ == STATE_RELEASE:
        box_stand.release()
        actor.release()
    elif __game_state__ == STATE_FLYING:
        actor.fly()
    elif __game_state__ == STATE_LANDING:
        actor.landing()
    elif __game_state__ == STATE_FORWARD:
        scene.forward()
    elif __game_state__ == STATE_FAIL:
        actor.fall()
    elif __game_state__ == STATE_GAMEOVER:
        scene.gameover()
    elif __game_state__ == STATE_WAIT:
        scene.wait()
    elif __game_state__ == STATE_READY:
        scene.getready()


box_stand = BaseBox(choice(colors))
box_jumpto = BaseBox(choice(colors))
box_prepare = BaseBox(choice(colors))
box_hidden = BaseBox(choice(colors))
box_used = box_stand
actor = Actor()
scene = Scene()


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    bgm_clip = pygame.mixer.Sound("Strobe.ogg")
    channel = pygame.mixer.find_channel(True)
    channel.play(bgm_clip, -1, 0, 10000)
    screen = pygame.display.set_mode((800,500))
    ground = pygame.Rect((0, 400), (800, 100))
    
    #screen.blit(bg_img1,(0,0))
    pygame.display.set_caption("跳一跳")
    font1 = pygame.font.Font("./TTTGB-Medium.ttf", 40)
    font2 = pygame.font.Font("./TTTGB-Medium.ttf", 20)
    scene.init()
    
    while True:
        framerate.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if __game_state__ == STATE_READY:
                    __game_state__ = STATE_PRESS
            elif event.type == MOUSEBUTTONUP:
                if __game_state__ == STATE_PRESS:
                    __game_state__ = STATE_RELEASE
            elif event.type == KEYDOWN:
                key_flag = True
                keys = pygame.key.get_pressed()
                if keys[K_SPACE]:
                    if __game_state__ == STATE_START:
                        __game_state__ == STATE_READY
                elif keys[K_RETURN]:
                    if __game_state__ == STATE_GAMEOVER:
                        __game_state__ = STATE_WAIT
                    if __game_state__ == STATE_WAIT:
                        __game_state__ = STATE_START
            elif event.type == KEYUP:
                key_flag = False
                keys = pygame.key.get_pressed()
                if keys[K_ESCAPE]:
                    sys.exit()
                    
                
        screen.fill((210, 225, 220))
        pygame.draw.rect(screen, (200, 215, 210), ground)
        #############################
        updateState()
        #############################
        box_stand.draw(screen)
        box_jumpto.draw(screen)
        actor.draw(screen)
        box_prepare.draw(screen)
        scene.info(screen)

        #update the display
        pygame.display.update()
        pygame.display.flip()



