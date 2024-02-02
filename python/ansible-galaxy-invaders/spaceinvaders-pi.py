#!/usr/bin/env python

# Space Invaders
# Created by Lee Robinson
# Enhanced by Damien Lederer

#######################################################################
from pygame import *
import sys, getopt
from os.path import abspath, dirname
from random import choice
import random
import asyncio
import websockets
import requests
import json
import datetime

BASE_PATH = abspath(dirname(__file__))
FONT_PATH = BASE_PATH + '/fonts/'
IMAGE_PATH = BASE_PATH + '/images/'
SOUND_PATH = BASE_PATH + '/sounds/'

#######################################################################
# Parse command line options
baseurl = ''

try:
    opts, args = getopt.getopt(sys.argv[1:],"hu:",["baseurl="])
except getopt.GetoptError:
    print ('spaceinvaders.py -u <base url>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print ('spaceinvaders.py -u <base url>')
        sys.exit()
    elif opt in ("-u", "--baseurl"):
        baseurl = arg

if not baseurl:
    print ('spaceinvaders.py -u <base url>')
    sys.exit(2)


#OCPDOMAIN = 'project1989.apps-crc.testing'
OCPDOMAIN = baseurl
WSURL = 'ws://eda-engine-' + OCPDOMAIN + '/ws/log'
LOGURL = 'http://eda-engine-' + OCPDOMAIN + '/log'
GETPODURL = 'http://kubeinvaders-' + OCPDOMAIN + '/kube/pods?action=list&namespace=target'
KILLPODURL = 'http://kubeinvaders-' + OCPDOMAIN + '/kube/pods?action=delete&namespace=target&pod_name='

print ('Base URL is "', OCPDOMAIN)


#######################################################################
# Constants

# Colors (R, G, B)
WHITE = (255, 255, 255)
GREEN = (78, 255, 87)
YELLOW = (241, 255, 0)
BLUE = (80, 255, 239)
PURPLE = (203, 0, 255)
RED = (237, 28, 36)

#SCREEN = display.set_mode((800, 600))
# We're aiming for a resolution of 1920 x 1080
#XRES=1920
#YRES=1080
XRES=1280
YRES=720

# The gamebox is the left half of the screen, but create a bit of a border
GAMEBOX=(XRES/2) - 5
#COMPRESSION=100   # Compress the game a bit in the Y axis
COMPRESSION=0   # Compress the game a bit in the Y axis

# The lightspeed box is the right half of the screen, and create a bit of a border
LIGHTSPEEDBOX=XRES/2 + 15

SCREEN = display.set_mode((0, 0), FULLSCREEN)
FONT = FONT_PATH + 'space_invaders.ttf'
IMG_NAMES = ['ship', 'mystery',
             'enemy1_1', 'enemy1_2',
             'enemy2_1', 'enemy2_2',
             'enemy3_1', 'enemy3_2',
             'explosionblue', 'explosiongreen', 'explosionpurple',
             'laser', 'enemylaser', 'bigip', 'cisco-aci', 'cloud-lb', 'f5', 'ibm-db2', 'nginx', 'openshift', 'sap-hana', 'websphere']
IMAGES = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha()
          for name in IMG_NAMES}

#BLOCKERS_POSITION = 450
BLOCKERS_POSITION = YRES - 150 - COMPRESSION
#BLOCKERS_SEPARATION = 200
BLOCKERS_SEPARATION = 150
#BLOCKERS_SIZE = 9
BLOCKERS_SIZE = 7

ENEMY_DEFAULT_POSITION = 100 + COMPRESSION  # Initial value for a new game
ENEMY_MOVE_DOWN = 35

DUALBULLETMODE = False
#LIGHTSPEEDTEXT = ''


