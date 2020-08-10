import struct
from obj import ObjFile

def char(c):
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    return struct.pack('=h', w)

def dword(d):
    return struct.pack('=l', d)

def color(r, g, b):
    return bytes([round(b * 255), round(g * 255), round(r * 255)])

def crossProduct(a, b):
    c = [a[1] * b[2] - a[2] * b[1],
         a[2] * b[0] - a[0] * b[2],
         a[0] * b[1] - a[1] * b[0]
    ]

    return c

def dotProduct(a, b):
    total = 0

    for i in range(len(a)):
        total += a[i] * b[i]

    return total

def vSubstract(a, b):
    c = [a[0] - b[0],
         a[1] - b[1],
         a[2] - b[2],
    ]

    return c

def linalgNormal(a):
    norm = 0

    for x in a:
        norm += x **2

    norm = norm ** 0.5

    for x in range(len(a)):
        try:
            a[x] /= norm
        except ZeroDivisionError:
            pass
    
    return a

def multipleCompare(a, b):
    for i in range(len(a)):
        if a[i] < b[i]:
            return False

    return True

def baricentricCoordinates(vA, vB, vC, vP):
    # u corresponde a vA, v corresponde a vB, w corresponde a vC
    try:
        u = (
            ( (vP[0] - vC[0]) * (vB[1] - vC[1]) + (vP[1] - vC[1]) * (vC[0] - vB[0]) ) 
            /
            ( (vA[0] - vC[0]) * (vB[1] - vC[1]) + (vA[1] - vC[1]) * (vC[0] - vB[0]) ) 
            )

        v = ( 
            ( (vP[0] - vC[0]) * (vC[1] - vA[1]) + (vP[1] - vC[1]) * (vA[0] - vC[0]) ) 
            /
            ( (vA[0] - vC[0]) * (vB[1] - vC[1]) + (vA[1] - vC[1]) * (vC[0] - vB[0]) ) 
            )

        w = 1 - u - v
    except:
        return -1, -1, -1

    return u, v, w

BLACK = color(0, 0, 0)
WHITE = color(1, 1, 1)

