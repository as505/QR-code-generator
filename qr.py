import pygame
import reedsolo
from PIL import Image

# Debug input data
DATA = 321                  # INPUT
DB_1 = DATA.to_bytes(2)     # Used for Reed Solomon

bitTest = "0101000001"                  # 321 in binary, padded to 10 bits
bitTestCharacterCount = "011"           # 3 characters are encoded
bitTestFullString = "0101000001011"     # Combine to one string
# MicroQR size 1 has 3 data blocks
bitTestBlock1 = "00001011"
bitTestBlock2 = "00001010"
bitTestBlock3 = "0000"                  # Third datablock for size 1 only holds 4 modules


# Test Reed solomon
rcs = reedsolo.RSCodec(2)
ecTestBlock1 = rcs.encode(DB_1)

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

# Creates timing pattern used to determine QR code size
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
    #bitmask = 0 << size
    bitmask = "0"
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


def write_rect_module_cell(width, binary, x, y, upwards):
    cellX = 0
    cellY = 0
    if upwards:
        direction = 1
        cellX = x
        cellY = y
    else:
        direction = -1
        raise ValueError("ERROR, DOWNWARD MODULE NOT IMPLEMENTED YET")

    for bit in list(binary):
    
        if bit == "1":
            draw_module(BLACK, cellX, cellY)
        
        cellX = cellX + direction
        if (cellX > x+width):
            cellX = x
            cellY += direction
        elif (cellX < x):
            cellX = x+width
            cellY += direction



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
             



# MicroQR has 4 mask patterns
# The mask Mask keyfunction determines how the mask pattern is generated,
# while draw_mask() is responsible for generating and overlaying the mask pattern over the QR code 
def mask_keyfunc_0(i, j):
    if (j % 2) == 0:
        return 1


def mask_keyfunc_1(i, j):
    if (((j//2)+(i//3)) % 2) == 0:
        return 1


def mask_keyfunc_2(i, j):
    if ((j*i % 2) + (j*i % 3)) % 2 == 0:
        return 1


def mask_keyfunc_3(i, j):
    if (((i+j) % 2) + (i*j % 3)) % 2 == 0:
        return 1

# Generate and overlay mask over QR code
def draw_mask(mask_keyfunc):
    j = 1
    while (j < MODULECOUNT):
        i = 1
        while (i < MODULECOUNT):
            if mask_keyfunc(j, i):
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


# Print image file for QR code
def print_QR_image(print_size):
    output_image = Image.new('RGB', ((MODULECOUNT+BORDER*2)*print_size, (MODULECOUNT+BORDER*2)*print_size))
    x = 0
    y = 0
    color = 0
    while (y < MODULECOUNT+BORDER*2):
        x = 0
        while(x < MODULECOUNT+BORDER*2):
            module = screen.get_at((x*MODULESIZE, y*MODULESIZE))
            
            if (module == BLACK):
                color = BLACK
            elif (module == WHITE):
                color = WHITE

            draw_scaled_pixel(output_image,scale=print_size, x=x*print_size, y=y*print_size, value=color)
            x = x+1
        y = y+1
    
    output_image.save('QR.png')

# One module gets represented by one pixel, 
# this function lets us scale that pixel by a power of 2 to make a higher resolution / larger image
def draw_scaled_pixel(image, scale, x, y, value):
    i = 0
    j = 0
    while (j < scale):
        i = 0
        while(i < scale):
            image.putpixel(xy=(x+i, y+j), value=value)
            i = i+1
        j = j+1



pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("QR")




run = True
output_size = 1

while run:
    for event in pygame.event.get():    
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                output_size = output_size*2
                print(f"SCALE : {output_size}")
            elif event.key == pygame.K_DOWN:
                # Minimum size is 1
                if output_size < 2:
                    output_size = int(1)
                else:
                    output_size = int(output_size/2)
                print(f"SCALE : {output_size}")
            elif event.key == pygame.K_p:
                print_QR_image(output_size)

    # rezise QR code to fit screen
    screen_height = screen.get_height()
    screen_width = screen.get_width()
    scalefactor = screen_width

    if scalefactor > screen_height:
        scalefactor = screen_height
    # Set scale of qr code modules
    
    MODULESIZE = int(scalefactor/(MODULECOUNT+1)/2)

    # Draw QR Code
    screen.fill(WHITE)
    create_marker()
    create_timing()
    #create_vertical_module_cell(8, bitTestBlock1, 12, 12)
    #create_horizontal_module_cell(8, int.from_bytes(test), 12-4, 12)
    # Data Blocks
    write_rect_module_cell(2, bitTestBlock3, 11, 1, True)
    write_rect_module_cell(2, bitTestBlock2, 11, 5, True)
    write_rect_module_cell(2, bitTestBlock1, 11, 9, True)
    # EC Blocks
    write_rect_module_cell(4, ecTestBlock1, 7, 11, True)
    #draw_mask(mask_keyfunc=mask_keyfunc_0)

    pygame.display.flip()

pygame.quit


