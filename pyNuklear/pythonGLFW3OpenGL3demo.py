#Copyright (c) 2017 William Emerison Six
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


import sys
import os
import OpenGL.GL as gl
import OpenGL.GL.shaders as shaders
import numpy as np
import glfw
import pyMatrixStack as ms
import ctypes
import math
import nuklear as nk

if __name__ != '__main__':
    sys.exit(1)

pwd = os.path.dirname(os.path.abspath(__file__))

glfloat_size = 4

floatsPerVertex = 3

class Triangle:
    def __init__(self):
        pass

    def prepareToRender(self):
        vertices = np.array([-0.6,  -0.4,  0.0,
                             0.6,   -0.4,  0.0,
                             0,     0.6,   0.0],
                            dtype=np.float32)

        self.numberOfVertices = np.size(vertices) // floatsPerVertex


        self.vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.vao)

        #initialize shaders

        with open(os.path.join(pwd, '..', 'shaders', 'triangle.vert'), 'r') as f:
            vs = shaders.compileShader(f.read() , gl.GL_VERTEX_SHADER)

        with open(os.path.join(pwd, '..', 'shaders', 'triangle.frag'), 'r') as f:
            fs = shaders.compileShader(f.read(), gl.GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(vs,fs)

        self.mvpMatrixLoc = gl.glGetUniformLocation(self.shader,"mvpMatrix")

        #send the modelspace data to the GPU
        vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

        position = gl.glGetAttribLocation(self.shader, 'position')
        gl.glEnableVertexAttribArray(position)

        gl.glVertexAttribPointer(position,
                                 floatsPerVertex,
                                 gl.GL_FLOAT,
                                 False,
                                 0,
                                 ctypes.c_void_p(0))

        gl.glBufferData(gl.GL_ARRAY_BUFFER,
                        glfloat_size * np.size(vertices),
                        vertices,
                        gl.GL_STATIC_DRAW)

        # reset VAO/VBO to default
        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER,0)


    def render(self):
        with ms.GLStackProtector(ms.MatrixStack.model):
            # rotate the triangle along the positive z axis
            ms.translate(ms.MatrixStack.model,
                         math.sin(glfw.glfwGetTime()),
                         0,
                         0)
            ms.rotateZ(ms.MatrixStack.model,glfw.glfwGetTime())

            gl.glUseProgram(self.shader)
            gl.glBindVertexArray(self.vao)


            gl.glUniformMatrix4fv(self.mvpMatrixLoc,
                                  1,
                                  gl.GL_TRUE,
                                  np.ascontiguousarray(
                                      ms.getCurrentMatrix(ms.MatrixStack.modelviewprojection),
                                      dtype=np.float32))
            gl.glDrawArrays(gl.GL_TRIANGLES,
                            0,
                            self.numberOfVertices)
            gl.glBindVertexArray(0)



# Initialize the library
if not glfw.glfwInit():
    sys.exit()

glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MAJOR,3)
glfw.glfwWindowHint(glfw.GLFW_CONTEXT_VERSION_MINOR,3)
glfw.glfwWindowHint(glfw.GLFW_OPENGL_PROFILE,glfw.GLFW_OPENGL_CORE_PROFILE)
#for osx
glfw.glfwWindowHint(glfw.GLFW_OPENGL_FORWARD_COMPAT, gl.GL_TRUE);


# Create a windowed mode window and its OpenGL context
window = glfw.glfwCreateWindow(640, 480, str.encode("Hello World"), None, None)
if not window:
    glfw.glfwTerminate()
    sys.exit()

# Make the window's context current
glfw.glfwMakeContextCurrent(window)

ctx = nk.glfw3_init(window, nk.GLFW3_INSTALL_CALLBACKS)

fontAtlas = nk.NKFontAtlas()
nk.glfw3_font_stash_begin(ctypes.byref(fontAtlas))
nk.glfw3_font_stash_end()