#######################################################################
class Ship(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        #self.rect = self.image.get_rect(topleft=(375, 540))
        self.rect = self.image.get_rect(topleft=(375, (YRES-60-COMPRESSION)))
        self.speed = 5

    def update(self, keys, *args):
        if keys[K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.speed
        #if keys[K_RIGHT] and self.rect.x < 740:
        if keys[K_RIGHT] and self.rect.x < (GAMEBOX-60):
            self.rect.x += self.speed
        game.screen.blit(self.image, self.rect)


class Bullet(sprite.Sprite):
    def __init__(self, xpos, ypos, direction, speed, filename, side):
        sprite.Sprite.__init__(self)
        self.image = IMAGES[filename]
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed
        self.direction = direction
        self.side = side
        self.filename = filename

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        #if self.rect.y < 15 or self.rect.y > 600:
        if self.rect.y < 15 or self.rect.y > (YRES-COMPRESSION -12):
            self.kill()


class Enemy(sprite.Sprite):
    def __init__(self, row, column):
        sprite.Sprite.__init__(self)
        self.row = row
        self.column = column
        self.images = []
        self.iconimages = {}
        self.load_images()
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.icon = None
        self.load_icon_images()

    def toggle_image(self):
        self.index += 1
        if self.index >= len(self.images):
            self.index = 0
        self.image = self.images[self.index]

    def update(self, *args):
        game.screen.blit(self.image, self.rect)
        # If this baddie has an icon, then show it
        if self.icon:
            game.screen.blit(self.iconimages[self.icon], self.rect)

    def load_images(self):
        images = {0: ['1_2', '1_1'],
                  1: ['2_2', '2_1'],
                  2: ['2_2', '2_1'],
                  3: ['3_1', '3_2'],
                  4: ['3_1', '3_2'],
                  }
        img1, img2 = (IMAGES['enemy{}'.format(img_num)] for img_num in
                      images[self.row])
        self.images.append(transform.scale(img1, (40, 35)))
        self.images.append(transform.scale(img2, (40, 35)))
        
    def load_icon_images(self):
        iconimages = [ 'bigip', 'cisco-aci', 'cloud-lb', 'f5', 'ibm-db2', 'nginx', 'openshift', 'sap-hana', 'websphere' ]
        for iconimage in iconimages:
            self.iconimages[iconimage] = transform.scale(IMAGES[iconimage], (25, 25))

    def assign_icon(self, icon):
        self.icon = icon

class EnemiesGroup(sprite.Group):
    def __init__(self, columns, rows):
        sprite.Group.__init__(self)
        self.enemies = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 600
        self.direction = 1
        #self.rightMoves = 30  # This is the number of "steps" of "velocity" below.  
        #self.leftMoves = 30
        self.resBasedMoves = (XRES/2 - 510)/10  # Work this out based on the res of the screen
        self.rightMoves = self.resBasedMoves
        self.leftMoves  = self.resBasedMoves
        self.moveNumber = 15
        self.timer = time.get_ticks()
        self.bottom = game.enemyPosition + ((rows - 1) * 45) + 35
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1

        # This is a list of the infrastructure icons that are on the screen
        self.pods = []

    def update(self, current_time):
        if current_time - self.timer > self.moveTime:
            if self.direction == 1:
                max_move = self.rightMoves + self.rightAddMove
            else:
                max_move = self.leftMoves + self.leftAddMove

            if self.moveNumber >= max_move:
                self.leftMoves = self.resBasedMoves + self.rightAddMove
                self.rightMoves = self.resBasedMoves + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for enemy in self:
                    enemy.rect.y += ENEMY_MOVE_DOWN
                    enemy.toggle_image()
                    if self.bottom < enemy.rect.y + 35:
                        self.bottom = enemy.rect.y + 35
            else:
                velocity = 10 if self.direction == 1 else -10
                for enemy in self:
                    enemy.rect.x += velocity
                    enemy.toggle_image()
                self.moveNumber += 1

            self.timer += self.moveTime

    def add_internal(self, *sprites):
        super(EnemiesGroup, self).add_internal(*sprites)
        for s in sprites:
            self.enemies[s.row][s.column] = s

    def remove_internal(self, *sprites):
        super(EnemiesGroup, self).remove_internal(*sprites)
        for s in sprites:
            self.kill(s)
        self.update_speed()

    def is_column_dead(self, column):
        return not any(self.enemies[row][column]
                       for row in range(self.rows))

    def random_bottom(self):
        col = choice(self._aliveColumns)
        col_enemies = (self.enemies[row - 1][col]
                       for row in range(self.rows, 0, -1))
        return next((en for en in col_enemies if en is not None), None)

    def update_speed(self):
        if len(self) == 1:
            self.moveTime = 100  # Mwuhahaha!  Let's make it faster!
        elif len(self) <= 5:
            self.moveTime = 200
        elif len(self) <= 10:
            self.moveTime = 400

    def kill(self, enemy):

        self.enemies[enemy.row][enemy.column] = None
        is_column_dead = self.is_column_dead(enemy.column)
        if is_column_dead:
            self._aliveColumns.remove(enemy.column)

        if enemy.column == self._rightAliveColumn:
            while self._rightAliveColumn > 0 and is_column_dead:
                self._rightAliveColumn -= 1
                self.rightAddMove += 5
                is_column_dead = self.is_column_dead(self._rightAliveColumn)

        elif enemy.column == self._leftAliveColumn:
            while self._leftAliveColumn < self.columns and is_column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                is_column_dead = self.is_column_dead(self._leftAliveColumn)
    
    def getNumRemainingEnemies(self):
        numRemainingEnemies = 0
        for row in self.enemies:
            for enemy in row:
                if enemy and not enemy.icon:
                    numRemainingEnemies += 1
        return numRemainingEnemies

    def allocate_icons(self, iconList, recentlyKilled):

        numRemainingEnemies = self.getNumRemainingEnemies()

        #print("Number remaining enemies:", numRemainingEnemies)

        # No point going any further if there's no more enemies without icons
        if (numRemainingEnemies == 0):
            return

        # Get the missing icons
        #print ("K8 Icon List: ", iconList)
        #print ("What's in my local list: ", self.pods)
        missingIcons = list(set(iconList) - set(self.pods))
        #print ("Missing icon list: ", missingIcons)
        for missingIcon in missingIcons:
            #print ("Missing icon:", missingIcon)

            if not missingIcon in recentlyKilled.keys():

                en = random.randint(0, numRemainingEnemies)
                #print ("Random: ", en)

                counter = 0
                for row in self.enemies:
                    for enemy in row:
                        if enemy and not enemy.icon:
                            if (counter == en):
                                #print ("Putting icon on: ",missingIcon, enemy.rect.x, enemy.rect.y)
                                enemy.icon = missingIcon
                                self.pods.append(missingIcon)
                            counter += 1

class Blocker(sprite.Sprite):
    def __init__(self, size, color, row, column):
        sprite.Sprite.__init__(self)
        self.height = size
        self.width = size
        self.color = color
        self.image = Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.row = row
        self.column = column

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)


class Mystery(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['mystery']
        self.image = transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, 45))
        self.row = 5
        self.moveTime = 25000
        self.direction = 1
        self.timer = time.get_ticks()
        self.mysteryEntered = mixer.Sound(SOUND_PATH + 'mysteryentered.wav')
        self.mysteryEntered.set_volume(0.3)
        self.playSound = True

    def update(self, keys, currentTime, *args):
        resetTimer = False
        passed = currentTime - self.timer
        if passed > self.moveTime:
            #if (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
            if (self.rect.x < 0 or self.rect.x > XRES) and self.playSound:
                self.mysteryEntered.play()
                self.playSound = False
            if self.rect.x < 840 and self.direction == 1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x += 2
                game.screen.blit(self.image, self.rect)
            if self.rect.x > -100 and self.direction == -1:
                self.mysteryEntered.fadeout(4000)
                self.rect.x -= 2
                game.screen.blit(self.image, self.rect)

        #if self.rect.x > 830:
        if self.rect.x > GAMEBOX:
            self.playSound = True
            self.direction = -1
            resetTimer = True
        if self.rect.x < -90:
            self.playSound = True
            self.direction = 1
            resetTimer = True
        if passed > self.moveTime and resetTimer:
            self.timer = currentTime


