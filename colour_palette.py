#!/usr/bin/env python
"""
 
The colour palette is lifted out so that maintencance and extension is clear

 v1.0 Baloothebear  12 Feb 2024


"""

white   = [255, 255, 255]
grey    = [125, 125, 125]
green   = [0, 128, 0]
amber   = [255, 215, 0]
red     = [255, 0, 0]
purple  = [128, 0, 128]
blue    = [0, 0, 255]
black   = [0, 0, 0]
yellow  = [255,255,0]

COLOUR_THEMES= {    'white' : {'light':[255,255,175], 'mid':[200,200,125], 'dark':grey, 'foreground':white, 'background':[50, 50, 50], 'alert':red,'range':[[255,255,75], [255,255,175], white] },
                    'std'   : {'light':[175,0,0], 'mid':grey, 'dark':[50,50,50], 'foreground':white, 'background':[10,5,5], 'alert':red,'range':[green, amber, red, purple] },
                    'blue'  : {'light':[75, 195, 242,], 'mid':[4, 138, 191], 'dark':[1, 40, 64], 'foreground':white, 'background':[1, 35, 50], 'alert':[75, 226, 242],'range':[ [1, 40, 64],[2, 94, 115],[4, 138, 191],[75, 195, 242,],[75, 235, 255] ] }, #[[0,10,75], [0,100,250]],
                    'red'   : {'light':[241, 100, 75], 'mid':[164, 46, 4], 'dark':[144, 46, 1], 'foreground':white, 'background':[25, 5, 1], 'alert':red,'range':[green, amber, red, purple] },  #[[75,10,0], [250,100,0]],
                    'leds'  : {'background': [5, 15, 30], 'range':[ [1, 40, 64],[75, 226, 242], [75, 195, 242]] },
                    'back'  : {'range':[ blue, black ] },
                    'grey'  : {'range':[ white,[75, 226, 242], [75, 195, 242] ] },
                    'meter1': {'light':[200,200,200], 'mid':grey, 'dark':[50,50,50], 'foreground':white, 'background':[10, 10, 10], 'alert':red, 'range':[ white, red, grey]},
                    'rainbow': {'white': white, 'grey': grey, 'green': green, 'amber': amber, 'red': red, 'purple': purple, 'blue': blue,  'black': black,  'yellow': yellow, 'range':[grey, red, yellow, green, blue, purple, white]},
                    'black' : { 'light':[240, 240, 240], 'mid': [192, 192, 192], 'dark': [64, 64, 64], 'foreground': white, 'background': [50, 50, 50], 'alert': red, 'range':[[64, 64, 64],[192, 192, 192],[240, 240, 240]]},
                    'ocean' : { 'dark':[0, 54, 74],  'mid':[19, 135, 177], 'light' :[167, 231, 173], 'foreground':[242, 247, 183],'background':[0, 34, 54], 'alert':  [82, 208, 187], 'range':[[0, 54, 74], [17, 96, 128], [19, 135, 177], [0, 173, 209], [82, 208, 187], [167, 231, 173], [242, 247, 183]] },
                    'salmon': { 'dark':[92, 7, 0], 'mid': [236, 154, 147], 'alert':[131, 43, 27], 'light':[255, 181, 175],'foreground': [255, 181, 175], 'background': [25, 3, 0], 'range':[green, amber, red, purple]},
                    'space' : { 'background': black, 'dark': [39, 70, 144], 'mid': [63, 89, 156], 'light': [54, 143, 139], 'foreground': [243, 223, 193], 'alert': purple, 'range': [[27, 38, 79], [39, 70, 144], [63, 89, 156], [54, 143, 139], [243, 223, 193]]},   #[27, 38, 79]
                    'zomp'  : { 'background': [46, 64, 87], 'dark': [102, 161, 130], 'mid': [202, 255, 185], 'light': [174, 247, 142], 'foreground':[192, 212, 97], 'alert': white, 'range':[[46, 64, 87], [102, 161, 130], [202, 255, 185], [174, 247, 142], [192, 212, 97]] },
                    'tea'   : { 'background': [29, 47, 111], 'dark': [131, 144, 250], 'mid': [250, 199, 72], 'light': [249, 233, 236], 'foreground': [248, 141, 173], 'alert': white, 'range': [[29, 47, 111], [131, 144, 250], [250, 199, 72], [249, 233, 236], [248, 141, 173]] },
                    'hifi'  : { 'background': [5, 15, 30], 'dark': [25, 40, 60],           'mid': [50, 65, 85], 'light': [180, 230, 255],  'foreground': [230, 240, 255], 'alert': [0, 191, 255],   'range': [[30, 45, 65],    [40, 80, 160],    [0, 120, 200],   [0, 191, 255],   [180, 230, 255]  ] }
                }

