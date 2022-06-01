import struct
import sys
import glfw
import numpy
from PIL import Image
import compushady
import compushady.formats
from compushady import *
from compushady.shaders import hlsl
from compushady.formats import R8G8B8A8_UNORM

# def read_texture(filename):
#     image = Image.open(filename)
#     pixels_to_format = image.load()
#     width, height = image.size
#
#     height = 2
#
#     pixels = [(0,0,0,0)] * width * height
#
#     for h in range(height):
#         for w in range(width):
#             pixels[h*width+w] = pixels_to_format[w,16+h]
#     return (width, height), pixels

#pixels_size, pixels = read_texture("sprites/peasant_.png")

# pixel_bytes = bytes(0)
# for pixel in pixels:
#     buffer = struct.pack('4B', pixel[0], pixel[1], pixel[2], pixel[3])
#     print(str(buffer) + " => " + str((pixel[0], pixel[1], pixel[2], pixel[3])))
#     pixel_bytes += buffer

# texture = Texture2D(pixels_size[0], pixels_size[1], compushady.formats.R8G8B8A8_UNORM)
# staging_buffer = Buffer(texture.size, HEAP_UPLOAD)


def to_array(lists):
    b = bytes(0)
    for item in lists:
        buff = struct.pack('8f', *item)
        b += buff
    return b


def move():
    global peasant, destination, delta_time, changed
    speed = 48
    current_position = [peasant[0], peasant[1]]
    if current_position[0] < destination[0]:
        current_position[0] += delta_time * speed
        if current_position[0] > destination[0]:
            current_position[0] = destination[0]
        changed = True
    elif current_position[0] > destination[0]:
        current_position[0] -= delta_time * speed
        if current_position[0] < destination[0]:
            current_position[0] = destination[0]
        changed = True
    elif current_position[1] < destination[1]:
        current_position[1] += delta_time * speed
        if current_position[1] > destination[1]:
            current_position[1] = destination[1]
        changed = True
    elif current_position[1] > destination[1]:
        current_position[1] -= delta_time * speed
        if current_position[1] < destination[1]:
            current_position[1] = destination[1]
        changed = True
    peasant[0] = current_position[0]
    peasant[1] = current_position[1]


def check_collisions():
    global peasant, draw, tree_1, tree_2, rock_1, rock_2

    if check_collision_with(tree_1):
        if peasant[0] == tree_1[0] + tree_1[2]:
            tree_1[2] -= 32
        if peasant[0] + peasant[2] == tree_1[0]:
            tree_1[2] -= 32
            tree_1[0] += 32
        if peasant[1] == tree_1[1] + tree_1[3] or peasant[1] + peasant[3] == tree_1[1]:
            if abs(peasant[0] - tree_1[0]) < abs(peasant[0] + peasant[2] - tree_1[0] + tree_1[2]):
                tree_1[2] -= 32
                tree_1[0] += 32
            else:
                tree_1[2] -= 32
        if tree_1[2] == 0:
            draw.remove(tree_1)

    if check_collision_with(tree_2):
        if peasant[1] == tree_2[1] + tree_2[3]:
            tree_2[3] -= 32
        if peasant[1] + peasant[3] == tree_2[1]:
            tree_2[3] -= 32
            tree_2[1] += 32
        if peasant[1] == tree_2[1] + tree_2[3] or peasant[1] + peasant[3] == tree_2[1]:
            if abs(peasant[1] - tree_2[1]) < abs(peasant[1] + peasant[3] - tree_2[1] + tree_2[3]):
                tree_2[3] -= 32
                tree_2[1] += 32
            else:
                tree_2[3] -= 32
        if tree_2[3] == 0:
            draw.remove(tree_2)

    if check_collision_with(tree_3):
        if peasant[1] == tree_3[1] + tree_3[3]:
            tree_3[3] -= 32
        if peasant[1] + peasant[3] == tree_3[1]:
            tree_3[3] -= 32
            tree_3[1] += 32
        if peasant[1] == tree_3[1] + tree_3[3] or peasant[1] + peasant[3] == tree_3[1]:
            if abs(peasant[1] - tree_3[1]) < abs(peasant[1] + peasant[3] - tree_3[1] + tree_3[3]):
                tree_3[3] -= 32
                tree_3[1] += 32
            else:
                tree_3[3] -= 32
        if tree_3[3] == 0:
            draw.remove(tree_3)

    check_collision_with(rock_1)
    check_collision_with(rock_2)


