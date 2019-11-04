# write-latex.py
import os
import sys
import time
import subprocess
from ROOT import TH1F, TH2F, TCanvas, THistPainter, TPad
from optparse import Option, OptionValueError, OptionParser

def writelatex(Location):
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
    %%\begin{frame}
    %%\titlepage
    %%\end{frame}
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
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SectLayPlaneZBF}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SectLayPlanePhiBF}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/png-e%(exp)sr%(run)s/occupancyForwardXYPromptBkgd}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/png-e%(exp)sr%(run)s/NRawKLM}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/png-e%(exp)sr%(run)s/RawKLMnumNodes}\\
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SectLayPlaneZBB}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SectLayPlanePhiBB}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/png-e%(exp)sr%(run)s/occupancyBackwardXYPromptBkgd}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/png-e%(exp)sr%(run)s/RawKLMnodeID}
    \includegraphics[width=.20\textwidth,height=.25\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/png-e%(exp)sr%(run)s/rawKLMlaneFlag} \\
    
    \end{center}
    \end{normalsize}
    \end{center}
    \end{frame}
    %%----------------------------------
    \begin{frame}
    \frametitle{BF TDC (RPCs)}
    \vspace*{.05cm}
    \begin{center}
    \begin{normalsize}
    \vspace*{-.2cm}
    \begin{center}

    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBF0}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBF1}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBF2}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBF3} \\
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBF4}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBF5}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBF6}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBF7}

    \end{center}
    \end{normalsize}
    \end{center}
    \end{frame}
    %%------------------------------------------
    \begin{frame}
    \frametitle{BB TDC (RPCs)}
    \vspace*{.05cm}
    \begin{center}
    \begin{normalsize}
    \vspace*{-.2cm}
    \begin{center}
    
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBB0}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBB1}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBB2}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBB3} \\
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBB4}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBB5}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBB6}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/RPCTdcBB7}


    \end{center}
    \end{normalsize}
    \end{center}
    \end{frame}
    %%----------------------------------------------
    \begin{frame}
    \frametitle{BF TDC (Scintillator)}
    \vspace*{.05cm}
    \begin{center}
    \begin{normalsize}
    \vspace*{-.2cm}
    \begin{center}
    
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBF0}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBF1}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBF2}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBF3} \\
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBF4}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBF5}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBF6}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBF7}

    \end{center}
    \end{normalsize}
    \end{center}
    \end{frame}
    %%----------------------------------------------
    \begin{frame}
    \frametitle{BB TDC (Scintillator)}
    \vspace*{.05cm}
    \begin{center}
    \begin{normalsize}
    \vspace*{-.2cm}
    \begin{center}
    
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBB0}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBB1}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBB2}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBB3} \\
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBB4}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBB5}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBB6}
    \includegraphics[width=.25\textwidth,height=.30\textheight,type=png,ext=.png,read=.png]{/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e%(exp)s/bklmroots/r%(run)s/hitmap-e%(exp)sr%(run)s/SciTdcBB7}
    
    \end{center}
    \end{normalsize}
    \end{center}
    \end{frame}
    %%--------------------------------------------------
'''
    footer = r'''\end{document}'''
    content = header + Main + footer

    if not os.path.exists(Location):
        os.makedirs(Location)
        
    TexFile = "/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/Short-listed/Slides_e{0}_r{1}.tex".format(exp, run)

    
    with open(TexFile,'w') as f:
        f.write(content % {"run": run , "exp" : exp})
        

    #os.system("pdflatex Slides.tex")
    os.chdir(Location)
    commandLine = subprocess.Popen(['pdflatex', TexFile])
    commandLine.communicate()
    os.system("rm -rf Slides_e{0}_r{1}.tex".format(exp, run))
    os.system("rm -rf Slides_e{0}_r{1}.out".format(exp, run))
    os.system("rm -rf Slides_e{0}_r{1}.snm".format(exp, run))
    os.system("rm -rf Slides_e{0}_r{1}.aux".format(exp, run))
    os.system("rm -rf Slides_e{0}_r{1}.nav".format(exp, run))
    os.system("rm -rf Slides_e{0}_r{1}.toc".format(exp, run))
    os.system("rm -rf Slides_e{0}_r{1}.log".format(exp, run))

#=========================================================================
#
#   Main routine
#
#=========================================================================

parser = OptionParser()
parser.add_option('-e', '--experiment', dest='eNumber',
                  default='8',
                  help='Experiment number [default=7]')
parser.add_option('-r', '--run', dest='rNumber',
                  default='0220',
                  help='Run number [default=0604]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))

RunLocation = "/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/Short-listed/".format(exp, run)

writelatex(RunLocation)
