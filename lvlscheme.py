import cmcrameri
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sys
sys.path.insert(0, '/Users/johannesheines/Documents/UiO/Master/Masteroppgave')
import figpresets

# TODO: make into a python package

arrowprops = {'width': 0.5,
              'headwidth': 4,
              'headlength': 3}
#colourmap = dict(zip(['k', 'b', 'r'], sns.color_palette("cmc.grayC", 3))) # map easy to write colours to the desired colourmap 
colourmap = {'k':'#aaa', 'b':'mediumpurple', 'r':'xkcd:evergreen'}

def main():
    
    lvlfile = sys.argv[1]
    gammafile = sys.argv[2]
    savename = sys.argv[3]
    lvldf = pd.read_table(lvlfile, sep='\t', comment='#')
    lvldf['colour'].fillna('k', inplace=True)
    lvldf['linestyle'].fillna('-', inplace=True)
    gammadf = pd.read_table(gammafile, sep='\t', dtype={'label':str}, comment='#')
    gammadf['colour'].fillna('k', inplace=True)
    gammadf['label'].fillna('', inplace=True)
#    for df in (lvldf, gammadf):
#        print(df)
#        print(df.dtypes)

    fig,ax = plt.subplots(figsize=(5,4))
    scheme = lvlscheme(lvldf, gammadf)
    scheme.plotlvl(ax)
#    print(lvldf.loc[lvldf['lvlE']==679])
    scheme.plotgamma(ax)
    ax.axis('off')
    fig.tight_layout(pad=0, rect=(-0.05, 0, 1, 1))
    plt.savefig(savename, format='eps')
    plt.show()

    return

class lvlscheme(object):
    def __init__(self, lvldf, gammadf):
        self.lvldf = lvldf
        self.gammadf = gammadf
        self.offset = {}

    def plotlvl(self,ax):
        y=self.lvldf['lvlE']
        xmin=self.lvldf['bandN']
        xmax=self.lvldf['bandN']+1
        colors=[colourmap[key] for key in self.lvldf['colour']]
        linestyles=self.lvldf['linestyle']
        ax.hlines(y, xmin, xmax, colors, linestyles)
        # add labels
        sidepad = 0.02
        for index, row in self.lvldf.iterrows():
            ax.annotate(f"{row['lvlE']}", xy=(row['bandN']+1-sidepad, row['lvlE']), va='bottom', ha='right', color=colourmap[row['colour']])
            ax.annotate(f"${row['spin']}^{row['parity']}$", xy=(row['bandN']+sidepad, row['lvlE']), va='bottom', ha='left', color=colourmap[row['colour']])

    def drawtransition(self, ax, lvli: pd.Series, lvlf: pd.Series, label, auxlimit=2):
        lvli = lvli.iloc[0]
        lvlf = lvlf.iloc[0]
        # Determine x coordinates of the arrow
        bandsep = lvli['bandN'] - lvlf['bandN']
        if abs(bandsep) >= auxlimit:
            x_start, x_end = self.auxlinetransition(ax, lvli, lvlf)
        elif -1 < bandsep < 1:
            x_start = x_end = (lvli['bandN'] + lvlf['bandN'])/2 + 0.5
        elif bandsep >= 1:
            x_start = lvli['bandN']
            x_end = lvlf['bandN']+1
        elif bandsep <= -1:
            x_start = lvli['bandN']+1
            x_end = lvlf['bandN']
        ax.annotate("", xy=(x_end, lvlf['lvlE']), xytext=(x_start, lvli['lvlE']), arrowprops=arrowprops)
        # add label
        sidepad = 0.01
        if x_start == x_end:
            va = 'center'
            ha = 'left'
        elif x_start < x_end:
            va = 'top'
            ha = 'right'
        else:
            va = 'top'
            ha = 'left'
        ax.annotate(label, xy=((x_start+x_end)/2+sidepad, (lvli['lvlE']+lvlf['lvlE'])/2), ha=ha, va=va, color=arrowprops['color']) 

    def plotgamma(self, ax):
        for Ei,Ef,col,label in zip(self.gammadf['Ei'], self.gammadf['Ef'], self.gammadf['colour'], self.gammadf['label']):
            arrowprops['color'] = colourmap[col]
            self.drawtransition(ax, lvli=self.lvldf.loc[self.lvldf['lvlE']==Ei], lvlf=self.lvldf.loc[self.lvldf['lvlE']==Ef], label=label)

    def auxlinetransition(self, ax, lvli, lvlf):
        angle = 1e-4
        range = (lvli['bandN'], lvlf['bandN'])
        offset_direction = (range[1]-range[0])/abs(range[1]-range[0])
        try:
            self.offset[lvli['lvlE']] += offset_direction*0.1 # offset between subsequent auxiliary gammas
        except KeyError:
            self.offset[lvli['lvlE']] = (range[0] < range[1]) - offset_direction*0.4 # distence from edge of first auxiliary gamma
        offset = self.offset[lvli['lvlE']]
        x_start = lvli['bandN'] + offset
        x_end = x_start + offset_direction * (lvli['lvlE'] - lvlf['lvlE'])*np.tan(angle) 
        ax.hlines(y=lvlf['lvlE'], xmin=min(range)+1, xmax=x_end, colors='lightgrey', linestyles=':')
        return(x_start, x_end)

if __name__ == '__main__':
    main()
