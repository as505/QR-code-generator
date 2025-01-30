import pygame
import reedsolo

# Debug input data
DATA = 321                  # INPUT
DB_1 = DATA.to_bytes(2)     # Used for Reed Solomon

# Default window size
WIDTH = 360
HEIGHT = 480

### QR SETTINGS
VERSION = 1
RESOLUTION = 15
MODULESIZE = 10
MODULECOUNT = 0
BORDER = 2

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

### Set number of modules
### Micro QR can have 4 sizes
assert VERSION < 5
assert VERSION > 0

if VERSION == 1:
    MODULECOUNT = 11
elif VERSION == 2:
    MODULECOUNT = 13
elif VERSION == 3:
    MODULECOUNT = 15
elif VERSION == 4:
    MODULECOUNT = 17


# Test Reed solomon
rcs = reedsolo.RSCodec(2)
test = rcs.encode(DB_1)


DATAWRITEX = MODULECOUNT-1
DATAWRITEY = MODULECOUNT

def draw_module(col, x, y):
    rect = pygame.Rect(x*MODULESIZE, y*MODULESIZE, MODULESIZE, MODULESIZE)
    pygame.draw.rect(screen, col, rect)


def create_marker():
    #draw_module(BLACK, 2, 2)
    rect_1 = pygame.Rect((BORDER)*MODULESIZE, (BORDER)*MODULESIZE, MODULESIZE*7, MODULESIZE*7)
    rect_2 = pygame.Rect((BORDER+1)*MODULESIZE, (BORDER+1)*MODULESIZE, MODULESIZE*5, MODULESIZE*5)
    rect_3 = pygame.Rect((BORDER+2)*MODULESIZE, (BORDER+2)*MODULESIZE, MODULESIZE*3, MODULESIZE*3)
    pygame.draw.rect(screen, BLACK, rect_1)
    pygame.draw.rect(screen, WHITE, rect_2)
    pygame.draw.rect(screen, BLACK, rect_3)


def create_timing():
    # Horizontal
    x = BORDER + 8 # Timing begins after whitespace border, and marker
    y = BORDER
    while x < MODULECOUNT+(BORDER):
        draw_module(BLACK, x, y)
        x += 2

    # Vertical
    y = BORDER + 8 # Timing begins after whitespace border, and marker
    x = BORDER
    while y < MODULECOUNT+(BORDER):
        draw_module(BLACK, x, y)
        y += 2


# TODO Fix module order in module cell functions
# TODO dynamically change module shape to fit all qr versions
def create_vertical_module_cell(size, binary, x, y):
    CurrentDigit = 0
    bitmask = 0b0
    cellX = 0
    y -= 3
    x -= 1
    # Extract bit from binary number
    while CurrentDigit < size:

        bitmask = 1 << CurrentDigit
        digit = binary & bitmask
        digit = digit >> CurrentDigit

        CurrentDigit += 1
        # Draw if 1
        if digit:
            draw_module(BLACK, x, y)
        
        cellX += 1
        if cellX > 1:
            cellX = 0
            x -= 1
            y += 1
        else:
            x += 1


def create_horizontal_module_cell(size, binary, x, y):
    CurrentDigit = 0
    bitmask = 0b0
    module = 0
    # Extract bit from binary number
    while CurrentDigit < size:

        bitmask = 1 << CurrentDigit
        digit = binary & bitmask
        digit = digit >> CurrentDigit

        CurrentDigit += 1
        # Draw if 1
        if digit:
            draw_module(BLACK, x, y)

        module += 1
        if module == 3:
            x -= 1
            y -= 1
        
        if module == 6:
            x -= 1
            y += 1
             

# TODO Simplify mask patern functions to use less duplicated code
# MicroQR has 4 mask patterns
def draw_mask_0():
    j = 1
    while (j < MODULECOUNT):
        i = 1
        while (i < MODULECOUNT):  
            if (j % 2) == 0:
                if i < 9 and j < 9:
                    pass
                else:
                    module = screen.get_at((i+BORDER, j+BORDER))
                    if module == WHITE:
                        draw_module(BLACK, i+BORDER, j+BORDER)
                    elif module == BLACK:
                        draw_module(WHITE, i+BORDER, j+BORDER)
            i = i + 1
        j = j + 1


def draw_mask_1():
    j = 1
    while (j < MODULECOUNT):
        i = 1
        while (i < MODULECOUNT):  
            if (((j//2)+(i//3)) % 2) == 0:
                if i < 9 and j < 9:
                    pass
                else:
                    module = screen.get_at((i+BORDER, j+BORDER))
                    if module == WHITE:
                        draw_module(BLACK, i+BORDER, j+BORDER)
                    elif module == BLACK:
                        draw_module(WHITE, i+BORDER, j+BORDER)
            i = i + 1
        j = j + 1


def draw_mask_2():
    j = 1
    while (j < MODULECOUNT):
        i = 1
        while (i < MODULECOUNT):  
            if ((j*i % 2) + (j*i % 3)) % 2 == 0:
                if i < 9 and j < 9:
                    pass
                else:
                    module = screen.get_at((i+BORDER, j+BORDER))
                    if module == WHITE:
                        draw_module(BLACK, i+BORDER, j+BORDER)
                    elif module == BLACK:
                        draw_module(WHITE, i+BORDER, j+BORDER)
            i = i + 1
        j = j + 1


def draw_mask_3():
    j = 1
    while (j < MODULECOUNT):
        i = 1
        while (i < MODULECOUNT):
            if (((i+j) % 2) + (i*j % 3)) % 2 == 0:
                if i < 9 and j < 9:
                    pass
                else:
                    module = screen.get_at((i+BORDER, j+BORDER))
                    if module == WHITE:
                        draw_module(BLACK, i+BORDER, j+BORDER)
                    elif module == BLACK:
                        draw_module(WHITE, i+BORDER, j+BORDER)
            i = i + 1
        j = j + 1


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("QR")




run = True


while run:
    for event in pygame.event.get():    
        if event.type == pygame.QUIT:
            run = False

    # rezise QR code to fit screen
    screen_height = screen.get_height()
    screen_width = screen.get_width()
    scalefactor = screen_width

    if scalefactor > screen_height:
        scalefactor = screen_height
    # Set scale of qr code modules
    MODULESIZE = scalefactor/(MODULECOUNT+1)/2

    # Draw QR Code
    screen.fill(WHITE)
    create_marker()
    create_timing()
    create_vertical_module_cell(8, DATA, 12, 12)
    create_horizontal_module_cell(8, int.from_bytes(test), 12-4, 12)
    draw_mask_3()

    pygame.display.flip()

pygame.quit


