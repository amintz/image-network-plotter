import svgwrite as svg
import xml.etree.ElementTree as et
import os
from PIL import Image

projectname = "test"
imgpath = "img/"
datapath = "data/"
outputspath = "outputs/" + projectname + "/"
outputsimgpath = outputspath + "img/"

restrictPage = True
resizeImage = False

insvg = et.parse(datapath + "wcdraw_images-label_tagcloud.svg")

if not os.path.exists(outputspath):
        os.makedirs(outputspath)
if not os.path.exists(outputsimgpath):
        os.makedirs(outputsimgpath)

imgmaxdim = 100, 100

outsvgw = 15000
outsvgh = 15000

# ---------

inroot = insvg.getroot()
ns = {'svg' : "http://www.w3.org/2000/svg" }
inimages = inroot.find("svg:g", ns)
numimages = 0

minx = 0
maxx = 0
miny = 0
maxy = 0

for image in inimages:

    numimages += 1

    inimgx = float(image.get('x'))
    inimgy = float(image.get('y'))

    if inimgx < minx:
        minx = inimgx
    if inimgx > maxx:
        maxx = inimgx
    if inimgy < miny:
        miny = inimgy
    if inimgy > maxy:
        maxy = inimgy

print("Plotting " + str(numimages) + " images.")
print("Minimum X: " + str(minx))
print("Maximum X: " + str(maxx))
print("Minimum Y: " + str(miny))
print("Maximum Y: " + str(maxy))

# --------

inw = maxx - minx
inh = maxy - miny

if (inw/inh) >= (outsvgw/outsvgh):
    # match width
    outfactor = outsvgw / inw
else:
    # match height
    outfactor = outsvgh / inh

outw = inw * outfactor
outh = inh * outfactor
outx = (outsvgw - outw)/2
outy = (outsvgh - outh)/2

outsvg = svg.Drawing(outputspath + "test.svg", (outsvgw,outsvgh), debug=True)

for image in inimages:
    filename = image.text.strip()
    infile = imgpath + filename

    try:
        curimage = Image.open(infile)
    except Exception:
        print("Image could not be loaded.\n")
        continue

    outfile = outputsimgpath + filename
    if resizeImage:
        print("Resizing image...")
        curimage.thumbnail(imgmaxdim, Image.ANTIALIAS)
        curimage.save(outfile)

    print("Plotting image...\n")

    if restrictPage:
        inimgx = (float(image.get('x'))-minx)/inw
        inimgy = (float(image.get('y'))-miny)/inh
        outimgx = (inimgx * outw) + outx
        outimgy = (inimgy * outh) + outy
    else:
        outimgx = inimgx
        outimgy = inimgy
    link = outsvg.add(outsvg.a(infile))
    image = link.add(outsvg.image(outfile, insert=(outimgx, outimgy)))

outsvg.save(pretty=True)

#
# dwg = svg.Drawing("test.svg", (400,400), debug=True)
# link = dwg.add(dwg.a("http://ufmg.br"))
# image = link.add(dwg.image("https://ufmg.br/thumbor/alr9PWRv0IW7Dc4022rBn7nuF8I=/480x341/smart/https://ufmg.br/storage/5/4/8/5/5485babb8c510fd85b5099cf23f5938b_15162661728518_740131612.jpg", (100,100)))
# dwg.save(pretty=True)
