#!/usr/bin/env python
"""
 
The colour palette is lifted out so that maintencance and extension is clear

 v1.0 Baloothebear  12 Feb 2024


"""

white   = (255, 255, 255)
grey    = (125, 125, 125)
green   = (0, 128, 0)
amber   = (255, 215, 0)
red     = (255, 0, 0)
purple  = (128, 0, 128)
blue    = (0, 0, 255)
black   = (0, 0, 0)
yellow  = (255,255,0)

COLOUR_THEMES= {    'white' : {'light':(255,255,175), 'mid':(200,200,125), 'dark':grey, 'foreground':white, 'background':(25, 25, 25), 'alert':red,'range':[(255,255,75), (255,255,175), white] },
                    'std'   : {'light':(175,0,0), 'mid':grey, 'dark':(50,50,50), 'foreground':white, 'background':black, 'alert':red,'range':[green, amber, red, purple] },
                    'blue'  : {'light':[75, 195, 242,], 'mid':[4, 138, 191], 'dark':[1, 40, 64], 'foreground':white, 'background':[1, 17, 28], 'alert':[75, 226, 242],'range':[ [1, 40, 64],[2, 94, 115],[4, 138, 191],[75, 195, 242,],[75, 226, 242] ] }, #[(0,10,75), (0,100,250)],
                    'red'   : {'light':[241, 100, 75], 'mid':[164, 46, 4], 'dark':[144, 46, 1], 'foreground':white, 'background':[25, 5, 1], 'alert':red,'range':[ [241, 100, 75],[164, 46, 4],[206, 100, 75], [132, 46, 2], [144, 46, 1] ]},  #[(75,10,0), (250,100,0)],
                    'leds'  : {'range':[ [1, 40, 64],[75, 226, 242], [75, 195, 242]] },
                    'back'  : {'range':[ blue, black ] },
                    'grey'  : {'range':[ white,[75, 226, 242], [75, 195, 242] ] },
                    'meter1': {'light':(200,200,200), 'mid':grey, 'dark':(50,50,50), 'foreground':white, 'background':(10, 10, 10), 'alert':red, 'range':[ white, red, grey]},
                    'rainbow': {'white': white, 'grey': grey, 'green': green, 'amber': amber, 'red': red, 'purple': purple, 'blue': blue,  'black': black,  'yellow': yellow, 'range':[grey, red, yellow, green, blue, purple, white]},
                    'black' : { 'light':(240, 240, 240), 'mid': (192, 192, 192), 'dark': (64, 64, 64), 'foreground': white, 'background': (50, 50, 50), 'alert': red, 'range':[(64, 64, 64),(192, 192, 192),(240, 240, 240)]},
                    'ocean' : { 'dark':(0, 54, 74),  'mid':(19, 135, 177), 'light' :(167, 231, 173), 'foreground':(242, 247, 183),'background':(0, 34, 54), 'alert':  (82, 208, 187), 'range':[(0, 54, 74), (17, 96, 128), (19, 135, 177), (0, 173, 209), (82, 208, 187), (167, 231, 173), (242, 247, 183)] },
                    'salmon': { 'dark':(92, 7, 0), 'mid': (236, 154, 147), 'alert':(131, 43, 27), 'light':(255, 181, 175),'foreground': (255, 181, 175), 'background': (25, 3, 0),  'range':[(92, 7, 0), (131, 43, 27), (164, 73, 59), (191, 102, 89), (215, 128, 118), (236, 154, 147), (255, 181, 175)]}
                }