class EnemyExplosion(sprite.Sprite):
    def __init__(self, enemy, *groups):
        super(EnemyExplosion, self).__init__(*groups)
        self.image = transform.scale(self.get_image(enemy.row), (40, 35))
        self.image2 = transform.scale(self.get_image(enemy.row), (50, 45))
        self.rect = self.image.get_rect(topleft=(enemy.rect.x, enemy.rect.y))
        self.timer = time.get_ticks()

    @staticmethod
    def get_image(row):
        img_colors = ['purple', 'blue', 'blue', 'green', 'green']
        return IMAGES['explosion{}'.format(img_colors[row])]

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
            game.screen.blit(self.image, self.rect)
        elif passed <= 200:
            game.screen.blit(self.image2, (self.rect.x - 6, self.rect.y - 6))
        elif 400 < passed:
            self.kill()


class MysteryExplosion(sprite.Sprite):
    def __init__(self, mystery, score, *groups):
        super(MysteryExplosion, self).__init__(*groups)
        self.text = Text(FONT, 20, str(score), WHITE,
                         mystery.rect.x + 20, mystery.rect.y + 6)
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 200 or 400 < passed <= 600:
            self.text.draw(game.screen)
        elif 600 < passed:
            self.kill()


class ShipExplosion(sprite.Sprite):
    def __init__(self, ship, *groups):
        super(ShipExplosion, self).__init__(*groups)
        self.image = IMAGES['ship']
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if 300 < passed <= 600:
            game.screen.blit(self.image, self.rect)
        elif 900 < passed:
            self.kill()


