'''
# ----------------------------------------------------------------------------
# Copyright (C) 2014 305engineering <305engineering@gmail.com>
# Original concept by 305engineering.
#
# "THE MODIFIED BEER-WARE LICENSE" (Revision: my own :P):
# <305engineering@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff (except sell). If we meet some day,
# and you think this stuff is worth it, you can buy me a beer in return.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------
'''


import sys
import os
import re

sys.path.append('/usr/share/inkscape/extensions')
sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions')

import subprocess
import math

import inkex
import png
import array


class GcodeExport(inkex.Effect):

########     Richiamata da _main()
    def __init__(self):
        """init the effetc library and get options from gui"""
        inkex.Effect.__init__(self)

        # Opzioni di esportazione dell'immagine
        self.OptionParser.add_option("-d", "--directory",action="store", type="string", dest="directory", default="/home/",help="Directory for files") ####check_dir
        self.OptionParser.add_option("-f", "--filename", action="store", type="string", dest="filename", default="-1.0", help="File name")
        self.OptionParser.add_option("","--add-numeric-suffix-to-filename", action="store", type="inkbool", dest="add_numeric_suffix_to_filename", default=True,help="Add numeric suffix to filename")
        self.OptionParser.add_option("","--bg_color",action="store",type="string",dest="bg_color",default="",help="")
        self.OptionParser.add_option("","--resolution",action="store", type="int", dest="resolution", default="5",help="") #Usare il valore su float(xy)/resolution e un case per i DPI dell export


        # Modalita di conversione in Bianco e Nero
        self.OptionParser.add_option("","--conversion_type",action="store", type="int", dest="conversion_type", default="1",help="")

        # Opzioni modalita
        self.OptionParser.add_option("","--BW_threshold",action="store", type="int", dest="BW_threshold", default="128",help="")
        self.OptionParser.add_option("","--grayscale_resolution",action="store", type="int", dest="grayscale_resolution", default="1",help="")
        self.OptionParser.add_option("","--custom_cmd",action="store", type="string", dest="custom_cmd", default="", help="")
        self.OptionParser.add_option("","--power_min",action="store", type="int", dest="power_min", default="0",help="")
        self.OptionParser.add_option("","--power_max",action="store", type="int", dest="power_max", default="255",help="")

        #Velocita Nero e spostamento
        self.OptionParser.add_option("","--speed_ON",action="store", type="int", dest="speed_ON", default="200",help="")

        # Mirror Y
        self.OptionParser.add_option("","--flip_y",action="store", type="inkbool", dest="flip_y", default=False,help="")

        # Homing
        self.OptionParser.add_option("","--homing",action="store", type="int", dest="homing", default="1",help="")

        # Commands
        self.OptionParser.add_option("","--laseron", action="store", type="string", dest="laseron", default="M03", help="")
        self.OptionParser.add_option("","--laseroff", action="store", type="string", dest="laseroff", default="M05", help="")


        # Anteprima = Solo immagine BN
        self.OptionParser.add_option("","--preview_only",action="store", type="inkbool", dest="preview_only", default=False,help="")

        #inkex.errormsg("BLA BLA BLA Messaggio da visualizzare") #DEBUG




########    Richiamata da __init__()
########    Qui si svolge tutto
    def effect(self):


        current_file = self.args[-1]
        bg_color = self.options.bg_color


        ##Implementare check_dir

        if (os.path.isdir(self.options.directory)) == True:

            ##CODICE SE ESISTE LA DIRECTORY
            #inkex.errormsg("OK") #DEBUG


            #Aggiungo un suffisso al nomefile per non sovrascrivere dei file
            if self.options.add_numeric_suffix_to_filename :
                dir_list = os.listdir(self.options.directory) #List di tutti i file nella directory di lavoro
                temp_name =  self.options.filename
                max_n = 0
                for s in dir_list :
                    r = re.match(r"^%s_0*(\d+)%s$"%(re.escape(temp_name),'.png' ), s)
                    if r :
                        max_n = max(max_n,int(r.group(1)))
                self.options.filename = temp_name + "_" + ( "0"*(4-len(str(max_n+1))) + str(max_n+1) )


            #genero i percorsi file da usare

            suffix = ""
            if self.options.conversion_type == 1:
                suffix = "_Thresh_%d_" % (self.options.BW_threshold)
            elif self.options.conversion_type == 2:
                suffix = "_Riemer_"
            elif self.options.conversion_type == 3:
                suffix = "_Floyd_"
            elif self.options.conversion_type == 4:
                suffix = "_Ord_"
            elif self.options.conversion_type == 5:
                suffix = "_Remap_"
            elif self.options.conversion_type == 6:
                suffix = "_Gray_"
            elif self.options.conversion_type == 7:
                suffix = "_GrayR_%d_" % (self.options.grayscale_resolution)
            elif self.options.conversion_type == 8:
                suffix = "_GrayF_%d_" % (self.options.grayscale_resolution)
            elif self.options.conversion_type == 9:
                suffix = "_GrayO_%d_" % (self.options.grayscale_resolution)
            elif self.options.conversion_type == 10:
                suffix = "_Cust_"


            pos_file_png_exported = os.path.join(self.options.directory,self.options.filename+".png")
            pos_file_png_BW = os.path.join(self.options.directory,self.options.filename+suffix+"BW.png")
            pos_file_gcode = os.path.join(self.options.directory,self.options.filename+".gcode")


            #Esporto l'immagine in PNG
            self.exportPage(pos_file_png_exported,current_file,bg_color)



            #DA FARE
            #Manipolo l'immagine PNG per generare il file Gcode
            self.PNGtoGcode(pos_file_png_exported,pos_file_png_BW,pos_file_gcode)


        else:
            inkex.errormsg("Directory does not exist! Please specify existing directory!")




