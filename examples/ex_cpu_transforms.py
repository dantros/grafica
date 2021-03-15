# coding=utf-8
"""Transforming vertices in the CPU to create shapes."""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.gpu_shape import GPUShape
import grafica.transformations as tr

__author__ = "Daniel Calderon"
__license__ = "MIT"


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


# A class to store the application control
class Controller:
    fillPolygon = True


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')


def drawCall(shaderProgram, shape):

    # Binding the proper buffers
    glBindVertexArray(shape.vao)
    glBindBuffer(GL_ARRAY_BUFFER, shape.vbo)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, shape.ebo)

    # Describing how the data is stored in the VBO
    position = glGetAttribLocation(shaderProgram, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
    glEnableVertexAttribArray(position)
    
    color = glGetAttribLocation(shaderProgram, "color")
    glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
    glEnableVertexAttribArray(color)

    # This line tells the active shader program to render the active element buffer with the given size
    glDrawElements(GL_TRIANGLES, shape.size, GL_UNSIGNED_INT, None)


def createGPUShape():

    # Here the new shape will be stored
    gpuShape = GPUShape()

    v1 = np.array([0.25,0,    0,1])
    v2 = np.array([0.5,0.5,  0,1])
    v3 = np.array([0.5,0.25,0.0,1])

    v1p = np.matmul(tr.translate(0.1,0,0), v1)
    v2p = np.matmul(tr.translate(0.1,0,0), v2)
    v3p = np.matmul(tr.translate(0.1,0,0), v3)

    v1r = np.array([v1p[0], v1p[1], v1p[2]]) / v1p[3]
    v2r = np.array([v2p[0], v2p[1], v2p[2]]) / v2p[3]
    v3r = np.array([v3p[0], v3[1], v3p[2]]) / v3p[3]

    print(v1r)
    print(v2r)
    print(v3r)

    lista = [0,0,0, 1,1,1]
    indicess = []

    r = 0.5

    xt = np.array([1,0,0,1])

    for i in range(0,30):

        # attempt 1: modifying manually each vertex.
        #         positions                                                        colors
        #lista += [r * np.cos(0.1 *i * np.pi), r * np.sin(0.1 *i * np.pi), 0.0,    1,0,0]

        # attempt 2: using transforms
        xtp = np.matmul(tr.rotationZ(0.1 *i * np.pi), xt)
        xtr = np.array([xtp[0], xtp[1], xtp[2]]) / xtp[3]

        #         positions               colors
        lista += [xtr[0], xtr[1], xtr[2], 0,0,1]

        # do not forget the indices!
        indicess += [0, i+1, i+2]


    # removing the last spare vertex
    indicess.pop()

    # Defining the location and colors of each vertex  of the shape
    vertexData = np.array(
            lista,
            dtype = np.float32) # It is important to use 32 bits data

    print(vertexData)

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = np.array(indicess, dtype= np.uint32)
        
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


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Transforming vertices in the CPU", None, None)

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

    # Creating shapes on GPU memory
    gpuShape = createGPUShape()

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Triangle
        transform = tr.translate(0,-1,0)

        # updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(shaderProgram, "transform"), 1, GL_TRUE, transform)

        # drawing function
        drawCall(shaderProgram, gpuShape)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)


    # freeing GPU memory
    gpuShape.clear()
    
    glfw.terminate()