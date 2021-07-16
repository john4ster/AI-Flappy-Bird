import pygame
import neat
import os
import random

#Set up window
WIN_WIDTH = 600
WIN_HEIGHT = 800
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("AI Flappy Bird")

#current_gen variable to be used for generation text display
current_gen = 0

#Load in images
BIRD_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "bird.png"))).convert()
PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("images", "pipe.png"))).convert()
GROUND_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join("images", "ground.png")), (WIN_WIDTH, 150)).convert()
BACKGROUND_IMAGE = pygame.transform.scale(pygame.image.load(os.path.join("images", "background.png")), (WIN_WIDTH, WIN_HEIGHT)).convert()

#Class to handle the bird's position and movement
class Bird():
  IMAGE = BIRD_IMAGE

  #Constructor
  def __init__(self, x, y):
    self.initial_x = x
    self.initial_y = y
    self.original_image = BIRD_IMAGE #Original image to be used for rotation
    self.image = BIRD_IMAGE #Image that will be drawn to the screen
    self.image_rect = self.image.get_rect(midtop = (x, y))
    self.dead = False
    self.gravity = 0.2
    self.movement = 0

  #Moves the bird upwards a certain amount (movement)
  def flap(self):
    #Make sure bird isn't dead before moving it
    if self.dead == False:
      #Move the bird up
      self.movement = 6
      self.image_rect.centery -= self.movement
      self.rotate(-15)

  #Method to move the bird up or down
  def update_gravity(self):
    #Accelerate gravity
    self.movement -= self.gravity
    #Check if bird is dead before moving it
    if self.dead == False:
      self.image_rect.centery -= self.movement
      self.rotate(15)
    #If the bird is dead, rotate it down 90 degrees so it's facing the ground and move it down to the ground
    else:
      self.rotate(-90)
      #Continue moving bird until it hits the ground
      if self.image_rect.centery <= WIN_HEIGHT - 150:
          self.image_rect.centery -= self.movement

  #Method to rotate the bird
  def rotate(self, angle):
    self.image = pygame.transform.rotate(self.original_image, angle)

#Class to handle each pair of pipes (top and bottom pipes)
class PipePair():
  #Images for bottom pipe and top pipe
  BOTTOM_IMAGE = PIPE_IMAGE
  TOP_IMAGE = pygame.transform.flip(PIPE_IMAGE, False, True)

  #Constructor
  def __init__(self, bottom_x, bottom_y):
    #Both pipes in a pair have the same x position
    self.x = bottom_x
    #Setup bottom pipe
    self.bottom_y = bottom_y
    self.bottom_image_rect = self.BOTTOM_IMAGE.get_rect(midtop = (self.x, self.bottom_y))
    #Setup top pipe (y should be bottom_x minus the gap between pipes)
    self.top_y = self.bottom_y - 805
    self.top_image_rect = self.TOP_IMAGE.get_rect(midtop = (self.x, self.top_y))

  #Method to move the pipes to the left
  def move(self, movement):
    self.bottom_image_rect.centerx -= movement
    self.top_image_rect.centerx -= movement

#Class to handle the moving ground
class Ground():
  GROUND_IMAGE = GROUND_IMAGE

  def __init__(self, x ,y):
    self.x = x
    self.y = y

  def move(self, ground_movement):
    self.x -= ground_movement #Keep ground moving to the left
    #Reset ground position before the ground goes off screen
    if self.x <= -WIN_WIDTH:
      self.x = 0
    return self.x

#Function to check collisions
def check_collisions(birds, pipes, ground):
  #Check collision between birds and pipes
  for pipe in pipes:
    for bird in birds:
      if bird.image_rect.colliderect(pipe.bottom_image_rect) or bird.image_rect.colliderect(pipe.top_image_rect):
        bird.dead = True

  #Check collision between birds and ground
  for bird in birds:
    if bird.image_rect.bottom >= ground.y:
      bird.dead = True

  #Check if bird goes above height limit, helps avoid birds trying to go over pipes
  for bird in birds:
    if bird.image_rect.centery <= 0:
      bird.dead = True

#Function to spawn a new pipe
def spawn_pipe():
  #Get a random height for each pipe pair
  pipe_heights = [200, 400, 600]
  random_height = random.choice(pipe_heights)
  #Return the new pipe, spawned off screen to make enough space between pipes
  return PipePair(WIN_WIDTH + 100, random_height)

#Functions to draw everything to the screen
def draw_background():
  screen.blit(BACKGROUND_IMAGE, (0, 0))

def draw_ground(ground):
  #Draws 2 ground images right next to each other to help with animation
  screen.blit(ground.GROUND_IMAGE, (ground.x, ground.y))
  screen.blit(ground.GROUND_IMAGE, (ground.x + WIN_WIDTH, ground.y))

def draw_pipes(incoming_pipes, passed_pipes):
  #Draw both incoming pipes and passed pipes
  for pipe in incoming_pipes:
    screen.blit(pipe.BOTTOM_IMAGE, pipe.bottom_image_rect)
    screen.blit(pipe.TOP_IMAGE, pipe.top_image_rect)
  for pipe in passed_pipes:
    screen.blit(pipe.BOTTOM_IMAGE, pipe.bottom_image_rect)
    screen.blit(pipe.TOP_IMAGE, pipe.top_image_rect)

def draw_birds(birds):
  for bird in birds:
    screen.blit(bird.image, bird.image_rect)

