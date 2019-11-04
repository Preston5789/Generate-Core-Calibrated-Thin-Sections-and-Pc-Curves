# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 09:50:53 2019

@author: craig
"""
#import sys

#from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
#from PyQt5.QtGui import QIcon


#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure
#import matplotlib.pyplot as plt
#
#import numpy as np
#import math
#import xlrd

#from IPython import get_ipython
#get_ipython().magic('reset -sf')



import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton
from PyQt5.QtGui import QIcon
#******************************************************************
import matplotlib
#import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")
import matplotlib.gridspec as gridspec
#******************************************************************
from PyQt5 import QtCore
from PyQt5 import QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt
import numpy as np
from numpy import diff
import math
import xlrd
from colorama import Fore, Style




# =============================================================================
# # ===========================================================================
# # #-------------------------------------------------------------------------- 
# # #                Read Reference Data Spreadsheet 
# # #  Read mapinv_reference_data_carbonates_calculatedMode_Rosetta data 
# # #                which is the Rosetta Stone reference data per Clerke
# # #--------------------------------------------------------------------------
# # ===========================================================================
# =============================================================================


book = xlrd.open_workbook("mapinv_reference_data_carbonates_calculatedMode_Rosetta.xls")  

print( "The number of worksheets is", book.nsheets)
#print( "Worksheet name(s):", book.sheet_names())
sh = book.sheet_by_index(0)
print(sh.name, sh.nrows, sh.ncols)

import win32com.client
o = win32com.client.Dispatch("Excel.Application")
#o.Visible = 1
#o.Workbooks.Add() # for office 97  95 a bit different!


# ---------------------------------------------------------------------------- 
#                  Initialize DATA 
# ----------------------------------------------------------------------------

Permeability = []
Porosity = []
G1 = []
PD1 = []
BV1 = []
G2 = []
PD2 = []
BV2 = []


# ------------------------------------------------------------------ 
#    read in maininv_reference2 data which is just Rosetta Stone 
#                     this is reference data
#                       DATA WILL BE LOADED
# ------------------------------------------------------------------


for i in range(0,sh.nrows,1):
        Permeability.append(sh.cell_value(rowx=i, colx=1))
        Porosity.append(sh.cell_value(rowx=i, colx=2))   #fraction
        G1.append(sh.cell_value(rowx=i, colx=3))
        PD1.append(sh.cell_value(rowx=i, colx=4))
        BV1.append(sh.cell_value(rowx=i, colx=7))
        G2.append(sh.cell_value(rowx=i, colx=5))
        PD2.append(sh.cell_value(rowx=i, colx=6))
        BV2.append(sh.cell_value(rowx=i, colx=8))
        

x4=np.array(Porosity)
y4=np.array(Permeability)


# =============================================================================
# # ===========================================================================
# # #------------------------------------------------------------ 
# # #               
# # #     End of reading in mapinv reference data
# # #------------------------------------------------------------
# # ===========================================================================
# =============================================================================








# =============================================================================
# # ===========================================================================
# # #--------------------------------------------------------------------------
# ##
# ##            Graphical Input of User Porosity and Pereability 
# ##
# # #--------------------------------------------------------------------------
# # ===========================================================================
# =============================================================================

def tellme(s):
    print(s)
    plt.title(s, fontsize=16, color = 'blue')
    plt.draw()



plt.clf()   #clear plot of other things
#tellme('You will define a triangle, click to begin')

plt.figure(1,figsize=(6, 5))
#plt.ion()
plt.semilogy(x4, y4  , 'b-*', linewidth=0, label='RSW Core Data' )
plt.xlim(0.0,.4)
plt.ylim(0.001, 10000)
plt.grid(True)


#plt.waitforbuttonpress()

#Use pts array to store selected points
pts = []

while len(pts) < 1:
    tellme('Select Poro-Perm point with mouse')
    pts = np.asarray(plt.ginput(1, timeout=3))
#        if len(pts) < 3:
#            tellme('Too few points, starting over')
#            time.sleep(1)  # Wait a second

Por = pts.item(0)
Perm = pts.item(1)

print()
print('Porosity =', Por, ' and Permeability =', Perm)
print()



plt.close('all')  










        
# =============================================================================
# # ===========================================================================
# # #--------------------------------------------------------------------------
# ##
# ##            This is the beginnin of Inverse Distance**4 
# ##
# # #--------------------------------------------------------------------------
# # ===========================================================================
# =============================================================================

#Por = float(input('Input Porosity (fraction) = '))
#Perm = float(input('Input Permeability (mD) = '))


por = Por
perm= Perm



unc_phi=0.005
unc_lperm=0.1

mode_est  = 10**(0.194123 + 0.55065*math.log10(perm))



# =============================================================================
# #---------------------------------------------------------------------------- 
# #           
# #              ESTIMATE THOMEER PARAMETERS FOR BOTH PORE SYSTEMS
# #                   
# #----------------------------------------------------------------------------
# =============================================================================

dist_inv = []
dist_phi = []
dist_lperm = []
G1_weight = []
PD1_weight = []
BV1_weight = []
G2_weight = []
PD2_weight = []
BV2_weight = []



dist_inv_total=0
G1_total  = 0
PD1_total = 0
BV1_total = 0
G2_total  = 0
PD2_total = 0
BV2_total = 0




inv_dist_array = []


#------------------------------------------------------------------ 
#               Estimate all Thomeer Parameters for *_est values
#-------------------------------------------------------------------

#this is the mapinv_reference_data being used 
for i in range(0,sh.nrows,1):
        #compute distance and Inverse Distance for por vs Porosity[i] and perm vs Permeability[i]
        dist_phi.append(max(unc_phi,abs(por - Porosity[i])))
        dist_lperm.append(max(unc_lperm,abs(math.log10(perm) - math.log10(Permeability[i]))))
        dist_inv.append(1/(((dist_phi[i]/unc_phi)**4 + (dist_lperm[i]/unc_lperm)**4)))
        dist_inv_total = dist_inv_total +  dist_inv[i]

        
        #calculalte weights for each
        G1_weight.append(dist_inv[i]  * G1[i])
        PD1_weight.append(dist_inv[i] * PD1[i])
        BV1_weight.append(dist_inv[i] * BV1[i])
        G2_weight.append(dist_inv[i]  * G2[i])
        PD2_weight.append(dist_inv[i] * PD2[i])
        BV2_weight.append(dist_inv[i] * BV2[i])
        
        #now Thomeer totals * Weights
        G1_total  = G1_total  + G1_weight[i]
        PD1_total = PD1_total + PD1_weight[i]
        BV1_total = BV1_total + BV1_weight[i]
        G2_total  = G2_total  + G2_weight[i]
        PD2_total = PD2_total + PD2_weight[i]
        BV2_total = BV2_total + BV2_weight[i]

        inv_dist_array.append(dist_inv);  # add items

#back to k values and calculate estimations now
G1_est  = G1_total  / dist_inv_total
PD1_est = PD1_total / dist_inv_total
BV1_est = (BV1_total / dist_inv_total)
G2_est  = G2_total  / dist_inv_total
PD2_est = PD2_total / dist_inv_total
BV2_est = (BV2_total / dist_inv_total)


print()
print(Fore.BLUE +'Thomeer Parameters from Inv Dist Estimations:') 
print(Fore.BLUE + '     Pd1 =',PD1_est, ',  G1 =',G1_est, ', BV1(%) =',BV1_est) 
print(Fore.BLUE + '     Pd2 =',PD2_est, ',  G2 =',G2_est, ', BV2(%) =',BV2_est)
print(Fore.BLUE + '     Mode of PTD =', mode_est, 'microns')  
 
#print('back to normal now') 

#------------------------------------------------------------------------------ 
#               Estimated  Pc plots from estimated Thomeer values
#------------------------------------------------------------------------------

Pc = 0.5
bvarray = []; #make list of 0 length
pcarray = []

   

for j in range(1, 105, 1):
    if Pc > PD1_est:
        BVOCC1 = BV1_est * 10**((-0.434 * G1_est) / math.log10(Pc / PD1_est))
    else:
        BVOCC1 = 0.001

    if Pc > PD2_est:
        BVOCC2 = BV2_est * 10 ** ((-0.434 * G2_est) / math.log10(Pc / PD2_est))
    else:
        BVOCC2 = 0.001

       
    BVOCC = BVOCC1 + BVOCC2
    
    bvarray.append(BVOCC); #add items 
    pcarray.append(Pc); #add items 
    
    Pc = Pc * 1.12

   
x=np.array(bvarray)
y=np.array(pcarray)




# =============================================================================
# # ===========================================================================
# # #--------------------------------------------------------------------------
# # #           
# # #               Find Closest distance Pc curve in poro-perm space
# # #--------------------------------------------------------------------------
# # ===========================================================================
# =============================================================================

a = np.array(inv_dist_array)
inv_dist_thresh = np.percentile(a, 99.999)
print()
#print("Inv Distance Threshold =", inv_dist_thresh)
print()


for i in range(0, sh.nrows, 1):
    if dist_inv[i] > inv_dist_thresh - 0.001:
        G_1 = G1[i]
        Pd1 = PD1[i]
        Bv1 = BV1[i]
        G_2 = G2[i]
        Pd2 = PD2[i]
        Bv2 = BV2[i]
        Perm_r = Permeability[i]
        Por_r = Porosity[i]
        mode_r = math.exp(-1.15*G_1)*(214/Pd1)

#os.system("color 1") # colour can be any number between 1 to 8
print(Fore.RED +  "Thomeer Parameters Reference Set:")
print('     Por_r = ', Por_r,'    ,  Perm_r = ', Perm_r) 
#print('    Pd1_r =',Pd1, '            , G1_r =',G_1, '             , BV1_r =',Bv1, '              , BV2_r =', Bv2, ', Mode = ', mode_r, ' , Perm_r = ', Perm_r, ', Por_r = ', Por_r) 
print('     Pd1_r =',Pd1, '         , G1_r =',G_1, '            , BV1_r =',Bv1) 
print('     Pd2_r =',Pd2, '         , G2_r =',G_2, '            , BV2_r =',Bv2) 
print('     Mode of PTD = ',mode_r , 'microns') 




Pc2 = 0.5
bvarray2 = []; #make list of 0 length
pcarray2 = []

for j in range(1, 105, 1):
    if Pc2 > Pd1:
        BVOCC11 = Bv1 * 10**((-0.434 * G_1) / math.log10(Pc2 / Pd1))
    else:
        BVOCC11 = 0.001

    if Pc2 > Pd2:
        BVOCC22 = Bv2 * 10 ** ((-0.434 * G_2) / math.log10(Pc2 / Pd2))
    else:
        BVOCC22 = 0.001

       
    BVOCC_r = BVOCC11 + BVOCC22
    
    bvarray2.append(BVOCC_r); #add items 
    pcarray2.append(Pc2); #add items 
    
    Pc2 = Pc2 * 1.12

   
x2=np.array(bvarray2)
y2=np.array(pcarray2)













# =============================================================================
# # ===========================================================================
# # #-------------------------------------------------------------------------- 
# # #                Read Thin Section Spreadsheet
# # #  Read CO3 thin Section data which is Arab D Carbonate Data like Rosetta Stone data
# # #--------------------------------------------------------------------------
# # ===========================================================================
# =============================================================================


Por = por
Perm = perm

print()
print(Fore.GREEN + "Representative Thin Section:")
#print()

book = xlrd.open_workbook("CO3_Thin_Sections.xls")   #mapinv_reference cleaned up of obscure tri-modal samples
#print( "The number of worksheets is", book.nsheets)
#print( "Worksheet name(s):", book.sheet_names())
sh = book.sheet_by_index(0)
#print(sh.name, sh.nrows, sh.ncols)
#print()

import win32com.client
o = win32com.client.Dispatch("Excel.Application")
#o.Visible = 1
#o.Workbooks.Add() # for office 97  95 a bit different!
    

#Depth = []
PorosityTS = []
PermeabilityTS = []
Path_TS = []
TS= False

  
for i in range(0,sh.nrows,1):

        PorosityTS.append(sh.cell_value(rowx=i, colx=1))
        PermeabilityTS.append(sh.cell_value(rowx=i, colx=2))
        Path_TS.append(sh.cell_value(rowx=i, colx=3))
       
x3=np.array(PorosityTS)
y3=np.array(PermeabilityTS)


#plt.figure(1,figsize=(6, 5))
#plt.semilogy(x3, y3  , 'b-*', linewidth=0, label='TS Core Data' )
#plt.show(block=False)
#plt.ion()
#        print(Depth[i],Porosity[i],Permeability[i],Path_TS[i])       
# =============================================================================
# # ===========================================================================
# ##
# ##                   Inverse Distance^4 
# ##
# # ===========================================================================
# =============================================================================


#Porosity_est=0
#Permeability_est=0
por = Por
perm= Perm
  
#print(por, perm)  
        
unc_phi=0.005
unc_lperm=0.1



dist_inv = []
dist_phi = []
dist_lperm = []
inv_dist_array = []
dist_inv_total=0



#------------------------------------------------------------------------------ 
#          Estimate Inv Distance data
#------------------------------------------------------------------------------

#this is the mapinv_reference_data being used using the mapinv Porosity and Permeability vs. por and perm
for i in range(0,sh.nrows ,1):
        #compute distance and Inverse Distance for por vs Porosity[i] and perm vs Permeability[i]
        dist_phi.append(max(unc_phi,abs(por - PorosityTS[i])))
        dist_lperm.append(max(unc_lperm,abs(math.log10(perm) - math.log10(PermeabilityTS[i]))))
        dist_inv.append(1/(((dist_phi[i]/unc_phi)**4 + (dist_lperm[i]/unc_lperm)**4)))
        dist_inv_total = dist_inv_total +  dist_inv[i]

        inv_dist_array.append(dist_inv); #add items


a = np.array(inv_dist_array) 
inv_dist_thresh = np.percentile(a, 99.999)


#plt.figure(2)        
for p in range(0,sh.nrows ,1):        
        if dist_inv[p] > inv_dist_thresh - 0.001 and dist_inv[p] > 0.001:
            TS = Path_TS[p]
            Por_TS = PorosityTS[p]
            Perm_TS = PermeabilityTS[p]
       

            print("     Reference Data: Porosity =",Porosity[i], ", Permeability =", Permeability[i],", Inv Dist '",dist_inv[i],TS)
            print(Fore.GREEN +"     Porosity =",PorosityTS[p], ", Permeability =", PermeabilityTS[p])
            print(Fore.GREEN +"     Inv Dist '",dist_inv[p],", TS Image =", Path_TS[p])    
            img=mpimg.imread(TS)
#            imgplot = plt.imshow(img)
#            plt.show()
#        else:
#            TS = 'blank.PNG'
#            Por_TS = 0
#            Perm_TS = 0
#            img=mpimg.imread(TS)               

if not TS :
    print("     'No Representative Thin Section'")
    TS = 'blank.PNG'
    Por_TS = 0
    Perm_TS = 0
    img=mpimg.imread(TS)               
    
else:
    print(Fore.GREEN + "     Representative Thin Section is Available")
       
print(Style.RESET_ALL) 







# =============================================================================
# # ===========================================================================
# # #-------------------------------------------------------------------------- 
# # #                
# # #               Qt GUI Plots made here
# # #--------------------------------------------------------------------------
# # ===========================================================================
# =============================================================================

#Define Canvas
class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 50
        self.top = 100
        self.title = 'Carbonate Petrophysical Analysis'
        self.width = 500
        self.height = 1200
        self.initUI()

#Define Canvas and Pushbutton
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

##### this defines the width and height of canvas 
        m = PlotCanvas(self, width=5, height=12)
        m.move(0,0)

        button = QPushButton('Quit Window', self)
        button.setDefault(True)
        button.setToolTip('Push this button to quit')
        #Botton starts at 500 and 0
        button.move(400,0)
        #Botton starts at 500 and goes +140 to 640 to cover canvas
        button.resize(100,30)

        def on_button_clicked():
            sys.exit(app.exec_())



        button.clicked.connect(on_button_clicked)




        self.show()
#            junk = input("Hit Enter to Exit")
#            self.close()


class PlotCanvas(FigureCanvas):

#what is this???
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
#            self.axes = fig.add_subplot(211)  apparently not needed now

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        self.plot()
        self.plot2()
        self.plot3()
        self.plot4()


# Pc Plot across top 0 to 3
    def plot(self):

        gs = gridspec.GridSpec(nrows=3, 
                               ncols=3, 
#                               figure=fig, 
                               width_ratios= [1, 1, 1],
                               height_ratios=[1, 1, 1],
                               wspace=0.3,
                               hspace=0.3)
#wspace = 0.2   # the amount of width reserved for blank space between subplots
#hspace = 0.2   # the amount of height reserved for white space between subplots 

       
#        ax = self.figure.add_subplot(411) 
        ax = self.figure.add_subplot(gs[0, 0:3]) 
        
        
#        ax.subplots_adjust(hspace=0.4, wspace=0.4)
        
        ax.loglog(x, y  , 'r-', linewidth=3, label='Inv Dist Weighted Pc Curve' )
        ax.loglog(x2, y2, 'b--' , linewidth=3, label='Nearest Pc Curve')
        ax.set_xlim(50, 0.1)
        #ax.gca().invert_xaxis()
        ax.set_ylim(1, 100000)
        ax.set_title("Pc Curves from Estimated Thomeer Parameters", color = 'red')            
        ax.set_ylabel('Pc Mercury', color = 'red')
        ax.set_xlabel('BVOCC', color = 'red')
        ax.grid(True)
        ax.legend()

        ax.text(50,8,' h = 2.4ft',horizontalalignment='left', fontsize=10, color='green')
        ax.text(50,80,' h = 24.5ft',horizontalalignment='left', fontsize=10, color='green')
        ax.text(50,800,' h = 245ft',horizontalalignment='left', fontsize=10, color='green') 
        ax.text(50,PD1_est,'------- height @ Pd',horizontalalignment='left', fontsize=8, color='red', fontstyle='italic') 
#        ax.text(50,9000,' h = 4544ft',horizontalalignment='left')       

        ax.text(.1,PD1_est,' Pd',horizontalalignment='left', fontsize=11, color='red')
        ax.text(max(diff(x)) + 2,    PD1_est + 6*PD1_est,'    G1',horizontalalignment='right', fontsize=11, color='red')
        ax.text(BV1_est+BV2_est,  14000,'  BVinf',horizontalalignment='right', fontsize=11, color='red')
        ax.axvline(x= BV1_est, color='red' , linestyle='--')  #vertical line        
#        ax.annotate('Pd', fontsize=10, color='green', xy=(.1, PD1_est), xytext=(.5, 2),
#            arrowprops=dict(facecolor='green', shrink=0.01),
#            )
#        ax.annotate('BVinf', fontsize=10, color='green', xy=(BV1_est+BV2_est, 10000), xytext=(60,10000),
#            arrowprops=dict(facecolor='green', shrink=0.01),
#            )
#        ax.annotate('G1', fontsize=10, color='green', xy=(1, 100), xytext=(1,100),
##            arrowprops=dict(facecolor='green', shrink=1),
#            )


 
        self.draw()


#Poro_Perm xplot Thomeer Clastics dB
    def plot2(self):

        gs = gridspec.GridSpec(nrows=3, 
                               ncols=3, 
#                               figure=fig, 
                               width_ratios= [1, 1, 1],
                               height_ratios=[1, 1, 1],
                               wspace=0.3,
                               hspace=0.3)
        
        cx = self.figure.add_subplot(gs[1,0:3])        
        
        #cx = self.figure.add_subplot(412) 

        cx.semilogy(x4, y4  , 'b-*', linewidth=0, label='Thomeer dB Core Data' )
        cx.semilogy(Por, Perm  , 'r-D', linewidth=0, label='User Poro-perm' )
        cx.semilogy(Por_r, Perm_r  , 'g-D', linewidth=0, label='Thomeer Nearest Sample ' )
#        cx.semilogy(Por_TS, Perm_TS  , 'c-^', linewidth=0, label='TS Poro-perm Point' )
        cx.set_xlim(0.0,.4)
        #ax.gca().invert_xaxis()
        cx.set_ylim(0.001, 10000)
        cx.set_title("Carbonate dB with Thomeer Pc Parameters", color = 'blue')            
        cx.set_ylabel('Permeability', color = 'blue')
        cx.set_xlabel('Porosity (Carbonate dB with Thomeer Pc Parameters)', color = 'blue')
        cx.annotate('User Poro-Perm', fontsize=10, color='red', xy=(Por, Perm), xytext=(.3, 1),
                    arrowprops=dict(facecolor='red', shrink=0.05),
                    )
        cx.annotate('Nearest Pc', fontsize=10, color='green' ,xy=(Por_r, Perm_r), xytext=(.01, 1500),
                    arrowprops=dict(facecolor='green', shrink=0.05),
                    )



        cx.grid(True)
        cx.legend()

        self.draw()


#Poro_Perm xplot of Katmai Core data
    def plot3(self):

#wspace = 0.2   # the amount of width reserved for blank space between subplots
#hspace = 0.2   # the amount of height reserved for white space between subplots         
        
        gs = gridspec.GridSpec(nrows=3, 
                               ncols=3, 
#                               figure=fig, 
                               width_ratios= [1, 1, 1],
                               height_ratios=[1, 1, 1],
                               wspace=0.0,
                               hspace=0.4)
        
        cx = self.figure.add_subplot(gs[2,0:3])        
        #cx = self.figure.add_subplot(414) 
        cx.semilogy(x4, y4  , 'y-*', linewidth=0, label='Thomeer dB Core Data' )
        cx.semilogy(x3, y3  , 'b-*', linewidth=0, label='TS Core Data' )
        cx.semilogy(Por, Perm  , 'r-D', linewidth=0, label='User Poro-perm ' )
        cx.semilogy(Por_TS, Perm_TS  , 'g-D', linewidth=0, label='TS Poro-perm ' )
        cx.set_xlim(0.0,.4)
        #ax.gca().invert_xaxis()
        cx.set_ylim(0.001, 10000)
        #cx.set_title("Katmai Core Analysis Database")            
        cx.set_ylabel('Permeability', color='green')
        cx.set_xlabel('Porosity (Carbonate Core Analysis dB with TS)', color = 'green')
        cx.grid(True)
        cx.annotate('User Poro-Perm', fontsize=10, color='red', xy=(Por, Perm), xytext=(.3, 1),
                    arrowprops=dict(facecolor='red', shrink=0.05),
                    )
        cx.annotate('Nearest TS', fontsize=10, color='green' ,xy=(Por_TS, Perm_TS), xytext=(.08, 0.0015),
                    arrowprops=dict(facecolor='green', shrink=0.05),
                    )

        cx.annotate('Nearest TS', fontsize=10, color='green' , xy=(0.16, 1000), xytext=(.24, 20000),
                    arrowprops=dict(facecolor='green', shrink=0.1),
                    )


        cx.legend()

        self.draw()



#Thin Section plot row 1 and column 0
    def plot4(self):

#wspace = 0.2   # the amount of width reserved for blank space between subplots
#hspace = 0.2   # the amount of height reserved for white space between subplots         
        
        gs = gridspec.GridSpec(nrows=3, 
                               ncols=3, 
#                               figure=fig, 
                               width_ratios= [1, 1, 1],
                               height_ratios=[1, 1, 1],
                               wspace=-0.3,
                               hspace=-0.4)
        
        bx = self.figure.add_subplot(gs[2,0:1]) 
#        bx = self.figure.add_subplot(413)  
#        imgplot = ax.imshow(img)

        bx.axes.get_xaxis().set_visible(False)
        bx.axes.get_yaxis().set_visible(False)

        bx.imshow(img)
#        bx.set_xlabel('Representative Thin Section')

        self.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

quit
exit
#os.system('cls')
#sys('clear')