class Life(sprite.Sprite):
    def __init__(self, xpos, ypos):
        sprite.Sprite.__init__(self)
        self.image = IMAGES['ship']
        self.image = transform.scale(self.image, (23, 23))
        self.rect = self.image.get_rect(topleft=(xpos, ypos))

    def update(self, *args):
        game.screen.blit(self.image, self.rect)


class Text(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

# I need another 'text' style class, apart from the one above.  As it turns out,
# the standard font renderer can't hand multi-lines!
class MultiText(object):
    def __init__(self, textFont, size, message, color, xpos, ypos):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xpos, ypos))
        self.message = message
        self.xpos = xpos
        self.ypos = ypos
        self.color = color

    def draw(self, surface):
        lines = self.message.splitlines()
        if len(lines) > 0:
            text_height = self.font.size(lines[0])[1]
            x = self.xpos
            y = self.ypos
            for i, l in enumerate(lines):
                # No harm in adding a bit of colour to some of the lines
                if l.startswith('| Suggestion'):
                  surface.blit(self.font.render(l, True, BLUE), (x, y + text_height*i))
                elif l.startswith('|'):
                  surface.blit(self.font.render(l, True, YELLOW), (x, y + text_height*i))
                else:
                  surface.blit(self.font.render(l, True, self.color), (x, y + text_height*i))


