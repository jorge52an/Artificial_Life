from random import randrange as randomRange, random
import math

import pygame
import pygame.gfxdraw
from pygame.locals import *
from pygame.color import *

ENERGY = 10000
FOOD_ENERGY = 10
VISION = 200
MAX_VELOCITY = 4

class Flock():
	def __init__( self, skin, fish, reproduceProbability ):
		self.boids = []
		self.skin = skin
		self.fish = fish
		self.reproduceProbability = reproduceProbability

	def addBoid( self, boid ):
		self.boids.append( boid )

	def run( self, sharks, food, screen, fishImage, fishImageSmall, font, height, width ):
		for boid in self.boids:
			closeBoids = []
			closeSharks = []
			for shark in sharks:
				distance = boid.distance( shark )
				if distance < boid.vision:
					closeSharks.append( shark )

			if len( closeSharks ) > 0: # Avoid sharks
				boid.moveAway( closeSharks, 60 )
			elif boid.energy < 5000: 
				closeFood = []
				for sprite in food:
					if sprite.energy < 1:
						sprite.remove()
						continue
					distance = boid.distance( sprite.rect )
					if distance < boid.vision:
						closeFood.append( sprite )

				if len( closeFood ) > 0: # Eat
					boid.moveCloser( closeFood )
					boid.energy += 10
					for sprite in closeFood:
						sprite.energy -= 1
				else: # Boids
					canReproduce = False
					for otherBoid in self.boids:
						if otherBoid.id == boid.id:
							continue

						distance = boid.distance( otherBoid )
						if distance < boid.vision:
							closeBoids.append( otherBoid )
						if distance < 100:
							canReproduce = True
							
					if canReproduce:
						probability = random()
						if probability < self.reproduceProbability:
							if boid.type == 0:
								newBoid = Individual( 0, self.boids[-1].id + 1, self.fish, boid.x, boid.y )
							else:
								newBoid = Individual( 1, self.boids[-1].id + 1, self.fish, boid.x, boid.y )
							self.boids.append( newBoid )

					boid.moveCloser( closeBoids )
					boid.moveWith( closeBoids )
					boid.moveAway( closeBoids, 40 )
			else: # Boids
				canReproduce = False
				for otherBoid in self.boids:
					if otherBoid.id == boid.id:
						continue

					distance = boid.distance( otherBoid )
					if distance < boid.vision:
						closeBoids.append( otherBoid )
					if distance < 100:
						canReproduce = True
						
				if canReproduce:
					probability = random()
					if probability < self.reproduceProbability:
						if boid.type == 0:
							newBoid = Individual( 0, self.boids[-1].id + 1, self.fish, boid.x, boid.y )
						else:
							newBoid = Individual( 1, self.boids[-1].id + 1, self.fish, boid.x, boid.y )
						self.boids.append( newBoid )

				boid.moveCloser( closeBoids )
				boid.moveWith( closeBoids )
				boid.moveAway( closeBoids, 40 )

			border = 25
			if boid.x < border and boid.velocityX < 0:
				boid.velocityX = -boid.velocityX * random()
			if boid.x > width - border and boid.velocityX > 0:
				boid.velocityX = -boid.velocityX * random()
			if boid.y < border and boid.velocityY < 0:
				boid.velocityY = -boid.velocityY * random()
			if boid.y > height - border and boid.velocityY > 0:
				boid.velocityY = -boid.velocityY * random()
				
			boid.move()
			
		i = 0
		while i < len( self.boids ):
			boid = self.boids[i]
			boid.energy -= 1
			if boid.energy < 1:
				del self.boids[i]
				i -= 1

			boidRect = pygame.Rect( boid.rect )
			boidRect.x = boid.x
			boidRect.y = boid.y
			screen.blit( boid.image, boidRect )
			skinRect = pygame.Rect( self.skin.get_rect() )
			skinRect.x = boid.x
			skinRect.y = boid.y
			screen.blit( self.skin, skinRect )
			screen.blit( font.render( str( boid.energy ), True, ( 0, 0, 0 ) ), boidRect )

			i += 1

class SharkSet():
	def __init__( self ):
		self.sharks = []

	def addShark( self, shark ):
		self.sharks.append( shark )

	def run( self, boids, screen, height, width ):
		for shark in self.sharks:
			closeBoids = []
			for boid in boids:
				distance = shark.distance( boid )
				if distance < VISION:
					closeBoids.append( boid )
				if distance < 50:
					boid.energy -= 10000

			shark.moveCloser( closeBoids )

			border = 25
			if shark.x < border and shark.velocityX < 0:
				shark.velocityX = -shark.velocityX * random()
			if shark.x > width - border and shark.velocityX > 0:
				shark.velocityX = -shark.velocityX * random()
			if shark.y < border and shark.velocityY < 0:
				shark.velocityY = -shark.velocityY * random()
			if shark.y > height - border and shark.velocityY > 0:
				shark.velocityY = -shark.velocityY * random()

			shark.move()

		for shark in self.sharks:
			sharkRect = pygame.Rect( shark.rect )
			sharkRect.x = shark.x
			sharkRect.y = shark.y
			screen.blit( shark.image, sharkRect )