def draw_text(score, gen, font):
  #Display score
  score_surface = font.render(str(score), True, (255, 255, 255))
  score_rect = score_surface.get_rect()
  score_rect.center = (WIN_WIDTH / 2, 100)
  screen.blit(score_surface, score_rect)
  #Display current gen
  gen_surface = font.render("Gen: " + str(gen - 1), True, (255, 255, 255))
  gen_rect = gen_surface.get_rect()
  gen_rect.center = (70, 20)
  screen.blit(gen_surface, gen_rect)

#eval_genomes function for the neat algorithm, this function also operates as the main game function
def eval_genomes(genomes, config):
  birds = [] #List of birds
  bird_initial_x = 200 #Initial x position of bird
  bird_initial_y = 200 #Initial y position of bird
  #Setup neat algorithm stuff
  nets = [] #List of neural networks
  genome_list = [] #List of genomes
  global current_gen
  current_gen += 1
  #Make a bird and neural network for each genome
  for genome_id, genome in genomes:
    genome.fitness = 0
    birds.append(Bird(bird_initial_x, bird_initial_y))
    nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
    genome_list.append(genome)
  #Initialize pygame
  pygame.init()
  #Initialize variables
  #Initialize ground and ground movement
  ground = Ground(0, WIN_HEIGHT - 150)
  ground_movement = 1
  #Initialize first pipe, incoming pipe list, passed pipes, and pipe movement
  first_pipe = spawn_pipe()
  incoming_pipes = [first_pipe] #Pipes the bird has not passed by
  passed_pipes = [] #Pipes the bird has passed by
  pipe_movement = 3
  #Initialize score and score font
  score = 0
  score_font = pygame.font.Font(os.path.join("fonts", "04B_19.TTF"),40)
  #Set up pygame clock
  CLOCK = pygame.time.Clock()
  #Set up timer to spawn pipes
  SPAWN_PIPE = pygame.USEREVENT
  pygame.time.set_timer(SPAWN_PIPE, 1200)

  #Start game loop
  running = True
  while running and len(birds) > 0:
    for event in pygame.event.get():
      #Check if user quits game
      if event.type == pygame.QUIT:
        pygame.quit()
        quit()

    #Increase fitness for each clock tick the birds are alive to increase incentive for them to survive
    for bird in birds:
      if bird.dead == False:
        genome_list[birds.index(bird)].fitness += 0.1
    
    #Check each bird's neural network output
    for bird in birds:
      #Run each network's activation function, and give it some fitness for still being alive
      #The network is given 4 inputs: the bird's y position, the distance between the bird's y and the bottom
      #pipe's y, the distance between the bird's y and the top pipe's y, and the distance between the bird and 
      #the ground. The network can give 2 outputs: either it flaps or it doesn't
      genome_list[birds.index(bird)].fitness += 0.5
      output = nets[birds.index(bird)].activate((bird.image_rect.centery,bird.image_rect.centery - incoming_pipes[0].bottom_y, incoming_pipes[0].top_y - bird.image_rect.centery, bird.image_rect.centery - ground.y))
      #If the output is greater than 0.5, make the bird flap
      if output[0] > 0.5:
        bird.flap()

    #Loop through incoming_pipes list and move each pipe
    for pipe in incoming_pipes:
      pipe.move(pipe_movement)
      #Check if birds have passed the pipe
      if pipe.bottom_image_rect.centerx < bird_initial_x:
        #Increase score if they have passed a pipe
        score += 1
        #If a pipe has been passed, spawn a new one
        if len(incoming_pipes) == 1:
          new_pipe = spawn_pipe()
          incoming_pipes.append(new_pipe)
          #Add old pipe to passed_pipes
          passed_pipes.append(pipe)
        #Increase each bird's fitness
        for bird in birds:
          genome_list[birds.index(bird)].fitness += 3
      
    #Loop through passed_pipes list and move each pipe
    for pipe in passed_pipes:
      pipe.move(pipe_movement)
      #Check if the pipe is in the incoming_pipes list as well, if it is, remove it from incoming_pipes
      if pipe in incoming_pipes:
        incoming_pipes.remove(pipe)
      #Check if pipe has gone off screen, if it has, remove it from the passed pipe list
      #(at this point it will not be in either pipe list, as we do not need to draw it or account for it anymore)
      if pipe.bottom_image_rect.right < 0:
        passed_pipes.remove(pipe)

    #Update bird gravity
    for bird in birds:
      bird.update_gravity()

    #Move the ground for ground animation
    ground.move(ground_movement)

    #Check collisions
    check_collisions(birds, incoming_pipes, ground)

    #Remove dead birds
    for x, bird in enumerate(birds):
      if bird.dead == True:
        genome_list[x].fitness -= 1
        birds.pop(x)
        nets.pop(x)
        genome_list.pop(x)
    
    #Reset score at the end of each generation
    if len(birds) == 0:
      score = 0

    #Draw everything to the screen
    draw_background()
    draw_pipes(incoming_pipes, passed_pipes)
    draw_ground(ground)
    draw_birds(birds)
    draw_text(score, current_gen, score_font)

    pygame.display.update()
    CLOCK.tick(120)

def run(config_file):
  #Load configuration
  config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                              neat.DefaultStagnation, config_file)
  
  #Setup neat population
  p = neat.Population(config)

  #Shows neat stats
  p.add_reporter(neat.StdOutReporter(True))
  stats = neat.StatisticsReporter()
  p.add_reporter(stats)

  p.run(eval_genomes, 100)

if __name__ == "__main__":
  #Get neat config info from file
  config_path = "./neat_config.txt"
  run(config_path)