#

# Palette inspiration from:  https://coolors.co/eff7cf-bad9b5-aba361-732c2c-420c14
# p= [{"name":"Space cadet","hex":"1b264f","rgb":[27,38,79],"cmyk":[66,52,0,69],"hsb":[227,66,31],"hsl":[227,49,21],"lab":[16,10,-27]},{"name":"Marian blue","hex":"274690","rgb":[39,70,144],"cmyk":[73,51,0,44],"hsb":[222,73,56],"hsl":[222,57,36],"lab":[31,15,-44]},{"name":"YInMn Blue","hex":"3f599c","rgb":[63,89,156],"cmyk":[60,43,0,39],"hsb":[223,60,61],"hsl":[223,42,43],"lab":[39,12,-40]},{"name":"Dark cyan","hex":"368f8b","rgb":[54,143,139],"cmyk":[62,0,3,44],"hsb":[177,62,56],"hsl":[177,45,39],"lab":[54,-27,-6]},{"name":"Champagne","hex":"f3dfc1","rgb":[243,223,193],"cmyk":[0,8,21,5],"hsb":[36,21,95],"hsl":[36,68,85],"lab":[90,2,17]}]

# p1= [{"name":"Charcoal","hex":"2e4057","rgb":[46,64,87],"cmyk":[47,26,0,66],"hsb":[214,47,34],"hsl":[214,31,26],"lab":[27,0,-16]},{"name":"Zomp","hex":"66a182","rgb":[102,161,130],"cmyk":[37,0,19,37],"hsb":[148,37,63],"hsl":[148,24,52],"lab":[62,-26,10]},{"name":"Tea green","hex":"caffb9","rgb":[202,255,185],"cmyk":[21,0,27,0],"hsb":[105,27,100],"hsl":[105,100,86],"lab":[95,-29,28]},{"name":"Light green","hex":"aef78e","rgb":[174,247,142],"cmyk":[30,0,43,3],"hsb":[102,43,97],"hsl":[102,87,76],"lab":[91,-41,43]},{"name":"Yellow Green","hex":"c0d461","rgb":[192,212,97],"cmyk":[9,0,54,17],"hsb":[70,54,83],"hsl":[70,57,61],"lab":[81,-23,54]}]
# p2= [{"name":"Delft Blue","hex":"1d2f6f","rgb":[29,47,111],"cmyk":[74,58,0,56],"hsb":[227,74,44],"hsl":[227,59,27],"lab":[22,17,-39]},{"name":"Vista Blue","hex":"8390fa","rgb":[131,144,250],"cmyk":[48,42,0,2],"hsb":[233,48,98],"hsl":[233,92,75],"lab":[63,23,-55]},{"name":"Saffron","hex":"fac748","rgb":[250,199,72],"cmyk":[0,20,71,2],"hsb":[43,71,98],"hsl":[43,95,63],"lab":[83,6,67]},{"name":"Lavender blush","hex":"f9e9ec","rgb":[249,233,236],"cmyk":[0,6,5,2],"hsb":[349,6,98],"hsl":[349,57,95],"lab":[94,6,0]},{"name":"Tickle me pink","hex":"f88dad","rgb":[248,141,173],"cmyk":[0,43,30,3],"hsb":[342,43,97],"hsl":[342,88,76],"lab":[71,44,1]}]
# t = ''
# r= []
# for c in p1:
#     t += "'light': %s, " % c["rgb"]
#     r.append(c["rgb"])
# print(t,'range', r)    