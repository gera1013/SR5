import re
import struct

# función para convertir valores r, g, b en color
def color(r, g, b):
    return bytes([int(b * 255), int(g * 255), int(r * 255)])

# Clase para un archivo de tipo .obj
# Abre el archivo, lo lee, y luego separa los atributos en:
# Vertices, Normals, Textures y Faces
class ObjFile(object):
    
    # Inicializa el objeto
    # Se dividen las lineas del archivo y se guardan en una lista
    def __init__(self, filename):
        self.lines = []
        self.vertexes = []
        self.normals = []
        self.textures = []
        self.faces = []

        obj__file = open(filename, 'r')

        for line in obj__file.readlines():
            self.lines.append(line.split(maxsplit = 1))

        self.objRead()

    # Lee las lineas del archivo 
    # Separa cada atributo según sea V, VN, T, F
    def objRead(self):
        for line in self.lines:
            if len(line) > 1:
                prefix, values = line[0], line[1]

                if prefix == 'v':
                    self.vertexes.append(list(map(float, re.split(' ', values))))
                elif prefix == 'vn':
                    self.normals.append(list(map(float, re.split(' ', values))))
                elif prefix == 'vt':
                    self.textures.append(list(map(float, re.split(' ', values))))
                elif prefix == 'f':
                    face = []
                    for vert in re.split(' ', values):
                        face.append(list(map(int, re.split('/', vert))))
                    
                    self.faces.append(face)

class Texture(object):
    def __init__(self, path):
        self.path = path
        self.openTexture()

    def openTexture(self):
        texture = open(self.path, 'rb')
        texture.seek(10)
        headerSize = struct.unpack('=l', texture.read(4))[0]

        texture.seek(14 + 4)
        self.width = struct.unpack('=l', texture.read(4))[0]
        self.height = struct.unpack('=l', texture.read(4))[0]
        texture.seek(headerSize)

        self.pixels = []

        for y in range(self.height):
            self.pixels.append([])
            for x in range(self.width):
                b = ord(texture.read(1)) / 255
                g = ord(texture.read(1)) / 255
                r = ord(texture.read(1)) / 255
                self.pixels[y].append(color(r, g, b))
        
        texture.close()
    
    def getColor(self, tx, ty):
        if tx >= 0 and tx <= 1 and ty >= 0 and ty <= 1:
            x = int(tx * self.width)
            y = int(ty * self.height)

            return self.pixels[y][x]
        else:
            return color(0, 0, 0)