import svgwrite as svg
import xml.etree.ElementTree as et
import os, configparser, sys, platform
from PIL import Image

def yn (answer):
    if answer.lower() == "yes":
        return True
    elif answer.lower() == "no":
        return False
    else:
        sys.exit('\n**ERROR**\nCheck config file. Some settings only take yes or no\n')

sys.tracebacklimit = 0

if platform.system() == 'Windows':
    iswindows = True
    slash = '\\'
else:
    iswindows = False
    slash = '/'

# Config parser

settings = configparser.ConfigParser()

try:
    settings.read('config.ini')
except Exception:
    sys.exit('\n**ERROR**\nCould not open configuration file. It should be in the same folder as the script and named \'config.ini\'\n')

print("\n-------------------------\nImage Network Plotter\n-------------------------")

absoluteinputpath = yn(settings['Folders']['AbsoluteInputImgPath'])

projectfolder   = "data" + slash + settings['Project']['ProjectName'] + slash

if absoluteinputpath:
    inputimgfolder  =  settings['Folders']['InputImgFolder'] + slash
else:
    inputimgfolder  = projectfolder + settings['Folders']['InputImgFolder'] + slash

thumbnailimgfolder    = projectfolder + settings['Folders']['ResizedImgFolder'] + slash


inputfilename = projectfolder + settings['Input']['InputFile']
justImages = yn(settings['Input']['JustImages'])
valuesep = settings['Input']['ValueSeparator']

outputfilename = projectfolder + "visual_" + settings['Input']['InputFile']

imgresizewidth = int(settings['Output']['ResizeMaxWidth'])
imgresizeheight = int(settings['Output']['ResizeMaxHeight'])

imgdrawwidth = int(settings['Output']['ImageMaxDispWidth'])
imgdrawheight= int(settings['Output']['ImageMaxDispHeight'])

outsvgw = int(settings['Output']['OutputWidth'])
outsvgh = int(settings['Output']['OutputHeight'])

restrictPage = yn(settings['Output']['RestricttoPage'])
resizeImage = yn(settings['Output']['CopyImagesResized'])


# Set internal variables

imgresizedim = imgresizewidth, imgresizeheight
imgdrawdim = imgdrawwidth, imgdrawheight

insvg = et.parse(inputfilename)

if not os.path.exists(thumbnailimgfolder):
        os.makedirs(thumbnailimgfolder)

# ---------

# Start parsing the SVG

inroot = insvg.getroot()
ns = {'svg' : "http://www.w3.org/2000/svg" }
inimages = inroot.find("svg:g", ns)

# Find graph bounding box and count images
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
# Configure output conversion

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

# --------
# Draw output

outsvg = svg.Drawing(outputfilename, (outsvgw,outsvgh), debug=True)
curimg = 1

for node in inimages:
    print("\n\nDrawing node " + str(curimg) + " in " + str(numimages))
    curimg += 1

    innodex = (float(node.get('x'))-minx)/inw
    innodey = (float(node.get('y'))-miny)/inh

    if restrictPage:
        outnodex = (innodex * outw) + outx
        outnodey = (innodey * outh) + outy
    else:
        outnodex = innodex
        outnodey = innodey

    if justImages:
        infile = inputimgfolder + node.text.strip()
        print("\tLoading image: " + infile)
        try:
            curimage = Image.open(infile)
        except Exception:
            print("\tImage could not be loaded.\n")
            continue

        if resizeImage:
            outfile = thumbnailimgfolder + node.text.strip()
            print("\tResizing image...")
            curimage.thumbnail(imgresizedim, Image.ANTIALIAS)
            curimage.save(outfile)
        else:
            outfile = infile

        print("\tPlotting image...\n")

        link = outsvg.add(outsvg.a(settings['Folders']['InputImgFolder'] + slash + node.text.strip()))
        image = link.add(outsvg.image(settings['Folders']['ResizedImgFolder'] + slash + node.text.strip(), insert=(outnodex, outnodey), size=imgdrawdim))

    else:
        textcomponents = node.text.strip().split(',')
        nodetype = textcomponents[0]

        if nodetype == 'image':
            infile = inputimgfolder + textcomponents[1]
            try:
                curimage = Image.open(infile)
            except Exception:
                print("\tImage could not be loaded.\n")
                continue

            if resizeImage:
                outfile = thumbnailimgfolder + textcomponents[1]
                print("\tResizing image...")
                curimage.thumbnail(imgresizedim, Image.ANTIALIAS)
                curimage.save(outfile)
            else:
                outfile = infile

            print("\tPlotting image...\n")

            link = outsvg.add(outsvg.a(textcomponents[2]))
            image = link.add(outsvg.image(outfile, insert=(outnodex, outnodey), size=(200,200)))

        # elif nodetype == 'gv_label':
        #     label = textcomponents[2]
        #     print("\tPlotting node...\n")
        #     text = outsvg.add(outsvg.text(label, insert=(outnodex, outnodey),style=("font-size:40px; font-weight:bold")))

outsvg.save(pretty=True)