class SpaceInvaders(object):
    def __init__(self, asyncloop):
        # It seems, in Linux buffersize=512 is not enough, use 4096 to prevent:
        #   ALSA lib pcm.c:7963:(snd_pcm_recover) underrun occurred
        mixer.pre_init(44100, -16, 1, 4096)
        init()
        self.clock = time.Clock()
        self.caption = display.set_caption('Space Invaders')
        self.screen = SCREEN

        #self.background = image.load(IMAGE_PATH + 'background.jpg').convert()
        img = image.load(IMAGE_PATH + 'background.jpg').convert()
        DEFAULT_BACKGROUND_SIZE = (XRES, YRES)
        img = transform.scale(img, DEFAULT_BACKGROUND_SIZE)
        self.background = img

        self.startGame = False
        self.mainScreen = True
        self.gameOver = False
        # Counter for enemy starting position (increased each new round)
        self.enemyPosition = ENEMY_DEFAULT_POSITION
        self.titleText = Text(FONT, 50, 'Ansible Galaxy Invaders', WHITE, (GAMEBOX)-400, (YRES/2)-175)
        self.titleText2 = Text(FONT, 25, 'Press any key to continue', WHITE,
                               (GAMEBOX)-200, (YRES/2)-105)
        self.gameOverText = Text(FONT, 50, 'Game Over', WHITE, (GAMEBOX)-150, (YRES/2))
        self.nextRoundText = Text(FONT, 50, 'Next Round', WHITE, (GAMEBOX)-150, (YRES/2))
        self.enemy1Text = Text(FONT, 25, '   =   10 pts', GREEN, (GAMEBOX)-30, (YRES/2)-50)
        self.enemy2Text = Text(FONT, 25, '   =  20 pts', BLUE, (GAMEBOX)-30, (YRES/2))
        self.enemy3Text = Text(FONT, 25, '   =  30 pts', PURPLE, (GAMEBOX)-30, (YRES/2)+50)
        self.enemy4Text = Text(FONT, 25, '   =  ?????', RED, (GAMEBOX)-30, (YRES/2)+100)
        self.scoreText = Text(FONT, 20, 'Score', WHITE, 5, 5+COMPRESSION)
        self.livesText = Text(FONT, 20, 'Lives ', WHITE, (GAMEBOX)-160, 5+COMPRESSION)

        self.life1 = Life((GAMEBOX)-85, 3+COMPRESSION)
        self.life2 = Life((GAMEBOX)-58, 3+COMPRESSION)
        self.life3 = Life((GAMEBOX)-31, 3+COMPRESSION)
        self.livesGroup = sprite.Group(self.life1, self.life2, self.life3)

        #self.lightspeedIntroText = Text(FONT, 25, 'Lightspeed Infrastructure AI Assistant', BLUE, LIGHTSPEEDBOX+130, 50)
        self.lightspeedIntroText = Text(FONT, 16, 'Lightspeed Infrastructure AI Assistant', BLUE, LIGHTSPEEDBOX+130, 50)
        # The main lightspeed text is empty for now
        self.lightspeedContentText = MultiText(FONT, 12, '', WHITE, LIGHTSPEEDBOX, 100)
        self.lightspeedRawText = ''

        self.asyncloop = asyncloop
        self.httpsession = requests.Session()

        self.wstimer = 0
        self.podtimer = 1
        self.k8PodList = []

        # We need to keep track of the pods that we've killed recently.  Otherwise they re-appear within milliseconds because
        # it takes a few seconds for the pod in OpenShift to die, in the meantime it comes back on the next pod-fetch call.
        self.recentlyKilled = {}

    def reset(self, score):
        self.player = Ship()
        self.playerGroup = sprite.Group(self.player)
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.mysteryShip = Mystery()
        self.mysteryGroup = sprite.Group(self.mysteryShip)
        self.enemyBullets = sprite.Group()
        self.make_enemies()
        self.allSprites = sprite.Group(self.player, self.enemies,
                                       self.livesGroup, self.mysteryShip)
        self.keys = key.get_pressed()

        self.timer = time.get_ticks()
        self.noteTimer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.score = score
        self.create_audio()
        self.makeNewShip = False
        self.shipAlive = True

    def make_blockers(self, number):
        blockerGroup = sprite.Group()
        for row in range(4):
            for column in range(BLOCKERS_SIZE):
                blocker = Blocker(10, GREEN, row, column)
                blocker.rect.x = 50 + (BLOCKERS_SEPARATION * number) + (column * blocker.width)
                blocker.rect.y = BLOCKERS_POSITION + (row * blocker.height)
                blockerGroup.add(blocker)
        return blockerGroup

    def create_audio(self):
        self.sounds = {}
        for sound_name in ['shoot', 'shoot2', 'invaderkilled', 'mysterykilled',
                           'shipexplosion', 'gameover']:
            self.sounds[sound_name] = mixer.Sound(
                SOUND_PATH + '{}.wav'.format(sound_name))
            self.sounds[sound_name].set_volume(0.2)

        self.musicNotes = [mixer.Sound(SOUND_PATH + '{}.wav'.format(i)) for i
                           in range(4)]
        for sound in self.musicNotes:
            sound.set_volume(0.5)

        self.noteIndex = 0

    def play_main_music(self, currentTime):
        if currentTime - self.noteTimer > self.enemies.moveTime:
            self.note = self.musicNotes[self.noteIndex]
            if self.noteIndex < 3:
                self.noteIndex += 1
            else:
                self.noteIndex = 0

            self.note.play()
            self.noteTimer += self.enemies.moveTime

    @staticmethod
    def should_exit(evt):
        # type: (pygame.event.EventType) -> bool
        return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)

    def check_input(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if self.should_exit(e):
                sys.exit()
            if e.type == KEYDOWN:
                #if e.key == K_SPACE:
                if e.key == K_x:
                    if len(self.bullets) == 0 and self.shipAlive:
                        if (not DUALBULLETMODE) or (self.score < 1000):
                            bullet = Bullet(self.player.rect.x + 23,
                                            self.player.rect.y + 5, -1,
                                            15, 'laser', 'center')
                            self.bullets.add(bullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot'].play()
                        else:
                            leftbullet = Bullet(self.player.rect.x + 8,
                                                self.player.rect.y + 5, -1,
                                                15, 'laser', 'left')
                            rightbullet = Bullet(self.player.rect.x + 38,
                                                 self.player.rect.y + 5, -1,
                                                 15, 'laser', 'right')
                            self.bullets.add(leftbullet)
                            self.bullets.add(rightbullet)
                            self.allSprites.add(self.bullets)
                            self.sounds['shoot2'].play()

    def make_enemies(self):
        enemies = EnemiesGroup(10, 5)
        for row in range(5):
            for column in range(10):
                enemy = Enemy(row, column)
                enemy.rect.x = 157 + (column * 50)
                enemy.rect.y = self.enemyPosition + (row * 45)
                enemies.add(enemy)

        self.enemies = enemies

    def make_enemies_shoot(self):
        if (time.get_ticks() - self.timer) > 700 and self.enemies:
            enemy = self.enemies.random_bottom()
            self.enemyBullets.add(
                Bullet(enemy.rect.x + 14, enemy.rect.y + 20, 1, 5,
                       'enemylaser', 'center'))
            self.allSprites.add(self.enemyBullets)
            self.timer = time.get_ticks()

    def calculate_score(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 300])
                  }

        score = scores[row]
        self.score += score
        return score

    def create_main_menu(self):
        self.enemy1 = IMAGES['enemy3_1']
        self.enemy1 = transform.scale(self.enemy1, (40, 40))
        self.enemy2 = IMAGES['enemy2_2']
        self.enemy2 = transform.scale(self.enemy2, (40, 40))
        self.enemy3 = IMAGES['enemy1_2']
        self.enemy3 = transform.scale(self.enemy3, (40, 40))
        self.enemy4 = IMAGES['mystery']
        self.enemy4 = transform.scale(self.enemy4, (80, 40))
        self.screen.blit(self.enemy1, ((GAMEBOX)-80, (YRES/2)-50))
        self.screen.blit(self.enemy2, ((GAMEBOX)-80, (YRES/2)))
        self.screen.blit(self.enemy3, ((GAMEBOX)-80, (YRES/2)+50))
        self.screen.blit(self.enemy4, ((GAMEBOX)-99, (YRES/2)+100))

    def check_collisions(self):
        sprite.groupcollide(self.bullets, self.enemyBullets, True, True)

        for enemy in sprite.groupcollide(self.enemies, self.bullets,
                                         True, True).keys():
            self.sounds['invaderkilled'].play()
            self.calculate_score(enemy.row)
            if enemy.icon:
                #self.k8PodList.remove(enemy.icon)
                self.enemies.pods.remove(enemy.icon)
                self.recentlyKilled[enemy.icon] = time.get_ticks() + 4000
                self.asyncloop.create_task(self.killPod(enemy.icon))
            EnemyExplosion(enemy, self.explosionsGroup)
            self.gameTimer = time.get_ticks()

        for mystery in sprite.groupcollide(self.mysteryGroup, self.bullets,
                                           True, True).keys():
            mystery.mysteryEntered.stop()
            self.sounds['mysterykilled'].play()
            score = self.calculate_score(mystery.row)
            MysteryExplosion(mystery, score, self.explosionsGroup)
            newShip = Mystery()
            self.allSprites.add(newShip)
            self.mysteryGroup.add(newShip)

        for player in sprite.groupcollide(self.playerGroup, self.enemyBullets,
                                          True, True).keys():
            if self.life3.alive():
                self.life3.kill()
            elif self.life2.alive():
                self.life2.kill()
            elif self.life1.alive():
                self.life1.kill()
            else:
                self.gameOver = True
                self.startGame = False
            self.sounds['shipexplosion'].play()
            ShipExplosion(player, self.explosionsGroup)
            self.makeNewShip = True
            self.shipTimer = time.get_ticks()
            self.shipAlive = False

        if self.enemies.bottom >= (YRES-60-COMPRESSION):
            sprite.groupcollide(self.enemies, self.playerGroup, True, True)
            if not self.player.alive() or self.enemies.bottom >= (YRES-COMPRESSION):
                self.gameOver = True
                self.startGame = False

        sprite.groupcollide(self.bullets, self.allBlockers, True, True)
        sprite.groupcollide(self.enemyBullets, self.allBlockers, True, True)
        if self.enemies.bottom >= BLOCKERS_POSITION:
            sprite.groupcollide(self.enemies, self.allBlockers, False, True)

    def create_new_ship(self, createShip, currentTime):
        if createShip and (currentTime - self.shipTimer > 900):
            self.player = Ship()
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewShip = False
            self.shipAlive = True

    def create_game_over(self, currentTime):
        self.sounds['gameover'].play()
        self.screen.blit(self.background, (0, 0))
        passed = currentTime - self.timer
        if passed < 750:
            self.gameOverText.draw(self.screen)
        elif 750 < passed < 1500:
            self.screen.blit(self.background, (0, 0))
        elif 1500 < passed < 2250:
            self.gameOverText.draw(self.screen)
        elif 2250 < passed < 2750:
            self.screen.blit(self.background, (0, 0))
        elif passed > 3000:
            self.mainScreen = True

        for e in event.get():
            if self.should_exit(e):
                sys.exit()
    
    def run_once(self, loop):
        loop.call_soon(loop.stop)
        loop.run_forever()

    async def checkws(self):
        #tstart = datetime.datetime.now()
        response = self.httpsession.get(LOGURL)
        if (response.ok):
            jData = json.loads(response.content)
            self.lightspeedRawText = jData['data']
            print (jData['data'])
        #tend = datetime.datetime.now()
        #ttime = tend - tstart
        #print (ttime)


    async def checkPods(self):
        #tstart = datetime.datetime.now()
        response = self.httpsession.get(GETPODURL)
        if (response.ok):
            jData = json.loads(response.content)
            #print (response.content)
            pods = jData['items']
            self.k8PodList = pods
        #tend = datetime.datetime.now()
        #ttime = tend - tstart
        #print (ttime)

    async def killPod(self, icon):
        response = self.httpsession.get(KILLPODURL + icon)
        #print ("Killing: ", icon)
    
    def cleanupKillList(self):
        keys = self.recentlyKilled.keys()
        for cleanup in list(keys):
            #print ("Cleanup list: ", cleanup)
            if self.recentlyKilled[cleanup] < time.get_ticks():
                del self.recentlyKilled[cleanup]

    def main(self):

        while True:
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.titleText.draw(self.screen)
                self.titleText2.draw(self.screen)
                self.enemy1Text.draw(self.screen)
                self.enemy2Text.draw(self.screen)
                self.enemy3Text.draw(self.screen)
                self.enemy4Text.draw(self.screen)
                self.create_main_menu()
                for e in event.get():
                    if self.should_exit(e):
                        sys.exit()
                    if e.type == KEYUP:
                        # Only create blockers on a new game, not a new round
                        self.allBlockers = sprite.Group(self.make_blockers(0),
                                                        self.make_blockers(1),
                                                        self.make_blockers(2),
                                                        self.make_blockers(3))
                        self.livesGroup.add(self.life1, self.life2, self.life3)
                        self.reset(0)
                        self.startGame = True
                        self.mainScreen = False

            # This is the main game loop
            elif self.startGame:

                # If we've cleared out the enemies, then this block moves onto the next level
                if not self.enemies and not self.explosionsGroup:
                    currentTime = time.get_ticks()
                    if currentTime - self.gameTimer < 4000:   # Increased this to give the Pods in OCP a chance to recover
                        self.screen.blit(self.background, (0, 0))
                        self.scoreText2 = Text(FONT, 20, str(self.score),
                                               GREEN, 85, 5+COMPRESSION)
                        self.scoreText.draw(self.screen)
                        self.scoreText2.draw(self.screen)
                        self.nextRoundText.draw(self.screen)
                        self.livesText.draw(self.screen)
                        self.livesGroup.update()
                        self.check_input()
                    if currentTime - self.gameTimer > 3000:
                        # Move enemies closer to bottom
                        self.enemyPosition += ENEMY_MOVE_DOWN
                        self.reset(self.score)
                        self.gameTimer += 3000
                
                # This block runs the main "game" loop
                else:
                    currentTime = time.get_ticks()
                    self.play_main_music(currentTime)
                    self.screen.blit(self.background, (0, 0))
                    self.allBlockers.update(self.screen)
                    self.scoreText2 = Text(FONT, 20, str(self.score), GREEN,
                                           85, 5+COMPRESSION)
                    self.scoreText.draw(self.screen)
                    self.scoreText2.draw(self.screen)
                    self.livesText.draw(self.screen)
                    self.check_input()
                    self.enemies.update(currentTime)
                    self.allSprites.update(self.keys, currentTime)
                    self.explosionsGroup.update(currentTime)
                    self.check_collisions()
                    #self.enemies.allocate_icons(self.k8PodList)
                    self.create_new_ship(self.makeNewShip, currentTime)
                    self.make_enemies_shoot()

                    draw.line(self.screen, WHITE, (XRES/2, 1), (XRES/2, YRES), 2)

                    self.lightspeedIntroText.draw(self.screen)
                    # The lightspeed text is updated to the global in the async task, so re-read it
                    #self.lightspeedContentText = MultiText(FONT, 16, self.lightspeedRawText, WHITE, LIGHTSPEEDBOX, 100)
                    self.lightspeedContentText = MultiText(FONT, 12, self.lightspeedRawText, WHITE, LIGHTSPEEDBOX, 100)
                    self.lightspeedContentText.draw(self.screen)

                    ## We want to check the WebSocket about every 500ms to make it seem smooth
                    if currentTime - self.wstimer > 1500:
                        self.wstimer = currentTime
                        # Add the WebSocket receive task to the asyncio queue
                        self.asyncloop.create_task(self.checkws())
                    
                    # We want to check the pods about every 1000ms
                    if currentTime - self.podtimer > 2000:
                        self.podtimer = currentTime
                        # Add the WebSocket receive task to the asyncio queue
                        self.asyncloop.create_task(self.checkPods())
                        self.enemies.allocate_icons(self.k8PodList, self.recentlyKilled)

                    self.cleanupKillList()

            elif self.gameOver:
                currentTime = time.get_ticks()
                # Reset enemy starting position
                self.enemyPosition = ENEMY_DEFAULT_POSITION
                self.create_game_over(currentTime)

            display.update()

            # This is the point where I need to run the async loop ourselves.  This won't always
            # have a task on it, so it should be quick most of the time.  This needs to run before
            # the clock tick below, because it yields for the delta time of each game loop vs the
            # framerate.  We need our async loop to eat into that yielding time, not add onto it.
            self.run_once(self.asyncloop)

            self.clock.tick(40)
            #print(self.clock.get_fps())


if __name__ == '__main__':

    # I need to take control of the async loop.  It doesn't run automatically inside
    # the pygame loop, so we'll grab it here, and run it ourselves inside the game loop.
    loop = asyncio.get_event_loop()

    game = SpaceInvaders(loop)
    game.main()
