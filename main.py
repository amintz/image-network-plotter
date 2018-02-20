import svgwrite as svg
import xml.etree.ElementTree as et
import os, configparser, sys, platform, traceback
from PIL import Image

def main():
    try:
        def yn (answer):
            if answer.lower() == "yes":
                return True
            elif answer.lower() == "no":
                return False
            else:
                sys.exit('\n**ERROR**\nCheck config file. Some settings only take yes or no\n')

        # ------------------------------------------
        # Platform check
        #-------------------------------------------

        sys.tracebacklimit = 0

        if platform.system() == 'Windows':
            iswindows = True
            slash = '\\'
        else:
            iswindows = False
            slash = '/'

        # ------------------------------------------
        # Read the config file
        #-------------------------------------------

        settings = configparser.ConfigParser()

        try:
            settings.read('config.ini')
        except Exception:
            sys.exit('\n**ERROR**\nCould not open configuration file. It should be in the same folder as the script and named \'config.ini\'\n')

        print("\n-------------------------\nImage Network Plotter\n-------------------------")

        try:
            dir_path        = os.path.dirname(os.path.realpath(__file__))
            absolutepath    = yn(settings['Input']['AbsolutePath'])

            if absolutepath:
                projectfolder   = settings['Input']['ProjectFolder'] + slash
            else:
                projectfolder   = dir_path + slash + settings['Input']['ProjectFolder'] + slash

            inputimgfolder  = projectfolder + settings['Folders']['InputImgFolder'] + slash
            thumbnailimgfolder    = projectfolder + settings['Folders']['ResizedImgFolder'] + slash

            inputfilename = projectfolder + settings['Input']['InputFile']
            outputfilename = projectfolder + "visual_" + settings['Input']['InputFile'].split(".")[0] + ".svg"

            imgresizewidth = int(settings['Output']['ResizeMaxWidth'])
            imgresizeheight = int(settings['Output']['ResizeMaxHeight'])

            imgdrawwidth = int(settings['Output']['ImageMaxDispWidth'])
            imgdrawheight= int(settings['Output']['ImageMaxDispHeight'])

            outsvgw = int(settings['Output']['OutputWidth'])
            outsvgh = int(settings['Output']['OutputHeight'])

            restrictPage = yn(settings['Output']['RestricttoPage'])
            resizeImage = yn(settings['Output']['CopyImagesResized'])
        except Exception:
            sys.exit("\n**ERROR**\nCould not parse at least one of the settings from the config file. Please verify its contents carefully.")

        # ------------------------------------------
        # Set internal variables
        #-------------------------------------------

        imgresizedim = imgresizewidth, imgresizeheight
        imgdrawdim = imgdrawwidth, imgdrawheight

        print(inputfilename)
        ingexf = et.parse(inputfilename)

        if resizeImage and not os.path.exists(thumbnailimgfolder):
                os.makedirs(thumbnailimgfolder)

        # ------------------------------------------
        # Parse GEXF and generate SVG
        #-------------------------------------------

        inroot = ingexf.getroot()
        ns = {'gexf' : "http://www.gexf.net/1.3" }
        viz = {'viz' : "http://www.gexf.net/1.3/viz"}

        typeAttId = -1
        linkAttId = -1
        fileAttId = -1

        graph = inroot.find("gexf:graph", ns)

        attributes = graph.find(".gexf:attributes",ns)

        for att in attributes:
            if att.get('title') == 'type':
                typeAttId = att.get('id')
            elif att.get('title') == 'link':
                linkAttId = att.get('id')
            elif att.get('title') == 'file':
                fileAttId = att.get('id')

        # print("\n\tType attribute ID: \t" + str(typeAttId))
        # print("\tLink attribute ID: \t" + str(linkAttId))
        # print("\tFile attribute ID: \t" + str(fileAttId))
        # print("\tDescription attribute ID: \t" + str(descAttId))

        nodes = graph.find("gexf:nodes", ns)

        # Find graph bounding box and count images
        numnodes = 0
        numimages = 0

        minx = 0
        maxx = 0
        miny = 0
        maxy = 0

        for node in nodes:
            numnodes += 1
            typeAtt = node.find("gexf:attvalues/gexf:attvalue[@for=\'" + str(typeAttId) +"\']",ns)
            if typeAtt.get('value') == "image":
                numimages += 1
                inimgx = float(node.find("viz:position", viz).get('x'))
                inimgy = float(node.find("viz:position", viz).get('y'))
                if inimgx < minx:
                    minx = inimgx
                if inimgx > maxx:
                    maxx = inimgx
                if inimgy < miny:
                    miny = inimgy
                if inimgy > maxy:
                    maxy = inimgy

        print("Graph contains " + str(numnodes) + " nodes.")
        print("Plotting " + str(numimages) + " images.\n")
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

        for node in nodes:
            typeAtt = node.find("gexf:attvalues/gexf:attvalue[@for=\'" + str(typeAttId) +"\']",ns)
            if typeAtt.get('value') == "image":
                print("\n\nDrawing image " + str(curimg) + " in " + str(numimages))
                curimg += 1

                innodex = (float(node.find("viz:position", viz).get('x'))-minx)/inw
                innodey = (float(node.find("viz:position", viz).get('y'))-miny)/inh

                if restrictPage:
                    outnodex = (innodex * outw) + outx
                    outnodey = (innodey * outh) + outy
                else:
                    outnodex = innodex
                    outnodey = innodey

                nodeid = node.get('id')
                imgfile = node.find("gexf:attvalues/gexf:attvalue[@for=\'" + str(fileAttId) +"\']",ns).get('value')
                linkUrl = node.find("gexf:attvalues/gexf:attvalue[@for=\'" + str(linkAttId) +"\']",ns).get('value')

                infile = inputimgfolder + imgfile

                try:
                    curimage = Image.open(infile)
                except Exception:
                    print("\t**ATTENTION** Image could not be loaded.\n")
                    continue

                if resizeImage:
                    outfile = thumbnailimgfolder + imgfile
                    print("\tResizing image...")
                    curimage.thumbnail(imgresizedim, Image.ANTIALIAS)
                    curimage.save(outfile)
                else:
                    outfile = infile

                print("\tPlotting image...\n")

                link = outsvg.add(outsvg.a(linkUrl))
                image = link.add(outsvg.image(outfile, id=nodeid, insert=(outnodex, outnodey), size=imgdrawdim))

        outsvg.save(pretty=True)
    except KeyboardInterrupt:
        if outsvg:
            outsvg.save(pretty=True)
        print("\n\n**Script interrupted by user**\n\n")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(0)

if __name__ == "__main__":
    main()
