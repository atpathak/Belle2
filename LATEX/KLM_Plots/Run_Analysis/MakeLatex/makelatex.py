# write-latex.py
import os
import sys
import time
import subprocess
from ROOT import TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

def writelatex():
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
    \includegraphics[scale=0.1]{/afs/cern.ch/user/s/swaban/public/university-of-louisville-logo.png}
    \end{minipage}}
    \date {{KLM meeting}\\9 April 2019}
    \begin{document}
    \begin{frame}
    \titlepage
    \end{frame}
    %%------------------------------------------------
'''
    Main = r'''%%---------------
    \begin{frame}
    \frametitle{Short list of KLM plots}
    \vspace*{.05cm}
    \begin{center}
    \begin{normalsize}
    \vspace*{-.2cm}
    \begin{center}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/test_hitmap_r%(run)s/png/SectLayPlaneZBF}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/test_hitmap_r%(run)s/png/SectLayPlanePhiBF}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/png-e%(exp)sr%(run)s/occupancyForwardXYBkgd}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/png-e%(exp)sr%(run)s/NRawKLM}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/png-e%(exp)sr%(run)s/RawKLMnumNodes}\\
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/test_hitmap_r%(run)s/png/SectLayPlaneZBB}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/test_hitmap_r%(run)s/png/SectLayPlanePhiBB}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/png-e%(exp)sr%(run)s/occupancyBackwardXYBkgd}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/png-e%(exp)sr%(run)s/RawKLMnodeID}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/afs/cern.ch/user/a/atpathak/afswork/public/Pixel/KLM_Plots/Run_Analysis/png-e%(exp)sr%(run)s/rawKLMlaneFlag} \\
    
    \end{center}
    \end{normalsize}
    \end{center}
    \end{frame}
    %%---------------
'''
    footer = r'''\end{document}'''
    content = header + Main + footer

    TexFile = "Slides_e{0}_r{1}.tex".format(exp, run)

    
    with open(TexFile,'w') as f:
        f.write(content % {"run": run , "exp" : exp})
        

    #os.system("pdflatex Slides.tex")
    commandLine = subprocess.Popen(['pdflatex', TexFile])
    commandLine.communicate()

#=========================================================================
#
#   Main routine
#
#=========================================================================

parser = OptionParser()
parser.add_option('-e', '--experiment', dest='eNumber',
                  default='7',
                  help='Experiment number [default=7]')
parser.add_option('-r', '--run', dest='rNumber',
                  default='1505',
                  help='Run number [default=0604]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))

#RunLocation = "/ghi/fs01/belle2/bdata/Data/Raw/e{0}/".format(exp)

writelatex()
