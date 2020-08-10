from gl import Render, color
from obj import ObjFile, Texture

r = Render(800, 800)

texture = Texture('model.bmp')
r.glSetTexture(texture)
r.glLoadObj('model.obj', (400, 400, 0), (300, 300, 300))

r.glFinish()
