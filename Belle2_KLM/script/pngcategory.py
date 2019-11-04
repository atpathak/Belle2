import ROOT
from ROOT import Belle2, TH1, TH2, TCanvas, THistPainter, TPad, gROOT, gStyle, TFile  
import os
import sys
import subprocess
from optparse import Option, OptionValueError, OptionParser


#BKLMCategory = ["RawKLMs", "RawKLM_Sector_channelMultiplicity","mappedSectoroccupancy","mappedChannelOccupancy","mappedRPCTime","mappedRPCTime_Sector","mappedScintCtime","mappedScintCtime_Sector", "RPC_occupancy"]

BKLMCategory = ["RawKLMs", "mappedSectoroccupancy", "mappedRPCTime", "mappedScintCtime", "RPC_occupancy"]

klmraw = ["NDigit", "NRawKLM", "RawKLMnodeID"] #["RawKLMnumEvents", "RawKLMnumNodes", "RawKLMnodeID", "rawKLMlaneFlag", "rawKLMtdcExtraRPC", "rawKLMtdcExtraScint"]
 
#klmrawchannelMultiplicity = ['rawKLM_S00_channelMultiplicity', 'rawKLM_S01_channelMultiplicity', 'rawKLM_S02_channelMultiplicity', 'rawKLM_S03_channelMultiplicity', 'rawKLM_S04_channelMultiplicity', 'rawKLM_S05_channelMultiplicity', 'rawKLM_S06_channelMultiplicity', 'rawKLM_S07_channelMultiplicity', 'rawKLM_S08_channelMultiplicity', 'rawKLM_S09_channelMultiplicity', 'rawKLM_S10_channelMultiplicity', 'rawKLM_S11_channelMultiplicity', 'rawKLM_S12_channelMultiplicity', 'rawKLM_S13_channelMultiplicity', 'rawKLM_S14_channelMultiplicity', 'rawKLM_S15_channelMultiplicity']

mapSectoccu = ["mappedRPCSectorOccupancy","unmappedRPCSectorOccupancy","mappedScintSectorOccupancy","unmappedScintSectorOccupancy"]

#mapChanOccu = ['mappedChannelOccupancy_S00PhiPrompt', 'mappedChannelOccupancy_S00ZPrompt', 'mappedChannelOccupancy_S01PhiPrompt', 'mappedChannelOccupancy_S01ZPrompt', 'mappedChannelOccupancy_S02PhiPrompt', 'mappedChannelOccupancy_S02ZPrompt', 'mappedChannelOccupancy_S03PhiPrompt', 'mappedChannelOccupancy_S03ZPrompt', 'mappedChannelOccupancy_S04PhiPrompt', 'mappedChannelOccupancy_S04ZPrompt', 'mappedChannelOccupancy_S05PhiPrompt', 'mappedChannelOccupancy_S05ZPrompt', 'mappedChannelOccupancy_S06PhiPrompt', 'mappedChannelOccupancy_S06ZPrompt', 'mappedChannelOccupancy_S07PhiPrompt', 'mappedChannelOccupancy_S07ZPrompt', 'mappedChannelOccupancy_S08PhiPrompt', 'mappedChannelOccupancy_S08ZPrompt', 'mappedChannelOccupancy_S09PhiPrompt', 'mappedChannelOccupancy_S09ZPrompt', 'mappedChannelOccupancy_S10PhiPrompt', 'mappedChannelOccupancy_S10ZPrompt', 'mappedChannelOccupancy_S11PhiPrompt', 'mappedChannelOccupancy_S11ZPrompt', 'mappedChannelOccupancy_S12PhiPrompt', 'mappedChannelOccupancy_S12ZPrompt', 'mappedChannelOccupancy_S13PhiPrompt', 'mappedChannelOccupancy_S13ZPrompt', 'mappedChannelOccupancy_S14PhiPrompt', 'mappedChannelOccupancy_S14ZPrompt', 'mappedChannelOccupancy_S15PhiPrompt', 'mappedChannelOccupancy_S15ZPrompt']

RPCTime = ['mappedRPCTime', 'mappedRPCTimeCal', 'mappedRPCTimeBySector'] #['mappedRPCTimeCal2', 'mappedRPCTimeBySector', 'unmappedRPCTime', 'unmappedRPCTimeBySector'] ##'mappedRPCTimeCalBySector', 


#SectorRPCTime = ["mappedRPCTime_S00","mappedRPCTime_S01","mappedRPCTime_S02", "mappedRPCTime_S03", "mappedRPCTime_S04", "mappedRPCTime_S05", "mappedRPCTime_S06", "mappedRPCTime_S07", "mappedRPCTime_S08", "mappedRPCTime_S09", "mappedRPCTime_S10", "mappedRPCTime_S11", "mappedRPCTime_S12", "mappedRPCTime_S13", "mappedRPCTime_S14", "mappedRPCTime_S15"]


