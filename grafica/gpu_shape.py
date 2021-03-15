# coding=utf-8
"""A convenience class container to reference a shape on GPU memory"""

#import OpenGL.GL as ogl
from OpenGL.GL import *

__author__ = "Daniel Calderon"
__license__ = "MIT"

class GPUShape:
    def __init__(self):
        """VAO, VBO, EBO and texture handlers to GPU memory"""
        
        self.vao = None
        self.vbo = None
        self.ebo = None
        self.texture = None
        self.size = None

    def __str__(self):
        return "vao=" + str(self.vao) +\
            "  vbo=" + str(self.vbo) +\
            "  ebo=" + str(self.ebo) +\
            "  tex=" + str(self.texture)

    def clear(self):
        """Freeing GPU memory"""

        if self.texture != None:
            glDeleteTextures(1, [self.texture])
        
        if self.ebo != None:
            glDeleteBuffers(1, [self.ebo])

        if self.vbo != None:
            glDeleteBuffers(1, [self.vbo])

        if self.vao != None:
            glDeleteVertexArrays(1, [self.vao])
        
        