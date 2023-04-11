import pygame, neat, time, os, random, pickle

pygame.font.init()

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
#window
WIN_WIDTH = BG_IMG.get_width()
WIN_HEIGHT = 800

GEN = 0

#load images
BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)


#distance between pipe spawns:
PIPE_DISTANCE = 600

FPS = 30
SCORE_LIMIT = 50
#creating the bird
class Bird:
    #parameters
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0 # basically every tick is every frame / game iteration
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0] 
    #jump function for the bird
    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y
    #This gets called in the game loop
    #function figures out where the brid needs to move when called
    def move(self):
        self.tick_count += 1
        #when this exponentially lowers the bird velocity like a parabola.
        #e.g. when bird jumps the vel is -10.5, after each 
        d = self.vel*self.tick_count + 1.5*self.tick_count**2

        #setting max movement (d)
        if d >= 16:
            d = 16
        if d < 0 :
            d -= 2

        #adds displacement to old pos for new pos
        self.y = self.y + d

        #calculates bird rotation based on if bird is going up or down 
        ####if moving up
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        ##if moving down
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL
    
    #animates our bird
    def draw(self, win):
        self.img_count += 1
     
        #Loops through the 3 images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        #if bird is going down show only one animation
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            #sets img_count to the one after 1 so that when the bird jumps up the animation is fluid
            self.img_count = self.ANIMATION_TIME*2

        #rotates image
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        #to fix bird not being rotated by its center
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft = (self.x, self.y)).center)
        #draws bird
        win.blit (rotated_image, new_rect.topleft)

        #smn to do with collisions
    def get_mask(self):
        return pygame.mask.from_surface(self.img)



#pipe class:
class Pipe:
    """This class creates and draws the pipes for the map, + collision"""
    #gap between pipes
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        

        #bottom and top pipe y pos
        self.top = 0
        self.bottom = 0
        #flipped version of pipe for the roof
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        #normal pipe
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        #generates random heihgt for pipes
        self.set_height()

    def set_height(self):
        #randomly generates height of pipe.
         self.height = random.randrange(50, 450)
         self.top = self.height - self.PIPE_TOP.get_height()
         self.bottom = self.height + self.GAP

    def move(self):
        #Moves pipes by to the left by their set velocity
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    #collisions using masks (more accurate than rects)
    def collide(self, bird):
        #gets mask using function from bird
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        #checks for overlaps betwwen the bird and bottom pipe mask based on
        # their offset (distance betwwen each other)
        b_point = bird_mask.overlap(bottom_mask, bottom_offset) #if their is no collision these return NONE
        t_point = bird_mask.overlap(top_mask, top_offset)

        #if their is a collision return True
        if t_point or b_point:
            return True
        
        return False


class Base:
    """class for the ground"""
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        #sets the 2 bases after each other
        self.x1 = 0
        self.x2 = self.WIDTH 

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL 

        #if the x positions are completely off the screen, the base cycles
        #back behind the other base
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


###  DRAWS ALL OBJECTS ###
def draw_window(win, birds, pipes, base, score, gen):
    #background
    win.blit(BG_IMG, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    #draw score !maybe add to a fucntion
    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255,255,255))
    win.blit(text, (10, 10))

    text = STAT_FONT.render("Unstoppable FlappyBird", 1, (255, 0, 0))
    win.blit(text, (WIN_HEIGHT-30, 10))
    
                            
    base.draw(win)
    for bird in birds:
        bird.draw(win)

    pygame.display.update()


#main game loop
#genome and config are necessary parameters
#THIS IS THE FITNESS FUNCTION, takes in all the genomes and uses the game tp evaluate them
def main(genomes, config):
    global GEN
    GEN += 1
    nets = [] #nn
    ge = [] #genome
    birds = [] #the bird in each position has a corresponding nn and genome in the other lsit at same pos
 
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)


    #create instanes of objects 
    base = Base(730)
    pipes = [Pipe(PIPE_DISTANCE)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    #score to 0
    score = 0
    
    #sets frames universally (not dependent on computer speed)
    clock = pygame.time.Clock()

    run = True
    while run:
        ind = 0
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                run = False
                pygame.quit()
                quit()

        #Determines which pipe we should be looking at
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        #if no birds left quite loop
        else:
            run = False
            break

        #movement on the bird based on nn
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            #this plugs in the birds pos and the pipes pos and gets a outpiut using nn
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            #if the nn gives a larger than 0.5 output, the bird should jump
            if output[0] > 0.5:
                bird.jump()
        
        #!add this to a function
        add_pipe = False
        rem = []
        ### Loops through all birds and pipes
        for pipe in pipes:
            for x, bird in enumerate(birds):
                #checks for collisioj
                if pipe.collide(bird):
                    #lowers fitness if bird hits pipe
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)


                if not pipe.passed and pipe.x < bird.x: #Checks if pipe is past the bird
                    pipe.passed = True
                    add_pipe = True
            
             #if pipe is out of the screen remove
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            #moves all pipes to the left
            pipe.move()

        if add_pipe:
            score += 1
            #any bird thats alive and went through a pipe gets +5 fitness
            for g in ge:
                g.fitness += 5

            pipes.append(Pipe(PIPE_DISTANCE))

        for r in rem:
            pipes.remove(r)

        #cehck if all birds have hit the ground
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x) 

        if score > SCORE_LIMIT:
            
            global net_pickled
            global ge_pickled

            net_pickled = pickle.dumps(nets[0])
            ge_pickled = pickle.dumps(ge[0])

            

            break

        base.move()
    
        draw_window(win, birds, pipes, base, score, GEN)   

    





def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                          neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)


    #(fitness function, 50 times)
    winner = p.run(main ,50)


### copy of the game for 1 bird only:
def run_fittest():   
    net_fittest = pickle.loads(net_pickled) 
    ge_fittest = pickle.loads(ge_pickled)
    nets = [net_fittest] # create pickled version of this
    ge = [ge_fittest] # 
    birds = [Bird(230, 350)] # !!! 

    #create instances of objects 
    base = Base(730)
    pipes = [Pipe(PIPE_DISTANCE)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    #score to 0
    score = 0
    
    #sets frames universally (not dependent on computer speed)
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        #Determines which pipe we should be looking at
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        #if no birds left quit loop
        else:
            run = False
            break

        #movement on the bird based on nn
        for x, bird in enumerate(birds):
            bird.move()
            
            #this plugs in the birds pos and the pipes pos and gets a outpiut using nn
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            #if the nn gives a larger than 0.5 output, the bird should jump
            if output[0] > 0.5:
                bird.jump()
        
        
        add_pipe = False
        rem = []
        ### Loops through all birds and pipes
        for pipe in pipes:
            for x, bird in enumerate(birds):
                #checks for collisioj
                if pipe.collide(bird):
                    run = False

                if not pipe.passed and pipe.x < bird.x: #Checks if pipe is past the bird
                    pipe.passed = True
                    add_pipe = True
            
            #if pipe is out of the screen remove
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            #moves all pipes to the left
            pipe.move()

        if add_pipe:
            score += 1
            pipes.append(Pipe(PIPE_DISTANCE))

        for r in rem:
            pipes.remove(r)

        #cehck if all birds have hit the ground
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                run = False

       

        base.move()
        
        draw_window(win, birds, pipes, base, score, GEN)   




if __name__ == "__main__":
    #loads config file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    #runs the run function using the config file
    run(config_path)

    
    run_fittest()