class TreeSet():
	def __init__( self ):
		self.trees = []

	def addTree( self, tree ):
		self.trees.append( tree )

	def draw( self, screen ):
		for tree in self.trees:
			treeRect = pygame.Rect( tree.rect )
			treeRect.x = tree.x
			treeRect.y = tree.y
			screen.blit( tree.image, treeRect )

class FoodSet():
	def __init__( self ):
		self.food = pygame.sprite.RenderPlain()

	def add( self, trees ):
		tree = trees[randomRange( len( trees ) )]

		self.food.empty()
		for i in range( 200 ):
			self.food.add( Food( randomRange( tree.x - 100, tree.x + 100 ), randomRange( tree.y - 100, tree.y + 100 ) ) )

	def draw( self, screen ):
		self.food.draw( screen )

class Individual():
	def __init__( self, type, id, image, x, y ):
		self.type = type
		self.id = id
		self.image = image
		self.x = x
		self.y = y
		self.velocityX = randomRange( 1, MAX_VELOCITY ) / MAX_VELOCITY
		self.velocityY = randomRange( 1, MAX_VELOCITY ) / MAX_VELOCITY
		self.energy = ENERGY
		self.vision = VISION
		self.rect = self.image.get_rect()

	def distance( self, individual ):
		distanceX = self.x - individual.x
		distanceY = self.y - individual.y

		return math.sqrt( distanceX * distanceX + distanceY * distanceY )

	def moveCloser( self, individuals ):
		if len( individuals ) < 1:
			return

		avgX = 0
		avgY = 0
		for individual in individuals:
			if individual.x == self.x and individual.y == self.y:
				continue

			avgX += ( self.x - individual.x )
			avgY += ( self.y - individual.y )

		avgX /= len( individuals )
		avgY /= len( individuals )

		self.velocityX -= ( avgX / 100 )
		self.velocityY -= ( avgY / 100 )

	def moveWith( self, individuals ):
		if len( individuals ) < 1:
			return

		avgX = 0
		avgY = 0

		for individual in individuals:
			avgX += individual.velocityX
			avgY += individual.velocityY

		avgX /= len( individuals )
		avgY /= len( individuals )

		self.velocityX += ( avgX / 40 )
		self.velocityY += ( avgY / 40 )

	def moveAway( self, individuals, minDistance ):
		if len( individuals ) < 1:
			return

		distanceX = 0
		distanceY = 0
		numClose = 0

		for individual in individuals:
			distance = self.distance( individual )
			if distance < minDistance:
				numClose += 1
				xdiff = ( self.x - individual.x )
				ydiff = ( self.y - individual.y )

				if xdiff >= 0:
					xdiff = math.sqrt( minDistance ) - xdiff
				elif xdiff < 0:
					xdiff = -math.sqrt( minDistance ) - xdiff

				if ydiff >= 0:
					ydiff = math.sqrt( minDistance ) - ydiff
				elif ydiff < 0:
					ydiff = -math.sqrt( minDistance ) - ydiff

				distanceX += xdiff
				distanceY += ydiff

		if numClose == 0:
			return

		self.velocityX -= distanceX / 5
		self.velocityY -= distanceY / 5

	def move( self ):
		if abs( self.velocityX ) > MAX_VELOCITY or abs( self.velocityY ) > MAX_VELOCITY:
			scaleFactor = MAX_VELOCITY / max( abs( self.velocityX ), abs( self.velocityY ) )
			self.velocityX *= scaleFactor
			self.velocityY *= scaleFactor

		self.x += self.velocityX
		self.y += self.velocityY

class Fish( Individual ):
	def move( self ):
		pass

class Shark( Individual ):
	def move( self ):
		pass

class Food( pygame.sprite.Sprite ):
	def __init__( self, x, y ):
		pygame.sprite.Sprite.__init__( self )
		self.x = x
		self.y = y
		self.color = "red"
		self.width = 10
		self.height = 10
		self.image = self.draw()
		self.rect = Rect( x, y, self.width, self.height )
		self.energy = FOOD_ENERGY

	def draw( self ):
		screen = pygame.Surface( ( self.width, self.height ) )
		screen.set_colorkey( ( 0, 0, 0 ) )
		pygame.gfxdraw.filled_circle( screen, int( self.width / 2 ), int( self.height / 2 ), int( self.height / 2 - 1 ), THECOLORS[self.color] )

		return screen