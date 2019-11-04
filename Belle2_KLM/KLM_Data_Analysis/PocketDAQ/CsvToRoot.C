#include "Riostream.h"
#include "TFile.h"
#include "TNtuple.h"
#include "TSystem.h"
#include "TH1.h"
#include "TString.h"
#include <string>
#include <iostream>
#include <fstream>
#include <stdlib.h>     /* atof */
#include "TROOT.h"
#include "TStyle.h"
#include "TMath.h"
#include "TF1.h"
#include "TCanvas.h"
#include "TSystem.h"
#include "TGraphErrors.h"
#include "TFrame.h"
#include <TPaveStats.h>
#include "TAttText.h"
#include "TMultiGraph.h"

void CsvToRoot() {
  TString dir = gSystem->UnixPathName(__FILE__);
  dir.ReplaceAll("CsvToRoot.C","");
  dir.ReplaceAll("/./","/");
  ifstream in;
  in.open(Form("%stest.csv",dir.Data()));
   //in.open("test.csv");
   
   Int_t axis;
   double eventNR,lane,channel,ctime,tdc,charge;
   Int_t nlines = 0;
   TFile *f = new TFile("CsvToRoot.root","RECREATE");
   TTree *tree = new TTree("ntuple","data from csv file");

   tree->Branch("eventNR",&eventNR,"eventNR/D");
   tree->Branch("lane",&lane,"lane/D");
   tree->Branch("channel",&channel,"channel/D");
   tree->Branch("axis",&axis,"axis/I");
   tree->Branch("ctime",&ctime,"ctime/D");
   tree->Branch("tdc",&tdc,"tdc/D");
   tree->Branch("charge",&charge,"charge/D");

   while (1) {
      in >> eventNR >> lane >> channel >> axis >> ctime >> tdc >> charge;
      if (!in.good()) break;
      tree->Fill();
      nlines++;
   }

   in.close();

   f->Write();
}