ScintCtime = [ 'mappedScintCtime', 'mappedScintCtime0', 'mappedScintCtimeBySector'] #['unmappedScintCtime', 'mappedScintCtimeBySector',  'unmappedScintCtimeBySector'] ##'mappedScintCtime1','mappedScintCtimeCalBySector'

#SectorScintCtime = ["mappedScintCtime_S00","mappedScintCtime_S01","mappedScintCtime_S02", "mappedScintCtime_S03", "mappedScintCtime_S04", "mappedScintCtime_S05", "mappedScintCtime_S06", "mappedScintCtime_S07", "mappedScintCtime_S08", "mappedScintCtime_S09", "mappedScintCtime_S10", "mappedScintCtime_S11", "mappedScintCtime_S12", "mappedScintCtime_S13", "mappedScintCtime_S14", "mappedScintCtime_S15"]


occupancyrpc = ["occupancyBackwardXYPromptBkgd","occupancyForwardXYPromptBkgd"] #[, "occupancyBackwardXYPrompt","occupancyBackwardXYBkgd", "occupancyForwardXYPrompt", "occupancyForwardXYBkgd",]

def makecategory(RunLocation):
    os.chdir(RunLocation)

    for i in BKLMCategory:
        if not os.path.exists(i):
            os.mkdir(i)

    for i in klmraw:
        if os.path.exists(i+".png"):
            os.system("mv "+i+".png RawKLMs/")

    #for i in klmrawchannelMultiplicity:
     #   if os.path.exists(i+".png"):
      #      os.system("mv "+i+".png RawKLM_Sector_channelMultiplicity/")

    for i in mapSectoccu:
        if os.path.exists(i+".png"):
            os.system("mv "+i+".png mappedSectoroccupancy/")

    #for i in mapChanOccu:
     #   if os.path.exists(i+".png"):
      #      os.system("mv "+i+".png mappedChannelOccupancy/")

    for i in RPCTime:
        if os.path.exists(i+".png"):
            os.system("mv "+i+".png mappedRPCTime/")

    #for i in SectorRPCTime:
     #   if os.path.exists(i+".png"):
      #      os.system("mv "+i+".png mappedRPCTime_Sector/")

    for i in ScintCtime:
        if os.path.exists(i+".png"):
            os.system("mv "+i+".png mappedScintCtime/")

    #for i in SectorScintCtime:
     #   if os.path.exists(i+".png"):
      #      os.system("mv "+i+".png mappedScintCtime_Sector/")

    for i in occupancyrpc:
        if os.path.exists(i+".png"):
            os.system("mv "+i+".png RPC_occupancy/")
        

def writehtml(RunLocation):
    header = r'''<!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    body {font-family: Arial, Helvetica, sans-serif;}

    #myImg {
    border-radius: 5px;
    cursor: pointer;
    transition: 0.3s;
    }

    #myImg:hover {opacity: 0.7;}

    /* The Modal (background) */
    .modal {
    display: none; /* Hidden by default */
    position: fixed; /* Stay in place */
    z-index: 1; /* Sit on top */
    padding-top: 100px; /* Location of the box */
    left: 0;
    top: 0;
    width: 100%; /* Full width */
    height: 100%; /* Full height */
    overflow: auto; /* Enable scroll if needed */
    background-color: rgb(0,0,0); /* Fallback color */
    background-color: rgba(0,0,0,0.9); /* Black w/ opacity */
    }

    /* Modal Content (image) */
    .modal-content {
    margin: auto;
    display: block;
    width: 80%;
    max-width: 700px;
    }

    /* Caption of Modal Image */
    #caption {
    margin: auto;
    display: block;
    width: 80%;
    max-width: 700px;
    text-align: center;
    color: #ccc;
    padding: 10px 0;
    height: 150px;
    }

    /* Add Animation */
    .modal-content, #caption {
    -webkit-animation-name: zoom;
    -webkit-animation-duration: 0.6s;
    animation-name: zoom;
    animation-duration: 0.6s;
    }

    @-webkit-keyframes zoom {
    from {-webkit-transform:scale(0)}
    to {-webkit-transform:scale(1)}
    }

    @keyframes zoom {
    from {transform:scale(0)}
    to {transform:scale(1)}
    }

    /* The Close Button */
    .close {
    position: absolute;
    top: 15px;
    right: 35px;
    color: #f1f1f1;
    font-size: 40px;
    font-weight: bold;
    transition: 0.3s;
    }

    .close:hover,
    .close:focus {
    color: #bbb;
    text-decoration: none;
    cursor: pointer;
    }

    /* 100% Image Width on Smaller Screens */
    @media only screen and (max-width: 700px){
    .modal-content {
    width: 100%;
    }
}
    </style>
    </head>
    <body>
'''
    footer = r'''<!-- The Modal -->
    <div id="myModal" class="modal">
    <span class="close">&times;</span>
    <img class="modal-content" id="img01">
    <div id="caption"></div>
    </div>

    <script>
    // Get the modal
    var modal = document.getElementById("myModal");

    // Get the image and insert it inside the modal - use its "alt" text as a caption
    var img = document.getElementById("myImg");
    var modalImg = document.getElementById("img01");
    var captionText = document.getElementById("caption");

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
    modal.style.display = "none";
    }
    // add the class 'imageToPopup' to all img elements you want to trigger the popup modal
    var imgArray = document.getElementsByClassName('imageToPopup');

    // Here we loop through ther array of img elements selected by class name and add an onclick event listener to each.
    for(var i = 0; i<imgArray.length; i++){
        imgArray[i].onclick = function(){
             modal.style.display = "block";
             modalImg.src = this.src;
             captionText.innerHTML = this.alt;
    }
}
    </script>

    </body>
    </html>
'''
    return header, footer