def check_collision_with(obj):
    global peasant
    is_left_intersected = obj[0] < peasant[0] < obj[0] + obj[2]
    is_right_intersected = obj[0] < peasant[0] + peasant[2] < obj[0] + obj[2]
    is_bottom_intersected = obj[1] < peasant[1] < obj[1] + obj[3]
    is_top_intersected = obj[1] < peasant[1] + peasant[3] < obj[1] + obj[3]

    if is_bottom_intersected and is_top_intersected:
        if is_left_intersected:
            left_collision(obj)
            return True
        elif is_right_intersected:
            right_collision(obj)
            return True
    elif is_left_intersected and is_right_intersected:
        if is_bottom_intersected:
            bottom_collision(obj)
            return True
        elif is_top_intersected:
            top_collision(obj)
            return True
    elif is_left_intersected:
        if is_bottom_intersected:
            if obj[0] - peasant[0] < obj[1] + obj[3] - peasant[1]:
                left_collision(obj)
            else:
                bottom_collision(obj)
            return True
        elif is_top_intersected:
            if obj[0] - peasant[0] < peasant[1] + peasant[3] - obj[1]:
                left_collision(obj)
            else:
                top_collision(obj)
            return True
    elif is_right_intersected:
        if is_bottom_intersected:
            if peasant[0] + peasant[2] - obj[0] < obj[1] + obj[3] - peasant[1]:
                right_collision(obj)
            else:
                bottom_collision(obj)
            return True
        elif is_top_intersected:
            if peasant[0] + peasant[2] - obj[0] < peasant[1] + peasant[3] - obj[1]:
                right_collision(obj)
            else:
                top_collision(obj)
            return True
    return False


def left_collision(obj):
    global peasant, destination
    destination[0] = obj[0] + obj[2]
    peasant[0] = obj[0] + obj[2]


def right_collision(obj):
    global peasant, destination
    destination[0] = obj[0] - peasant[2]
    peasant[0] = obj[0] - peasant[2]


def bottom_collision(obj):
    global peasant, destination
    destination[1] = obj[1] + obj[3]
    peasant[1] = obj[1] + obj[3]


def top_collision(obj):
    global peasant, destination
    destination[1] = obj[1] - peasant[3]
    peasant[1] = obj[1] - peasant[3]


def adjust_destination():
    global destination, peasant
    destination = [destination[0] - (peasant[2] * 0.5), destination[1] - (peasant[3] * 0.5)]


delta_time = 0
last_time = 0
time = 0

title_update_timer = 1

if not glfw.init():
    sys.exit()

glfw.window_hint(glfw.CLIENT_API, glfw.NO_API)


window = glfw.create_window(640, 480, "WCII", None, None)
if not window:
    sys.exit()

target = compushady.Texture2D(640, 480, R8G8B8A8_UNORM)
quads_staging_buffer = Buffer(8*4*7, HEAP_UPLOAD)
quads_buffer = Buffer(quads_staging_buffer.size, format = R8G8B8A8_UNORM)
shader = hlsl.compile("""
struct quad_s
{
    float2 pos;
    float2 size;
    float4 color;
};
RWTexture2D<float4> target : register(u0);
StructuredBuffer<quad_s> quads : register(t0);

[numthreads(8,8,1)]
void main(int3 tid : SV_DispatchThreadID)
{
    quad_s quad = quads[tid.z];
    if (tid.x > quad.pos.x + quad.size.x)
        return;
    if (tid.x < quad.pos.x)
        return;
    if (tid.y < quad.pos.y)
        return;
    if (tid.y > quad.pos.y + quad.size.y)
        return;
    target[tid.xy] = float4(quad.color);
}
""")
compute = Compute(shader, srv=[quads_buffer], uav=[target])

# a super simple clear screen procedure
clear_screen = compushady.Compute(hlsl.compile("""
RWTexture2D<float4> target : register(u0);

[numthreads(8, 8, 1)]
void main(int3 tid : SV_DispatchThreadID)
{
    target[tid.xy] = float4(0, 0, 0, 0);
}
"""), uav=[target])

swapchain = compushady.Swapchain(glfw.get_win32_window(window), R8G8B8A8_UNORM, 3)

grass =  [  0,   0, 640, 480, 126/255, 178/255, 107/255, 1]
peasant =[304, 224,  32,  32, 1, 1, 0, 1]
tree_1 = [ 32,  32, 160,  32,  23/255,  87/255,       0, 1]
tree_2 = [512,  96,  32, 192,  23/255,  87/255,       0, 1]
tree_3 = [544,  96,  32, 192,  23/255,  87/255,       0, 1]
rock_1 = [ 32, 416, 160,  32, 124/255, 117/255, 117/255, 1]
rock_2 = [160,  96,  64, 192, 124/255, 117/255, 117/255, 1]

draw = [grass, peasant, tree_1, tree_2, tree_3, rock_1, rock_2]

destination = [304, 224]

changed = True
while not glfw.window_should_close(window):
    glfw.poll_events()
    last_time = time
    time = glfw.get_time()
    delta_time = time - last_time

    title_update_timer += delta_time
    if title_update_timer > 1:
        glfw.set_window_title(window, "WCII | FPS: " + str(1 / delta_time))
        title_update_timer = 0

    if glfw.get_window_attrib(window, glfw.HOVERED):
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS:
            mouse_pos = glfw.get_cursor_pos(window)
            destination[0] = mouse_pos[0]
            destination[1] = mouse_pos[1]
            adjust_destination()

    move()
    check_collisions()

    if changed:
        clear_screen.dispatch(target.width, target.height, 1)
        quads_staging_buffer.upload(to_array(draw))
        quads_staging_buffer.copy_to(quads_buffer)
        compute.dispatch(target.width, target.height, 7)
        swapchain.present(target)
        changed = False

glfw.terminate()
