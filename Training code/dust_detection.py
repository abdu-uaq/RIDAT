import matplotlib
import matplotlib.image as m
import matplotlib.pyplot as plt
import os
import numpy as np
import imageio as io
import os
from sklearn import tree



def rgb2gray(rgb):

    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray


def import_images(folder):
    images = []
    a=os.listdir(folder)  # listdir returns a list of the entries in the folder
    for image in a[1:]:    
        img = m.imread(os.path.join(folder,image))  # imread reads an image from a file into an array
        print(type(img[0][0]))
        if 'numpy' in str(type(img[0][0])):
            img = rgb2gray(img)
        images.append(img)
    return(images)

def make_gif(image_list):
    images = []
    for filename in image_list:
        images.append(io.imread("plots/"+filename))
    io.mimsave('surface1.gif', images, duration=0.5)

def iterate_frames(images):
    for i in range(len(images.images)):
        print(i)
        images.activeimage=i
        current_frame={"xpositions":[],"ypositions":[],"widths":[], "lengths":[],"pixels":[],"name":"undefined"}
        [pos1, bgsub1] = images.find_dust(28)
        print(i)
        current_frame["pixels"]=images.collect_dust(pos1)
        print(i)
        current_frame = images.characterise_dust(current_frame["pixels"])


        images.dust_every_frame[images.activeimage] = current_frame


class Images:
    def __init__(self,images):
        self.images=images # list of all the pixel data of every image
        self.bg = np.zeros_like(self.images[0]) #create a blank slate for background
        self.activeimage=0 # sets the current image worked on for find_dust, collect_dust, and characterise_dust
        self.dust_every_frame=len(self.images)*[0]
        
    def find_bg(self):
        """Function that returns the average of all the images"""
        try:
            for image in self.images:
                self.bg += image
            self.bg = self.bg/len(self.images)
        except: #pictures could be an empty list, we don't want an error in that case. we just don't do anything to it then
            return 0
        
    def find_dust(self,threshold):
        """Function that sets dust images to brightness 1, and stores the positions in dust_positions array"""
        dust_positions=[]
        bgsubtracted_image = self.images[self.activeimage]-self.bg
        for i in range(len(bgsubtracted_image)):
            for j in range(len(bgsubtracted_image[0])):
                if bgsubtracted_image[i][j]>=threshold:
                    bgsubtracted_image[i][j]=1.0
                    dust_positions.append([i,j])
                else:
                    bgsubtracted_image[i][j]=0.0
        return([dust_positions,bgsubtracted_image])
        
    def collect_dust(self,positions):
        """Function that lumps dust pixels into dust grains, by checking if the bright pixels neighbor other bright pixels"""
        
        dust_grains = []
        dust_grains.append([positions[0]])
        positions.pop(0)
        
        while(len(positions)>=1):
            contained = False
            for i in range(len(dust_grains)):
                for j in range(len(dust_grains[i])):
                    if(np.absolute(positions[0][0]-dust_grains[i][j][0])<=1 and np.absolute(positions[0][1]-dust_grains[i][j][1])<=1):
                        contained = i
            if type(contained)==int:
                dust_grains[contained].append(positions[0])
            else:
                dust_grains.append([positions[0]])
            positions.pop(0)
        keep_dustgrains=[]
        
        for grain in (dust_grains):
            if len(grain)>=2:
                keep_dustgrains.append(grain)
        return(keep_dustgrains)
        
        

    def characterise_dust(self,pixels):
        """Funciton that takes pixel locations of each dust grain and outpus entire dust grain position and dimensions"""
        dust_this_frame={"xpositions":[],"ypositions":[],"widths":[], "lengths":[],"pixels":[],"name":"undefined"}
        dust_lengths=len(pixels)*[0] # set placeholder positions and dimensions
        dust_widths= len(pixels)*[0]
        dust_xpositions = len(pixels)*[0]
        dust_ypositions =len(pixels)*[0]
        
        for i in range(len(pixels)):
            for j in range(len(pixels[i])):
                for k in range(j,len(pixels[i])):
                    r2= (pixels[i][j][0]-pixels[i][k][0])**2
                    + (pixels[i][j][1] - pixels[i][k][1])**2
                    if dust_lengths[i] <= np.sqrt(r2):
                        dust_lengths[i] = np.sqrt(r2)
      
        for i in range(len(dust_lengths)):
            dust_widths[i] = len(pixels[i])/(dust_lengths[i]+1)
            
        for i in range(len(pixels)):
            av_x=0
            av_y=0
            for j in range(len(pixels[i])):
                av_x+=pixels[i][j][0]
                av_y+=pixels[i][j][1]
            av_x = av_x/len(pixels[i])
            av_y = av_y/len(pixels[i])
            dust_xpositions[i] = av_x
            dust_ypositions[i] = av_y

        dust_this_frame["pixels"]
        dust_this_frame["xpositions"]= dust_xpositions
        dust_this_frame["ypositions"]=dust_ypositions
        dust_this_frame["widths"]= dust_widths
        dust_this_frame["lengths"]=dust_lengths
        return(dust_this_frame)

    def connect_frames(self,features,labels):
        """When dust in all frames has been sorted and characterised, this function connects dust particles across frames, forming a trajectory"""
        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(features, labels)


        for i in self.dust_every_frame: #check to ensure characterisation has been performed for every frame
            if i==0:
                return 0


        trackx = []
        tracky = []
        trackw=[]

        for i in range(len(self.dust_every_frame[0]["xpositions"])):
            trackx.append([self.dust_every_frame[0]["xpositions"][i]])
            tracky.append([self.dust_every_frame[0]["ypositions"][i]])
            trackw.append([self.dust_every_frame[0]["widths"][i]])
        for i in range(len(trackx)):
            trackframe.append(0)

        for i in range(1,len(self.images)):
            for j in range(len(self.dust_every_frame[i]["xpositions"])):
                belongto=False
                for k in range(len(trackx)):
                    dw = np.abs(self.dust_every_frame[i]["widths"][j] -
                                trackw[k][-1])
                    dp = np.sqrt((self.dust_every_frame[i]["xpositions"][j] -
                                  trackx[k][-1]) ** 2 +
                                 (self.dust_every_frame[i]["ypositions"][j] -
                                  tracky[k][-1]) ** 2)
                    print(clf.predict([[dw,dp]]))
                    if clf.predict([[dw, dp]])=="yes":
                        trackx[k].append(self.dust_every_frame[i]["xpositions"][j])
                        tracky[k].append(self.dust_every_frame[i]["ypositions"][j])
                        trackw[k].append(self.dust_every_frame[i]["widths"][j])
                        belongto=True

                if belongto==False:
                    trackx.append([self.dust_every_frame[i]["xpositions"][j]])
                    tracky.append([self.dust_every_frame[i]["ypositions"][j]])
                    trackw.append([self.dust_every_frame[i]["widths"][j]])



        return(trackx,tracky)

