# coding=utf-8
"""Ilustrating different transformations"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.gpu_shape import GPUShape
import grafica.transformations as tr

__author__ = "Daniel Calderon"
__license__ = "MIT"


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


# Transformation states that will operate over the shape
TR_STANDARD      = 0
TR_ROTATE_ZP     = 1
TR_ROTATE_ZM     = 2
TR_TRANSLATE     = 3
TR_UNIFORM_SCALE = 4
TR_NONUNIF_SCALE = 5
TR_REFLEX_Y      = 6
TR_SHEARING_XY   = 7


# Shapes
SP_TRIANGLE   = 0
SP_QUAD       = 1
SP_CUBE       = 2
SP_CIRCLE     = 3


# A class to store the application control
class Controller:
    showTransform = TR_STANDARD
    fillPolygon = True
    shape = SP_TRIANGLE
    animated = False


# we will use the global controller as communication with the callback function
controller = Controller()


def getTransform(showTransform, theta):

    if showTransform == TR_STANDARD:
        return tr.identity()

    elif showTransform == TR_ROTATE_ZP:
        return tr.rotationZ(theta)

    elif showTransform == TR_ROTATE_ZM:
        return tr.rotationZ(-theta)

    elif showTransform == TR_TRANSLATE:
        return tr.translate(0.3 * np.cos(theta), 0.3 * np.cos(theta), 0)

    elif showTransform == TR_UNIFORM_SCALE:
        return tr.uniformScale(0.7 + 0.5 * np.cos(theta))

    elif showTransform == TR_NONUNIF_SCALE:
        return tr.scale(
            1.0 - 0.5 * np.cos(1.5 * theta),
            1.0 + 0.5 * np.cos(2 * theta),
            1.0)

    elif showTransform == TR_REFLEX_Y:
        return tr.scale(1,-1,1)

    elif showTransform == TR_SHEARING_XY:
        return tr.shearing(0.3 * np.cos(theta), 0, 0, 0, 0, 0)
    
    else:
        # This should NEVER happend
        raise Exception()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_0:
        print("No transformations applied")
        controller.showTransform = TR_STANDARD

    elif key == glfw.KEY_1:
        print('Rotation Z+')
        controller.showTransform = TR_ROTATE_ZP

    elif key == glfw.KEY_2:
        print('Rotation Z-')
        controller.showTransform = TR_ROTATE_ZM

    elif key == glfw.KEY_3:
        print('Uniform Scaling')
        controller.showTransform = TR_UNIFORM_SCALE

    elif key == glfw.KEY_4:
        print('Non-uniform Scaling')
        controller.showTransform = TR_NONUNIF_SCALE

    elif key == glfw.KEY_5:
        print('Translation')
        controller.showTransform = TR_TRANSLATE

    elif key == glfw.KEY_6:
        print('Shearing XY')
        controller.showTransform = TR_SHEARING_XY

    elif key == glfw.KEY_7:
        print('Reflexion Y')
        controller.showTransform = TR_REFLEX_Y

    elif key == glfw.KEY_Q:
        print('Showing triangle')
        controller.shape = SP_TRIANGLE

    elif key == glfw.KEY_W:
        print('Showing quad')
        controller.shape = SP_QUAD

    elif key == glfw.KEY_E:
        print('Showing cube')
        controller.shape = SP_CUBE

    elif key == glfw.KEY_R:
        print('Showing circle')
        controller.shape = SP_CIRCLE

    elif key == glfw.KEY_A:
        print('Toggling animated')
        controller.animated = not controller.animated

    elif key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key. Try small numbers!')


def drawCall(shaderProgram, shape, transform):

    # Binding the proper buffers
    glBindVertexArray(shape.vao)
    glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

    # updating the new transform attribute
    glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, transform)

    # Describing how the data is stored in the VBO
    position = glGetAttribLocation(shaderProgram, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)
    
    color = glGetAttribLocation(shaderProgram, "color")
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)

    # This line tells the active shader program to render the active element buffer with the given size
    glDrawElements(GL_TRIANGLES, shape.size, GL_UNSIGNED_INT, None)


def createTriangle():

    # Here the new shape will be stored
    gpuShape = GPUShape()

    # Defining the location and colors of each vertex  of the shape
    vertexData = np.array(
    #     positions       colors
        [-0.7, -0.7, 0.0, 1.0, 0.0, 0.0,
          0.7, -0.7, 0.0, 0.0, 1.0, 0.0,
          0.0,  0.7, 0.0, 0.0, 0.0, 1.0],
          dtype = np.float32) # It is important to use 32 bits data

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = np.array(
        [0, 1, 2], dtype= np.uint32)
        
    gpuShape.size = len(indices)

    # VAO, VBO and EBO and  for the shape
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    return gpuShape


def createQuad():

    # Here the new shape will be stored
    gpuShape = GPUShape()

    # Defining locations and colors for each vertex of the shape
    
    vertexData = np.array([
    #   positions        colors
        -0.5, -0.5, 0.0,  1.0, 0.0, 0.0,
         0.5, -0.5, 0.0,  0.0, 1.0, 0.0,
         0.5,  0.5, 0.0,  0.0, 0.0, 1.0,
        -0.5,  0.5, 0.0,  1.0, 1.0, 1.0
    # It is important to use 32 bits data
        ], dtype = np.float32)

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = np.array(
        [0, 1, 2,
         2, 3, 0], dtype= np.uint32)

    gpuShape.size = len(indices)

    # VAO, VBO and EBO and  for the shape
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    # Vertex data must be attached to a Vertex Buffer Object (VBO)
    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, GL_STATIC_DRAW)

    # Connections among vertices are stored in the Elements Buffer Object (EBO)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    return gpuShape


def createCube():

    # Here the new shape will be stored
    gpuShape = GPUShape()

    # Defining the location and colors of each vertex  of the shape
    vertexData = np.array(
    #    positions        colors
       [-0.5, -0.5,  0.5, 1.0, 0.0, 0.0,
         0.5, -0.5,  0.5, 0.0, 1.0, 0.0,
         0.5,  0.5,  0.5, 0.0, 0.0, 1.0,
        -0.5,  0.5,  0.5, 1.0, 1.0, 1.0,

        -0.5, -0.5, -0.5, 1.0, 1.0, 0.0,
         0.5, -0.5, -0.5, 0.0, 1.0, 1.0,
         0.5,  0.5, -0.5, 1.0, 0.0, 1.0,
        -0.5,  0.5, -0.5, 1.0, 1.0, 1.0],
        dtype = np.float32) # We must use 32 bits data

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = np.array(
        [0, 1, 2, 2, 3, 0,
         4, 5, 6, 6, 7, 4,
         4, 5, 1, 1, 0, 4,
         6, 7, 3, 3, 2, 6,
         5, 6, 2, 2, 1, 5,
         7, 4, 0, 0, 3, 7], dtype= np.uint32)

    gpuShape.size = len(indices)

    # VAO, VBO and EBO and  for the shape
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    # Vertex data must be attached to a Vertex Buffer Object (VBO)
    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, GL_STATIC_DRAW)

    # Connections among vertices are stored in the Elements Buffer Object (EBO)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    return gpuShape


def createCircle(N):

    # Here the new shape will be stored
    gpuShape = GPUShape()

    # First vertex at the center, white color
    vertices = [0, 0, 0, 1.0, 1.0, 1.0]
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            0.5 * np.cos(theta), 0.5 * np.sin(theta), 0,

            # color generates varying between 0 and 1
                  np.sin(theta),       np.cos(theta), 0]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    vertices = np.array(vertices, dtype =np.float32)
    indices = np.array(indices, dtype= np.uint32)
        
    gpuShape.size = len(indices)

    # VAO, VBO and EBO and  for the shape
    gpuShape.vao = glGenVertexArrays(1)
    gpuShape.vbo = glGenBuffers(1)
    gpuShape.ebo = glGenBuffers(1)

    glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * SIZE_IN_BYTES, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW)

    return gpuShape


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Basic Linear Transformations - Modern OpenGL", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Defining shaders for our pipeline
    vertex_shader = """
    #version 130
    in vec3 position;
    in vec3 color;

    out vec3 fragColor;

    uniform mat4 transform;

    void main()
    {
        fragColor = color;
        gl_Position = transform * vec4(position, 1.0f);
    }
    """

    fragment_shader = """
    #version 130

    in vec3 fragColor;
    out vec4 outColor;

    void main()
    {
        outColor = vec4(fragColor, 1.0f);
    }
    """

    # Assembling the shader program (pipeline) with both shaders
    shaderProgram = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    # Telling OpenGL to use our shader program
    glUseProgram(shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    gpuTriangle = createTriangle()
    gpuQuad = createQuad()
    gpuCube = createCube()
    gpuCircle = createCircle(20)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if controller.animated:
            # Using the time as the theta parameter
            theta = glfw.get_time()
        else:
            theta = np.pi / 6
        
        transform = getTransform(controller.showTransform, theta)

        if (controller.shape == SP_TRIANGLE):
            drawCall(shaderProgram, gpuTriangle, transform)

        elif (controller.shape == SP_QUAD):
            drawCall(shaderProgram, gpuQuad, transform)

        elif (controller.shape == SP_CUBE):
            Rx = tr.rotationX(np.pi/3)
            Ry = tr.rotationY(np.pi/3)
            transform = tr.matmul([Ry, Rx, transform])
            drawCall(shaderProgram, gpuCube, transform)

        elif (controller.shape == SP_CIRCLE):
            drawCall(shaderProgram, gpuCircle, transform)

        else:
            # This should never happen
            raise Exception()

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuTriangle.clear()
    gpuQuad.clear()
    gpuCube.clear()
    gpuCircle.clear()
    
    glfw.terminate()