def makehtml(RunLocation):

    os.chdir(RunLocation)

    header, footer = writehtml(RunLocation)

    for i in BKLMCategory:
        
        os.chdir(RunLocation+"/"+i)
        filehtml = open("index.html",'w')

        if i is 'RawKLMs':
            Namehtml = ''
            for j in klmraw:
                Namehtml += "<img class='imageToPopup' src='"+j+".png' width='25%'></img>"

            content = header + Namehtml + footer
            filehtml.write(content)

        #if i is 'RawKLM_Sector_channelMultiplicity':
         #   Namehtml = ''
          #  for j in klmrawchannelMultiplicity:
           #     Namehtml += "<img class='imageToPopup' src='"+j+".png' width='25%'></img>"

            #content = header + Namehtml + footer
            #filehtml.write(content)

        if i is 'mappedSectoroccupancy':
            Namehtml = ''
            for j in mapSectoccu:
                Namehtml += "<img class='imageToPopup' src='"+j+".png' width='25%'></img>"

            content = header + Namehtml + footer
            filehtml.write(content)

        #if i is 'mappedChannelOccupancy':
         #   Namehtml = ''
          #  for j in mapChanOccu:
           #     Namehtml += "<img class='imageToPopup' src='"+j+".png' width='25%'></img>"

            #content = header + Namehtml + footer
            #filehtml.write(content)

        if i is 'mappedRPCTime':
            Namehtml = ''
            for j in RPCTime:
                Namehtml += "<img class='imageToPopup' src='"+j+".png' width='25%'></img>"

            content = header + Namehtml + footer
            filehtml.write(content)

        #if i is 'mappedRPCTime_Sector':
         #   Namehtml = ''
          #  for j in SectorRPCTime:
           #     Namehtml += "<img class='imageToPopup' src='"+j+".png' width='25%'></img>"

            #content = header + Namehtml + footer
            #filehtml.write(content)

        if i is 'mappedScintCtime':
            Namehtml = ''
            for j in ScintCtime:
                Namehtml += "<img class='imageToPopup' src='"+j+".png' width='25%'></img>"

            content = header + Namehtml + footer
            filehtml.write(content)

        #if i is 'mappedScintCtime_Sector':
         #   Namehtml = ''
          #  for j in SectorScintCtime:
           #     Namehtml += "<img class='imageToPopup' src='"+j+".png' width='25%'></img>"

            #content = header + Namehtml + footer
            #filehtml.write(content)

        if i is 'RPC_occupancy':
            Namehtml = ''
            for j in occupancyrpc:
                Namehtml += "<img class='imageToPopup' src='"+j+".png' width='25%'></img>"

            content = header + Namehtml + footer
            filehtml.write(content)

                
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
                  default='0133',
                  help='Run number [default=0604]')
(options, args) = parser.parse_args()
exp = '{0:04d}'.format(int(options.eNumber))
run = '{0:05d}'.format(int(options.rNumber))
runhit = '{0:04d}'.format(int(options.rNumber))

pngdir = '/ghi/fs01/belle2/bdata/group/detector/BKLM/Run_Analysis/e{0}/bklmroots/r{1}/png-e{0}r{1}/'.format(exp, run)
#pngdir = '/home/belle2/atpathak/ppcc2018/work/KLM_16Apr2019/png-e0008r01772/'
makecategory(pngdir)
makehtml(pngdir)