########    ESPORTA L IMMAGINE IN PNG
########    Richiamata da effect()

    def exportPage(self,pos_file_png_exported,current_file,bg_color):
        ######## CREAZIONE DEL FILE PNG ########
        #Crea l'immagine dentro la cartella indicata  da "pos_file_png_exported"
        # -d 127 = risoluzione 127DPI  =>  5 pixel/mm  1pixel = 0.2mm
        ###command="inkscape -C -e \"%s\" -b\"%s\" %s -d 127" % (pos_file_png_exported,bg_color,current_file)

        DPI = (254 * self.options.resolution) / 10

        command="inkscape -C -e \"%s\" -b\"%s\" %s -d %d" % (pos_file_png_exported,bg_color,current_file,DPI) #Comando da linea di comando per esportare in PNG

        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_code = p.wait()
        f = p.stdout
        err = p.stderr


########    CREA IMMAGINE IN B/N E POI GENERA GCODE
########    Richiamata da effect()

    def PNGtoGcode(self,pos_file_png_exported,pos_file_png_BW,pos_file_gcode):

        B=255
        N=0
        greyscale = False

        if self.options.conversion_type == 1:
            convert_options = "-normalize -threshold %d%% -colorspace Gray" % (self.options.BW_threshold)
        elif self.options.conversion_type == 2:
            convert_options = "-normalize -monochrome -colorspace Gray"
        elif self.options.conversion_type == 3:
            convert_options = "-normalize -colorspace Gray -dither FloydSteinberg -colors 2 -monochrome -colorspace Gray"
        elif self.options.conversion_type == 4:
            convert_options = "-normalize -ordered-dither o8x8,2 -monochrome -colorspace Gray"
        elif self.options.conversion_type == 5:
            convert_options = "-normalize -colorspace Gray -remap pattern:gray50 -colorspace Gray"
        elif self.options.conversion_type == 6:
            convert_options = "-colorspace Gray"
            greyscale = True
        elif self.options.conversion_type == 7:
            convert_options = "-normalize -colorspace Gray -dither Riemersma -colors %d -colorspace Gray" % (self.options.grayscale_resolution)
            greyscale = True
        elif self.options.conversion_type == 8:
            convert_options = "-normalize -colorspace Gray -dither FloydSteinberg -colors %d -colorspace Gray" % (self.options.grayscale_resolution)
            greyscale = True
        elif self.options.conversion_type == 9:
            convert_options = "-colorspace Gray -ordered-dither o8x8,%d" % (self.options.grayscale_resolution)
            greyscale = True
        elif self.options.conversion_type == 10:
            convert_options = (self.options.custom_cmd) + " -colorspace Gray"
            greyscale = True

        command="convert \"%s\" %s \"%s\"" % (pos_file_png_exported, convert_options, pos_file_png_BW)

        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_code = p.wait()
        f = p.stdout
        err = p.stderr


        reader = png.Reader(pos_file_png_BW)
        w, h, pixels, metadata = reader.read_flat()
        matrice_BN = [[255 for i in range(w)]for j in range(h)]

        for y in range(h):
            for x in range(w):
                pixel_position = (x + y * w)
                matrice_BN[y][x] = pixels[pixel_position] * 255 if metadata['bitdepth'] == 1 else pixels[pixel_position]
                #inkex.debug(pixels[pixel_position])

        #### GENERO IL FILE GCODE ####
        if self.options.preview_only == False: #Genero Gcode solo se devo

            if self.options.flip_y == False: #Inverto asse Y solo se flip_y = False
                #-> coordinate Cartesiane (False) Coordinate "informatiche" (True)
                matrice_BN.reverse()


            Laser_ON = False
            F_G01 = self.options.speed_ON
            Scala = self.options.resolution

            file_gcode = open(pos_file_gcode, 'w')  #Creo il file

            #Configurazioni iniziali standard Gcode
            file_gcode.write('; Generated with:\n; "Raster 2 Laser Gcode generator"\n; based on 305 Engineering work\n')
            file_gcode.write('; Improved by A Metaphysical Drama\n;\n;\n;\n')
            #HOMING
            if self.options.homing == 1:
                file_gcode.write('G28; home all axes\n')
            elif self.options.homing == 2:
                file_gcode.write('$H; home all axes\n')
            else:
                pass
            file_gcode.write('G21; Set units to millimeters\n')
            file_gcode.write('G90; Use absolute coordinates\n')
            #file_gcode.write('G92; Coordinate Offset\n')

            #Creazione del Gcode

            #allargo la matrice per lavorare su tutta l'immagine
            for y in range(h):
                matrice_BN[y].append(B)
            w = w+1

            if not greyscale:
                for y in range(h):
                    if y % 2 == 0 :
                        for x in range(w):
                            if matrice_BN[y][x] == N :
                                if Laser_ON == False :
                                    #file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G00) + '\n')
                                    file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n') #tolto il Feed sul G00
                                    file_gcode.write(self.options.laseron + '\n')
                                    Laser_ON = True
                                if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
                                    if x == w-1 :
                                        file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
                                        file_gcode.write(self.options.laseroff + '\n')
                                        Laser_ON = False
                                    else:
                                        if matrice_BN[y][x+1] != N :
                                            file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
                                            file_gcode.write(self.options.laseroff + '\n')
                                            Laser_ON = False
                    else:
                        for x in reversed(range(w)):
                            if matrice_BN[y][x] == N :
                                if Laser_ON == False :
                                    #file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G00) + '\n')
                                    file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + '\n') #tolto il Feed sul G00
                                    file_gcode.write(self.options.laseron + '\n')
                                    Laser_ON = True
                                if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
                                    if x == 0 :
                                        file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
                                        file_gcode.write(self.options.laseroff + '\n')
                                        Laser_ON = False
                                    else:
                                        if matrice_BN[y][x-1] != N :
                                            file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
                                            file_gcode.write(self.options.laseroff + '\n')
                                            Laser_ON = False

            else: ##SCALA DI GRIGI
                assert (self.options.power_max > self.options.power_min)
                delta = self.options.power_max - self.options.power_min
                # 255 : delta = pix : X
                mul = delta / 255
                base = self.options.power_min

                for y in range(h):
                    if y % 2 == 0 :
                        for x in range(w):
                            if matrice_BN[y][x] != B :
                                if Laser_ON == False :
                                    file_gcode.write('G00 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                    power = int(base + (255 - matrice_BN[y][x]) * mul)
                                    file_gcode.write(self.options.laseron + ' '+ ' S' + str(power) +'\n')
                                    Laser_ON = True

                                if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
                                    if x == w-1 : #controllo fine riga
                                        file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
                                        file_gcode.write(self.options.laseroff + '\n')
                                        Laser_ON = False

                                    else:
                                        if matrice_BN[y][x+1] == B :
                                            file_gcode.write('G01 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
                                            file_gcode.write(self.options.laseroff + '\n')
                                            Laser_ON = False

                                        elif matrice_BN[y][x] != matrice_BN[y][x+1] :
                                            file_gcode.write('G01 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
                                            power = int(base + (255 - matrice_BN[y][x+1]) * mul)
                                            file_gcode.write(self.options.laseron + ' '+ ' S' + str(power) +'\n')


                    else:
                        for x in reversed(range(w)):
                            if matrice_BN[y][x] != B :
                                if Laser_ON == False :
                                    file_gcode.write('G00 X' + str(float(x+1)/Scala) + ' Y' + str(float(y)/Scala) +'\n')
                                    power = int(base + (255 - matrice_BN[y][x]) * mul)
                                    file_gcode.write(self.options.laseron + ' '+ ' S' + str(power) +'\n')
                                    Laser_ON = True

                                if  Laser_ON == True :   #DEVO evitare di uscire dalla matrice
                                    if x == 0 : #controllo fine riga ritorno
                                        file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) +' F' + str(F_G01) + '\n')
                                        file_gcode.write(self.options.laseroff + '\n')
                                        Laser_ON = False

                                    else:
                                        if matrice_BN[y][x-1] == B :
                                            file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
                                            file_gcode.write(self.options.laseroff + '\n')
                                            Laser_ON = False

                                        elif  matrice_BN[y][x] != matrice_BN[y][x-1] :
                                            file_gcode.write('G01 X' + str(float(x)/Scala) + ' Y' + str(float(y)/Scala) + ' F' + str(F_G01) +'\n')
                                            power = int(base + (255 - matrice_BN[y][x-1]) * mul)
                                            file_gcode.write(self.options.laseron + ' '+ ' S' + str(power) +'\n')



            #Configurazioni finali standard Gcode
            file_gcode.write('G00 X0 Y0; home\n')
            #HOMING
            if self.options.homing == 1:
                file_gcode.write('G28; home all axes\n')
            elif self.options.homing == 2:
                file_gcode.write('$H; home all axes\n')
            else:
                pass

            file_gcode.close() #Chiudo il file




########     ########     ########     ########     ########     ########     ########     ########     ########


def _main():
    e=GcodeExport()
    e.affect()

    exit()

if __name__=="__main__":
    _main()