class Render(object):
    def __init__(self, w, h):
        self.glInit(w, h)
    
    # no tiene parámetros
    # esta función se ejecuta al crear un objeto de tipo render
    # inicializa las variables necesarias en su valor default
    def glInit(self, width, height):
        self.height = 0
        self.width = 0
        self.vp_height = 0
        self.vp_width = 0
        self.vp_start_point_x = 0
        self.vp_start_point_y = 0
        self.clear_color = BLACK
        self.point_color = WHITE
        self.texture = None
        self.light = [0, 0, 1]
        self.active_shader = None
        self.glCreateWindow(width, height)

    # (width, height)
    # se inicializa el framebuffer con la altura y ancho indicados
    def glCreateWindow(self, width, height):
        self.height = round(height)
        self.width = round(width)
        self.glClear()
        self.glViewPort(0, 0, width, height)
        
        return True

    # no tiene parametros
    # se llena el mapa de bits con el color seleccionado
    def glClear(self):
        self.pixels = [[self.clear_color for x in range(self.width)] for y in range(self.height)]

        #Z - buffer, depthbuffer, buffer de profudidad
        self.zbuffer = [ [ -10000 for x in range(self.width)] for y in range(self.height) ]

    # (r, g, b) - valores entre 0 y 1
    # define el color con el que se realiza el clear
    def glClearColor(self, r, g, b):
        if r > 1 or r < 0 or g > 1 or g < 0 or b > 1 or b < 0:
            return False
        
        self.clear_color = color(r, g, b)
        return True
    
    # (r, g, b) - valores entre 0 y 1
    # define el color con el que se dibuja el punto
    def glColor(self, r, g, b):
        if r > 1 or r < 0 or g > 1 or g < 0 or b > 1 or b < 0:
            return False

        self.point_color = color(r, g, b)
        return True

    # (x, y, width, height)
    # crea el viewport en donde se podrá dibujar
    # restringe al viewport dentro de la ventana
    def glViewPort(self, x, y, width, height):
        if x > self.width or y > self.height:
            return False
        elif x + width > self.width or y + height > self.height:
            return False
        else:
            self.vp_start_point_x = x
            self.vp_start_point_y = y
            self.vp_width = width
            self.vp_height = height
            return True

    # no tiene parámetros
    # función extra
    # dibuja el contorno del viewport 
    def glDrawViewPort(self):
        for x in range(self.vp_start_point_x, self.vp_start_point_x + self.vp_width):
            self.pixels[self.vp_start_point_y][x] = color(255, 0, 251)
            self.pixels[self.vp_start_point_y + self.vp_height][x] = color(255, 0, 251)
        
        for y in range(self.vp_start_point_y, self.vp_start_point_y + self.vp_height):
            self.pixels[y][self.vp_start_point_x] = color(255, 0, 251)
            self.pixels[y][self.vp_start_point_x + self.vp_width] = color(255, 0, 251)

    # (x, y) - valores entre -1 y 1
    # se crea un punto dentro del viewport
    # las coordenadas son relativas al viewport
    def glVertex(self, x, y):
        if x > 1 or x < -1 or y > 1 or y < -1:
            return False
        else:
            new_x = (x + 1) * (self.vp_width / 2) + self.vp_start_point_x
            new_y = (y + 1) * (self.vp_height / 2) + self.vp_start_point_y
            self.pixels[round(new_y - 1) if round(new_y) == self.vp_height else round(new_y)][round(new_x - 1) if round(new_x) == self.vp_width else round(new_x)] = self.point_color

            return True

    # (x, y) - coordenadas
    # recibe las coordenadas en pixeles para dibujar 
    def glVertexNDC(self, x, y, color = None):
        self.pixels[(y - 1) if y == self.vp_height else y][(x - 1) if x == self.vp_width else x] = color or self.point_color
    
    # (x0, y0, x1, y1) - el punto inicial y final de una recta
    # la función es una implementación del algoritmo de bresenham
    # permite dibujar una linea de un punto inicial a uno final (en coordenadas relativas al vp entre -1 y 1)
    def glLine(self, x0, y0, x1, y1):
        new_x0 = round((x0 + 1) * (self.vp_width / 2) + self.vp_start_point_x)
        new_y0 = round((y0 + 1) * (self.vp_height / 2) + self.vp_start_point_y)
        new_x1 = round((x1 + 1) * (self.vp_width / 2) + self.vp_start_point_x)
        new_y1 = round((y1 + 1) * (self.vp_height / 2) + self.vp_start_point_y)

        ystep = False

        if abs(new_x1 - new_x0) < abs(new_y1 - new_y0):
            ystep = True
            new_x0, new_x1, new_y0, new_y1 = new_y0, new_y1, new_x0, new_x1

        if (new_x0 > new_x1):
            new_x0, new_x1, new_y0, new_y1 = new_x1, new_x0, new_y1, new_y0

        dx = new_x1 - new_x0
        dy = new_y1 - new_y0

        xsign = 1
        ysign = 1

        if dy < 0:
            ysign = -1
            dy = -dy

        D = 2 * dy - dx
        Y = new_y0

        for x in range(new_x0, new_x1):
            if ystep:
                self.glVertexNDC(Y, x)
            else:
                self.glVertexNDC(x, Y)

            if D > 0:
                Y = Y + ysign
                D = D - 2 * dx
            
            D = D + 2 * dy

    # (x0, y0, x1, y1) - el punto inicial y final de una recta
    # la función es una implementación del algoritmo de bresenham
    # permite dibujar una linea de un punto inicial a uno final (en coordenadas de la ventana)
    def glLineNDC(self, x0, y0, x1, y1):
        ystep = False

        if abs(x1 - x0) < abs(y1 - y0):
            ystep = True
            x0, x1, y0, y1 = y0, y1, x0, x1

        if (x0 > x1):
            x0, x1, y0, y1 = x1, x0, y1, y0

        dx = x1 - x0
        dy = y1 - y0

        xsign = 1
        ysign = 1

        if dy < 0:
            ysign = -1
            dy = -dy

        D = 2 * dy - dx
        Y = y0

        for x in range(x0, x1):
            if ystep:
                self.glVertexNDC(Y, x)
            else:
                self.glVertexNDC(x, Y)

            if D > 0:
                Y = Y + ysign
                D = D - 2 * dx
            
            D = D + 2 * dy

    # (nombre del archivo, traslacion, escala)
    # se lee un archivo de tipo obj
    # con la informacion de los vertices y caras, se renderiza el objeto en modo de wireframe
    def glObj(self, obj__file, translate, scale):
        model = ObjFile(obj__file)

        for face in model.faces:

            vertCount = len(face)

            for vert in range(vertCount):
                v0 = model.vertexes[ face[vert][0] - 1]
                v1 = model.vertexes[ face[(vert + 1) % vertCount][0] - 1]

                x0 = round(v0[0] * scale[0] + translate[0])
                y0 = round(v0[1] * scale[1] + translate[1])
                x1 = round(v1[0] * scale[0] + translate[0])
                y1 = round(v1[1] * scale[1] + translate[1])

                self.glLineNDC(x0, y0, x1, y1)

    # función para dibujar un poligono
    # se dinujan lineas entre los vertices del poligono
    def glDrawPolygon(self, vertexes):
        min__x = self.width
        min__y = self.height
        max__x = 0
        max__y = 0

        for x in range(len(vertexes)):
            v0 = vertexes[x]
            v1 = vertexes[(x + 1) % len(vertexes)]

            max__x = v0[0] if v0[0] > max__x else max__x
            min__x = v0[0] if v0[0] < min__x else min__x
            max__y = v0[1] if v0[1] > max__y else max__y
            min__y = v0[1] if v0[1] < min__y else min__y
            
            self.glLineNDC((v0[0]), (v0[1]), (v1[0]), (v1[1]))
        
        self.glFillPolygon(max__x, max__y, min__x, min__y)
        # self.fillPolygon(max__x, max__y, min__x, min__y, vertexes)
    
    # (x, y) - pixel a revisar
    # función auxiliar para glFillPolygon
    # revisa de forma recursiva 
    def check(self, x, y):
        return self.pixels[y][x] != self.point_color

    # (mx, my, Mx, My) - la altura y ancho maximo y minimo
    # función para rellenar un poligono
    # se dibujan lineas para rellenar
    def glFillPolygon(self, Mx, My, mx, my):
        for x in range(mx, Mx):
            COLOR = 0
            for y in range(my - 1, My - 1):
                CHECK = True
                if self.pixels[y][x] == self.point_color:
                    if self.check(x, y + 1):
                        yy = y + 1
                        while CHECK and yy < self.height - 1:
                            yy += 1
                            CHECK = self.check(x, yy)

                        if yy != self.height - 1:
                            if COLOR % 2 == 0:
                                self.glLineNDC(x, y, x, yy)
                            COLOR += 1
 
    # función para aplicar transformaciones a un vector
    # aplica la escala y traslación de los pixeles
    def transform(self, vertex, translate = [0, 0, 0], scale = [1, 1, 1]):
        return [round(vertex[0] * scale[0] + translate[0]),
                round(vertex[1] * scale[1] + translate[1]),
                round(vertex[2] * scale[2] + translate[2])]
    
    # función para cargar el archivo obj 
    # se dibujan y rellenan la figura utilizando coordenadas baricéntricas
    # con las coordenadas baricéntricas se simula un foco de luz de frente al objeto y en el medio
    def glLoadObj(self, filename, translate = [0, 0, 0], scale = [1, 1, 1]):
        model = ObjFile(filename)

        for face in model.faces:
            vertexes = len(face)

            v0 = model.vertexes[face[0][0] - 1]
            v1 = model.vertexes[face[1][0] - 1]
            v2 = model.vertexes[face[2][0] - 1]
            if vertexes > 3:
                v3 = model.vertexes[face[3][0] - 1]

            v0 = self.transform(v0, translate, scale)
            v1 = self.transform(v1, translate, scale)
            v2 = self.transform(v2, translate, scale)

            if vertexes > 3:
                v3 = self.transform(v3, translate, scale)

            if self.texture:
                t0 = model.textures[face[0][1] - 1]
                t1 = model.textures[face[1][1] - 1]
                t2 = model.textures[face[2][1] - 1]

                if len(face) > 3:
                    v3 = model.textures[face[3][0] - 1]
            
            else:
                t0 = [0, 0]
                t1 = [0, 0]
                t2 = [0, 0]
                t3 = [0, 0]

            normal = crossProduct(vSubstract(v1, v0), vSubstract(v2, v0))
            normal = linalgNormal(normal)
            intensity = dotProduct(normal, self.light)

            # si la luz le da al pixel, entonces se dibuja
            if intensity >= 0:
                c = color(intensity, intensity, intensity)
                
                self.glBaricentricTriangle(v0, v1, v2, textureCs = [t0, t1, t2], _color_ = c)

                if vertexes > 3:
                    self.glBaricentricTriangle(v0, v2, v3, textureCs = [t0, t2, t3], _color_ = c)


    # dibujado y rellenado de un triángulo usando coordenadas baricentricas
    def glBaricentricTriangle(self, vA, vB, vC, textureCs, _color_ = WHITE):
        # valores mínimos y máximos para x,y sirviendo como contención de la imagen
        minX = min(vA[0], vB[0], vC[0])
        minY = min(vA[1], vB[1], vC[1])
        maxX = max(vA[0], vB[0], vC[0])
        maxY = max(vA[1], vB[1], vC[1])

        for x in range(minX, maxX + 1):
            for y in range(minY, maxY + 1):
                if x >= self.width or x < 0 or y >= self.height or y < 0:
                    continue

                u, v, w = baricentricCoordinates(vA, vB, vC, [x, y])

                if multipleCompare([u, v, w], [0, 0, 0]):

                    # fórmula para calcular el valor de z utilizando el área de u, v, w
                    z = vA[2] * u + vB[2] * v + vC[2] * w

                    # si z se puede dibujar 
                    if z > self.zbuffer[y][x]:
                        b, g, r = _color_

                        b /= 255
                        g /= 255
                        r /= 255

                        if self.texture:
                            ta, tb, tc = textureCs
                            tx = ta[0] * u + tb[0] * v + tc[0] * w
                            ty = ta[1] * u + tb[1] * v + tc[1] * w

                            texColor = self.texture.getColor(tx, ty)
                            b *= texColor[0] / 255
                            g *= texColor[1] / 255
                            r *= texColor[2] / 255

                        self.glVertexNDC(x, y, color(r, g, b))
                        self.zbuffer[y][x] = z

    # función para la textura del objeto a renderizar setter 
    def glSetTexture(self, t):
        self.texture = t

    # no tiene parámetros
    # renderiza el mapa de bits
    def glFinish(self):
        file = open('sr5.bmp', 'wb')

        # file header
        file.write(bytes('B'.encode('ascii')))
        file.write(bytes('M'.encode('ascii')))
                   
        file.write(dword(14 + 40 + self.width * self.height * 3))
        file.write(dword(0))
        file.write(dword(14 + 40))

        # image header
        file.write(dword(40))
        file.write(dword(self.width))
        file.write(dword(self.height))
        file.write(word(1))
        file.write(word(24))
        file.write(dword(0))
        file.write(dword(self.width * self.height * 3))
        file.write(dword(0))
        file.write(dword(0))
        file.write(dword(0))
        file.write(dword(0))

        # pixels, 3 bytes each
        for x in range(self.height):
            for y in range(self.width):
                file.write(self.pixels[x][y])

        file.close()

    # función para exportar los valores del zbuffer en un archivo bmp
    def glZBuffer(self):
        file = open('zbuffer.bmp', 'wb')

        # File header 14 bytes
        file.write(bytes('B'.encode('ascii')))
        file.write(bytes('M'.encode('ascii')))
        file.write(dword(14 + 40 + self.width * self.height * 3))
        file.write(dword(0))
        file.write(dword(14 + 40))

        # Image Header 40 bytes
        file.write(dword(40))
        file.write(dword(self.width))
        file.write(dword(self.height))
        file.write(word(1))
        file.write(word(24))
        file.write(dword(0))
        file.write(dword(self.width * self.height * 3))
        file.write(dword(0))
        file.write(dword(0))
        file.write(dword(0))
        file.write(dword(0))

        # max y min valores para z
        minZ = 10000
        maxZ = -10000

        for x in range(self.height):
            for y in range(self.width):
                if self.zbuffer[x][y] == -10000:
                    pass
                else:
                    if minZ > self.zbuffer[x][y]:
                        minZ = self.zbuffer[x][y]
                    if maxZ < self.zbuffer[x][y]:
                        maxZ = self.zbuffer[x][y]

        for x in range(self.height):
            for y in range(self.width):
                depth = self.zbuffer[x][y]
                if depth == -10000:
                    depth = minZ
                depth = (depth - minZ) / (maxZ - minZ)
                file.write(color(depth, depth, depth))

        file.close()