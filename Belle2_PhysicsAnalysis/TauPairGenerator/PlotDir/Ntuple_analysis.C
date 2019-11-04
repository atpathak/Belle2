#include "TH1.h"
#include "TFile.h"
#include "TString.h"
#include <string>
#include <iostream>
#include <fstream>
#include <stdlib.h>     /* atof */
#include "TROOT.h"
#include "TStyle.h"
#include "TMath.h"
#include "TF1.h"
#include "TH2.h"
#include "TCanvas.h"
#include "TSystem.h"
#include "TGraphErrors.h"
#include "TFrame.h"
#include <TPaveStats.h>
#include "TAttText.h"
#include "TMultiGraph.h"
#include "TChain.h"
#include "TTree.h"
#include "TLatex.h"
#include <TCut.h>
#include <TLegend.h>

void Ntuple_analysis(){
    TFile *f = new TFile("../tau_Generator_analysis_test.root");
    TTree *t1 = (TTree*)f->Get("tree");
    Double_t tauPlusMCMode;
    Double_t tauMinusMCMode;
    t1->SetBranchAddress("tauPlusMCMode",&tauPlusMCMode);
    t1->SetBranchAddress("tauMinusMCMode",&tauMinusMCMode);
    
    TH1F *h_tauPlus   =   new TH1F("h_tauPlus", "tau Plus Decays", 100,0,50);
    TH1F *h_tauMinus  =   new TH1F("h_tauMinus", "tau Minus Decays", 100,0,50);
    
    Int_t nentries = (Int_t)t1->GetEntries();
    for (Int_t i=0; i<nentries; i++) {
        t1->GetEntry(i);
        h_tauPlus->Fill(tauPlusMCMode);
        h_tauMinus->Fill(tauMinusMCMode);
    }
    
    TCanvas* c1=new TCanvas("c1","c1",400,400);
    h_tauPlus->GetXaxis()->SetTitle("tau Plus decay modes");
    h_tauPlus->GetYaxis()->SetTitle("Number of events");
    h_tauPlus->Draw();
    c1->Update();
    c1->SaveAs("tauPlusMCMode.pdf");
    delete c1;
    c1=0;
    
    TCanvas* c2=new TCanvas("c2","c2",400,400);
    h_tauMinus->GetXaxis()->SetTitle("tau Minus decay modes");
    h_tauMinus->GetYaxis()->SetTitle("Number of events");
    h_tauMinus->Draw();
    c2->Update();
    c2->SaveAs("tauMinusMCMode.pdf");
    delete c2;
    c2=0;
    
    
}







