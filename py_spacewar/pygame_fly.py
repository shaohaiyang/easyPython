import pygame, os, sys, random, platform
from pygame.locals import *

size = w, h = 1000, 800
title = '太空大战'
running = True
autofire = True
life = 3
score = 0
if "Darwin" in platform.system():
	dir = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])
	font_file = "/System/Library/Fonts/PingFang.ttc"
else:
	dir = os.path.dirname(__file__)
	font_file = r"C:\windows\Fonts\msyh.ttc"

pygame.init()
pygame.mixer.init()
pygame.display.set_caption(title)
pygame.mouse.set_visible(False)
pygame.key.set_repeat(500)
screen = pygame.display.set_mode(size)
background = pygame.image.load(os.path.join(dir, 'earth.gif'))
snd_back = pygame.mixer.Sound(os.path.join(dir, 'endure.ogg'))
snd_over = pygame.mixer.Sound(os.path.join(dir, 'gameover.ogg'))
snd_back.play(-1)


class Plane(pygame.sprite.Sprite):
	def __init__(self, speed=10):
		super().__init__()
		self.image = pygame.image.load(os.path.join(dir, 'spaceship.png'))
		self.rect = self.image.get_rect(topleft=(0, random.randint(0, h)))
		self.speed = speed
		self.hit = False

	def update(self, key):
		if key[K_UP] and self.rect.top > 0:
			self.rect.move_ip(0, - self.speed)
		if key[K_DOWN] and self.rect.bottom < h:
			self.rect.move_ip(0, self.speed)
		if key[K_LEFT] and self.rect.left > 0:
			self.rect.move_ip(- self.speed, 0)
		if key[K_RIGHT] and self.rect.right < w:
			self.rect.move_ip(self.speed, 0)


class Shit(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()
		# self.image = pygame.Surface((20, 20))
		# color = (
		# 	random.randrange(100, 200, 10),
		# 	random.randrange(100, 200, 10),
		# 	random.randrange(100, 200, 10),
		# )
		# self.image.fill(color)
		self.image = pygame.image.load(os.path.join(dir, 'poop.png'))
		self.rect = self.image.get_rect(center=(w, random.randrange(0, h, 50)))

	def update(self):
		if self.rect.right <= 0:
			self.kill()
		else:
			self.rect.move_ip(- random.randint(4, 8), 0)


class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, scale=1):
		super().__init__()
		self.image = pygame.Surface((10 * scale, 10 * scale), SRCALPHA)
		pygame.draw.circle(self.image, (255, 0, 0), (10 * scale // 2, 10 * scale // 2), 10 * scale)
		self.rect = self.image.get_rect(center=(x + 50, y))

	def update(self):
		if self.rect.left >= w:
			self.kill()
		else:
			self.rect.move_ip(10, 0)


plane = Plane()
planes = pygame.sprite.GroupSingle(plane)
shits = pygame.sprite.Group()
bullets = pygame.sprite.Group()
ADDSHIT = pygame.USEREVENT + 1
pygame.time.set_timer(ADDSHIT, 500)
ADDBULLET = pygame.USEREVENT + 1
pygame.time.set_timer(ADDBULLET, 300)

while running:
	screen.blit(pygame.transform.scale(background, size), (0, 0))

	for e in pygame.event.get():
		if e.type == ADDBULLET:
			if autofire:
				_ = Bullet(plane.rect.centerx, plane.rect.centery)
				bullets.add(_)
		if e.type == ADDSHIT:
			_ = Shit()
			shits.add(_)
		if e.type == QUIT:
			running = False
		if e.type == KEYDOWN:
			if e.key == K_ESCAPE:
				running = False
			if e.key == K_SPACE:
				new_bullet = Bullet(plane.rect.centerx, plane.rect.centery, scale=5)
				bullets.add(new_bullet)

	if pygame.sprite.groupcollide(shits, bullets, True, True):
		score += 20
	if pygame.sprite.spritecollideany(plane, shits):
		life -= 1
		if life <= 0:
			snd_over.play(1)
			pygame.time.delay(1000)
			running = False
		else:
			plane.kill()
			plane = Plane()
			planes = pygame.sprite.GroupSingle(plane)
	score_text = pygame.font.Font(font_file, 25).render(
		f'得分：{score:<6d} 生命力：{life:<3d}',
		True, (255, 0, 0)
	)
	screen.blit(score_text, (w // 3, 10))

	planes.draw(screen)
	shits.draw(screen)
	bullets.draw(screen)

	planes.update(pygame.key.get_pressed())
	shits.update()
	bullets.update()
	pygame.display.update()