# Install a key handler
def on_key(window, key, scancode, action, mods):
    if key == glfw.GLFW_KEY_ESCAPE and action == glfw.GLFW_PRESS:
        glfw.glfwSetWindowShouldClose(window,1)
glfw.glfwSetKeyCallback(window, on_key)

gl.glClearColor(0.0,0.0,0.0,1.0)
gl.glEnable(gl.GL_DEPTH_TEST)
gl.glClearDepth(1.0)
gl.glDepthFunc(gl.GL_LEQUAL)



class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 10.0

        self.rotationX = 0.0
        self.rotationY = 0.0

camera = Camera()

triangle = Triangle()
triangle.prepareToRender()

# does python have static local variables?  this declaration is way too far away from use
#property = ctypes.c_int(20)


# Loop until the user closes the window
while not glfw.glfwWindowShouldClose(window):
    # Render here

    # Poll for and process events
    glfw.glfwPollEvents()
    nk.glfw3_new_frame()

    width, height = glfw.glfwGetFramebufferSize(window)
    gl.glViewport(0, 0, width, height)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    ms.setToIdentityMatrix(ms.MatrixStack.model)
    ms.setToIdentityMatrix(ms.MatrixStack.view)
    ms.setToIdentityMatrix(ms.MatrixStack.projection)

    # set the projection matrix to be perspective
    ms.perspective(fov= 45.0,
                   aspectRatio= width / height,
                   nearZ= 0.1,
                   farZ= 10000.0)

    # get input from keyboard for camera movement
    if not nk.item_is_any_active(ctx):
        # set up Camera
        if glfw.glfwGetKey(window, glfw.GLFW_KEY_RIGHT) == glfw.GLFW_PRESS:
            camera.rotationY -= 0.03

        if glfw.glfwGetKey(window, glfw.GLFW_KEY_LEFT) == glfw.GLFW_PRESS:
            camera.rotationY += 0.03

        if glfw.glfwGetKey(window, glfw.GLFW_KEY_UP) == glfw.GLFW_PRESS:
            camera.x -= math.sin(camera.rotationY)
            camera.z -= math.cos(camera.rotationY)

        if glfw.glfwGetKey(window, glfw.GLFW_KEY_DOWN) == glfw.GLFW_PRESS:
            camera.x += math.sin(camera.rotationY)
            camera.z += math.cos(camera.rotationY)

    # move the camera to the correct position, which means
    # updating the view stack
    ms.rotateX(ms.MatrixStack.view,
               camera.rotationX)
    ms.rotateY(ms.MatrixStack.view,
               -camera.rotationY)
    ms.translate(ms.MatrixStack.view,
                 -camera.x,
                 -camera.y,
                 -camera.z)

    # render the models

    triangle.render()

    MAX_VERTEX_BUFFER = 512 * 1024
    MAX_ELEMENT_BUFFER = 128 * 1024


    if(nk.begin(ctx,
                        b'Demonstration',
                        nk.NKRect(50.0,50.0,230.0,250.0),
                        nk.WINDOW_BORDER
                           |nk.WINDOW_MOVABLE
                           |nk.WINDOW_SCALABLE
                           |nk.WINDOW_MINIMIZABLE
                           |nk.WINDOW_TITLE)):

        nk.layout_row_static(ctx, ctypes.c_float(30.0), 80, 5)
        if nk.button_label(ctx, b'button'):
            print('button pressed')

        nk.layout_row_dynamic(ctx, ctypes.c_float(30.0), 2)

        # simulate a local static variable
        try:
            op
        except Exception:
            op = 0

        if nk.option_label(ctx, b'easy', op == 0): op = 0
        if nk.option_label(ctx, b'hard', op == 1): op = 1

        nk.layout_row_dynamic(ctx, ctypes.c_float(25.0), 1)

        # simulate a local static variable
        try:
            prop
        except Exception:
            prop = ctypes.c_int(20)


        nk.property_int(ctx, b'Compression:', 0, ctypes.byref(prop), 100, 10, 1);

        nk.layout_row_dynamic(ctx, ctypes.c_float(20.0), 1)
        nk.label(ctx, b'background:', nk.TEXT_LEFT)



        # simulate a local static variable
        try:
            background
        except Exception:
            background = nk.NKColor(0, 0, 0, 255)



        nk.layout_row_dynamic(ctx, ctypes.c_float(25.0), 1)

        if nk.combo_begin_color(ctx,
                                        background,
                                        nk.NKVec2(nk.widget_width(ctx),
                                                       400)):
            nk.layout_row_dynamic(ctx, ctypes.c_float(120.0), 1);
            background = nk.color_picker(ctx,
                                                 background,
                                                 nk.RGBA)

            nk.layout_row_dynamic(ctx, ctypes.c_float(25.0), 1);
            background.r = nk.propertyi(ctx, b'#R:', 0, background.r, 255, 1, ctypes.c_float(1))
            background.g = nk.propertyi(ctx, b'#G:', 0, background.g, 255, 1, ctypes.c_float(1))
            background.b = nk.propertyi(ctx, b'#B:', 0, background.b, 255, 1, ctypes.c_float(1))
            background.a = nk.propertyi(ctx, b'#A:', 0, background.a, 255, 1, ctypes.c_float(1))


            gl.glClearColor(background.r/255,background.g/255,background.b/255,background.a/255)

            nk.combo_end(ctx);

    nk.end(ctx)



    # show overview

    # simulate a local static variable
    try:
        show_menu
    except Exception:
        show_menu = True
    try:
        titlebar
    except Exception:
        titlebar  = True
    try:
        border
    except Exception:
        border = True
    try:
        resize
    except Exception:
        resize = True
    try:
        movable
    except Exception:
        movable = True
    try:
        no_scrollbar
    except Exception:
        no_scrollbar = False
    try:
        scale_left
    except Exception:
        scale_left = False
    try:
        window_flags
    except Exception:
        window_flags = 0
    try:
        minimizable
    except Exception:
        minimizable = True



    #TODO -- map the ctx struct

    #ctx->style.window.header.align = header_align;

    if(border) : window_flags |= nk.WINDOW_BORDER
    if(resize) : window_flags |= nk.WINDOW_SCALABLE
    if(movable) : window_flags |= nk.WINDOW_MOVABLE
    if(no_scrollbar) : window_flags |= nk.WINDOW_NO_SCROLLBAR
    if(scale_left) : window_flags |= nk.WINDOW_SCALE_LEFT
    if(minimizable) : window_flags |= nk.WINDOW_MINIMIZABLE


    if nk.begin(ctx, b'Overview', nk.NKRect(400,200,400,600),window_flags):
        pass
        if show_menu:
            try:
                mprog
            except Exception:
                mprog = 60
            try:
                mslider
            except Exception:
                mslider = 10
            try:
                mcheck
            except Exception:
                mcheck = True

            nk.menubar_begin(ctx)
            nk.layout_row_begin(ctx, nk.STATIC, ctypes.c_float(25.0),4)
            nk.layout_row_push(ctx, ctypes.c_float(45))


            if nk.menu_begin_label(ctx, b'MENU', nk.TEXT_LEFT, nk.NKVec2(120,120)):
                nk.layout_row_dynamic(ctx, ctypes.c_float(25.0), 1)
                if nk.menu_item_label(ctx, b'Hide', nk.TEXT_LEFT):
                    show_menu = False
                if nk.menu_item_label(ctx, b'About', nk.TEXT_LEFT):
                    show_app_about = True

                nk.menu_end(ctx)
            nk.menubar_end(ctx)

    nk.end(ctx)

    nk.glfw3_render(nk.ANTI_ALIASING_ON, MAX_VERTEX_BUFFER, MAX_ELEMENT_BUFFER)

    # done with frame, flush and swap buffers
    # Swap front and back buffers
    glfw.glfwSwapBuffers(window)


glfw.glfwTerminate()