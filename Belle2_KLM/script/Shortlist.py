# write-latex.py
import os
import sys
import time
import subprocess
from ROOT import TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

def findpng(Location):

    os.chdir(Location)
    pngdir = sorted(filter(os.path.isfile, os.listdir(Location)), key=os.path.getmtime)
    png = [i[:-4] for i in pngdir]
    return png

def writelatex(Location):

    run = findpng(RunLocation)
    
    header = r'''\documentclass{beamer}
    \mode<presentation> {
    \usetheme{default}
    \setbeamertemplate{footline}[page number] 
    \setbeamertemplate{navigation symbols}{} 
    }
    \usepackage{graphicx}
    \usepackage{booktabs}
    \usepackage{amsmath}
    \usepackage{slashed}
    \usepackage{color}
    \usepackage{rotating}
    \usepackage{array}
    \usepackage{varwidth}
    \usepackage{pdfpages}
    \usepackage{pgffor}
    %%----------------------------------------------------------------------------------------
    %%	TITLE PAGE 
    %% Caution: If you want to comment out then please use %% (double percentage)
    %%----------------------------------------------------------------------------------------

    \title{Analysis of KLM Run} %% The short title appears at the bottom of every slide, the full title is only on the title page
    \author{{\bf Atanu ~Pathak} \\}
    \institute{\begin{minipage}{0.5\textwidth}\centering
    \includegraphics[scale=0.1]{/home/belle2/atpathak/png/university-of-louisville-logo.png}
    \end{minipage}}
    \begin{document}
    \begin{frame}
    \titlepage
    \end{frame}
    %%------------------------------------------------
'''
    Main = ''
    for j in range(1,29):
        Main1 =r'''%%---------------
        \begin{frame}
        \frametitle{List of Plots}
        \vspace*{.05cm}
        \begin{center}
        {\scalebox{.60}{
        \begin{tabular}{|c|c|c|}\hline\hline
        Page Number & Plot Name & Sign  \\\hline

'''
        Main2 = ''
        for i, name in enumerate(run[(j-1)*20:j*20], 2):
            
            page  = 20*(j-1)+i
            Main2 += str(page)+''' & '''+name.replace('_','\_')+''' &  \\\ \hline \n'''


        Main3 = '''\hline
        \end{tabular}
        }}
        
        \end{center}
        \end{frame}
    
'''
        Main += Main1 + Main2 + Main3

    footer = r'''\end{document}
'''
    
    content = header + Main + footer

    if not os.path.exists(Location):
        os.makedirs(Location)
            

    TexFile = "/home/belle2/atpathak/ppcc2018/work/Slides_1Jul2019/Slides_shortlist/Slides.tex"

    with open(TexFile,'w') as f:
        f.write(content)

#=========================================================================
#
#   Main routine
#
#=========================================================================

RunLocation = "/home/belle2/atpathak/ppcc2018/work/Slides_1Jul2019/png-e0008r03115/"

writelatex('/home/belle2/atpathak/ppcc2018/work/Slides_1Jul2019/Slides_shortlist/')
    
