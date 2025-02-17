import pygame
import reedsolo
from PIL import Image
from bitstring import BitArray

# Debug input data
DATA = 321                  # INPUT
DB_1 = DATA.to_bytes(2)     # Used for Reed Solomon

'''
input = 321

input data is split into groups of 3 digits
    321
each group is converted to binary
    0101000001
character count is 3 for 3 digits
m1 character count is 3 bits binary
    011
mode indicator is 0 bits for m1, since it only supports numerical
N/A + 011 + 0101000001
=
011 0101000001

split into groups 8, 8, 4

01101010 00001000 0000
'''
bitTestBlock1 = "01101010"
bitTestBlock2 = "00001000"
bitTestBlock3 = "0000"

# Test Reed solomon
rcs = reedsolo.RSCodec(2)
ecTestVar = rcs.encode(DB_1)


'''
ecTestBlock1 = rcs.encode(b'00000000101000001011')
#print(ecTestBlock1)

bitECblock1 = []
bitECblock2 = []
ec_written_bits = 0
for bit in ecTestBlock1:
    if ec_written_bits < 8:
        bitECblock1.append(bit)
    else:
        bitECblock2.append(bit)
    ec_written_bits += 1

#print(rcs.decode(ecTestBlock1))
#ecBits = BitArray(ecTestBlock1).bin
'''

# Default window size
WIDTH = 360
HEIGHT = 480

### QR SETTINGS
VERSION = 1
RESOLUTION = 15
MODULESIZE = 10
MODULECOUNT = 0
BORDER = 2

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)

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



def write_rect_module_cell(binary, x, y, upwards):
    cellX = x
    cellY = y
    if upwards:
        direction = 1
    else:
        direction = -1
        cellX += 1

    for bit in list(binary):
    
        if bit == "1":
            draw_module(BLACK, cellX, cellY)
        
        cellX = cellX + direction
        if (cellX > x+1):
            cellX = x
            cellY += 1
        elif (cellX < x):
            cellX = x+1
            cellY += 1


def find_next_position():
    pass

# Temp function
def create_horizontal_module_cell(binary, x, y):
    n = 8
    down_block = [4]
    up_block = [4]
    for bit in binary:
        print(bit)
        if n > 4:
            down_block.append(bit)
            n -= 1
        else:
            up_block.append(bit)
    
    write_rect_module_cell(up_block, x-2, y, True)
    write_rect_module_cell(down_block, x, y, False)
             
def create_test_ec_module_cell(binary, x, y):
    CurrentDigit = 0
    bitmask = 0b0
    module = 0
    # Extract bit from binary number
    while CurrentDigit < 16:
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
                if (i < 9 and j < 9):
                    pass
                else:
                    module = screen.get_at(((i+BORDER)*MODULESIZE, (j+BORDER)*MODULESIZE))
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
    write_rect_module_cell(bitTestBlock1, 11, 9, True)
    write_rect_module_cell(bitTestBlock2, 11, 5, True)
    write_rect_module_cell(bitTestBlock3, 11, 3, True)
    # EC Blocks
    #create_test_ec_module_cell(int.from_bytes(ecTestVar), 7, 11)
    draw_mask(mask_keyfunc=mask_keyfunc_3)

    pygame.display.flip()

pygame.quit


