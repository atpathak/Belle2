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
using namespace std;
void MyProjecttdc(TTree*tree,TH1*hist,TString var1,TString var2,TString var3,TString var4,TString var5,TString var6,TString var7,int laneval,int axisval){
  Stat_t nevtot=tree->GetEntries();
  //cout << "nevtot = " << nevtot << endl;
  int ifirst=0;
  Int_t myvariable1 ;
  tree->SetBranchAddress(var1,&myvariable1);
  Int_t myvariable2 ;
  tree->SetBranchAddress(var2,&myvariable2);
  Int_t myvariable3 ;
  tree->SetBranchAddress(var3,&myvariable3);
  Int_t myvariable4 ;
  tree->SetBranchAddress(var4,&myvariable4);
  Float_t myvariable5 ;
  tree->SetBranchAddress(var5,&myvariable5);
  Float_t myvariable6 ;
  tree->SetBranchAddress(var6,&myvariable6);
  Float_t myvariable7 ;
  tree->SetBranchAddress(var7,&myvariable7);
  for (unsigned int ievt = ifirst; ievt < ifirst+nevtot; ++ievt) { //Process each event
    //In case of a TChain, ientry is the entry number in the current file
    int ientry = tree->LoadTree(ievt);
    //Read in this event
    tree->GetEntry(ievt);
    bool selection1 = myvariable2 == laneval;
    bool selection2 = myvariable4 == axisval;
    if (selection1 && selection2 ) {
      hist->Fill(myvariable6);
    }
  }
}

void MyProjectmytime(TTree*tree,TH1*hist,TString var1,TString var2,TString var3,TString var4,TString var5,TString var6,TString var7,int laneval,int axisval){
  Stat_t nevtot=tree->GetEntries();
  //cout << "nevtot = " << nevtot << endl;
  int ifirst=0;
  Int_t myvariable1 ;
  tree->SetBranchAddress(var1,&myvariable1);
  Int_t myvariable2 ;
  tree->SetBranchAddress(var2,&myvariable2);
  Int_t myvariable3 ;
  tree->SetBranchAddress(var3,&myvariable3);
  Int_t myvariable4 ;
  tree->SetBranchAddress(var4,&myvariable4);
  Float_t myvariable5 ;
  tree->SetBranchAddress(var5,&myvariable5);
  Float_t myvariable6 ;
  tree->SetBranchAddress(var6,&myvariable6);
  Float_t myvariable7 ;
  tree->SetBranchAddress(var7,&myvariable7);
  for (unsigned int ievt = ifirst; ievt < ifirst+nevtot; ++ievt) { //Process each event
    //In case of a TChain, ientry is the entry number in the current file
    int ientry = tree->LoadTree(ievt);
    //Read in this event
    tree->GetEntry(ievt);
    bool selection1 = myvariable2 == laneval;
    bool selection2 = myvariable4 == axisval;
    if (selection1 && selection2 ) {
      hist->Fill(myvariable5);
    }
  }
}

void MyProjecttdc2(TTree*tree,TH2*hist,TString var1,TString var2,TString var3,TString var4,TString var5,TString var6,TString var7,int laneval,int axisval){
  Stat_t nevtot=tree->GetEntries();
  //cout << "nevtot = " << nevtot << endl;
  int ifirst=0;
  Int_t myvariable1 ;
  tree->SetBranchAddress(var1,&myvariable1);
  Int_t myvariable2 ;
  tree->SetBranchAddress(var2,&myvariable2);
  Int_t myvariable3 ;
  tree->SetBranchAddress(var3,&myvariable3);
  Int_t myvariable4 ;
  tree->SetBranchAddress(var4,&myvariable4);
  Float_t myvariable5 ;
  tree->SetBranchAddress(var5,&myvariable5);
  Float_t myvariable6 ;
  tree->SetBranchAddress(var6,&myvariable6);
  Float_t myvariable7 ;
  tree->SetBranchAddress(var7,&myvariable7);
  for (unsigned int ievt = ifirst; ievt < ifirst+nevtot; ++ievt) { //Process each event
    //In case of a TChain, ientry is the entry number in the current file
    int ientry = tree->LoadTree(ievt);
    //Read in this event
    tree->GetEntry(ievt);
    bool selection1 = myvariable2 == laneval;
    bool selection2 = myvariable4 == axisval;
    if (selection1 && selection2 ) {
      hist->Fill(float(myvariable3),myvariable6);
    }
  }
}

void MyProjectmytime2(TTree*tree,TH2*hist,TString var1,TString var2,TString var3,TString var4,TString var5,TString var6,TString var7,int laneval,int axisval){
  Stat_t nevtot=tree->GetEntries();
  //cout << "nevtot = " << nevtot << endl;
  int ifirst=0;
  Int_t myvariable1 ;
  tree->SetBranchAddress(var1,&myvariable1);
  Int_t myvariable2 ;
  tree->SetBranchAddress(var2,&myvariable2);
  Int_t myvariable3 ;
  tree->SetBranchAddress(var3,&myvariable3);
  Int_t myvariable4 ;
  tree->SetBranchAddress(var4,&myvariable4);
  Float_t myvariable5 ;
  tree->SetBranchAddress(var5,&myvariable5);
  Float_t myvariable6 ;
  tree->SetBranchAddress(var6,&myvariable6);
  Float_t myvariable7 ;
  tree->SetBranchAddress(var7,&myvariable7);
  for (unsigned int ievt = ifirst; ievt < ifirst+nevtot; ++ievt) { //Process each event
    //In case of a TChain, ientry is the entry number in the current file
    int ientry = tree->LoadTree(ievt);
    //Read in this event
    tree->GetEntry(ievt);
    bool selection1 = myvariable2 == laneval;
    bool selection2 = myvariable4 == axisval;
    if (selection1 && selection2 ) {
      hist->Fill(float(myvariable3), myvariable5);
    }
  }
}

int main(int argc, char* argv[]){
  //
  // Argument variables
  //
  //  int imode    = (argc>1) ? atoi(argv[1]) : 0;
  //
  gStyle->SetOptStat(0);
  gStyle->SetOptFit(01);
  
  const int Nlane=6;
  int lane_val[Nlane] = {1,2,8,13,16,20};

  const int Naxis=2;
  int axis_val[Naxis] = {0,1};

  TString v1 = "eventNR"; //!
  TString v2 = "lane";//!
  TString v3 = "channel"; //!
  TString v4 = "axis"; //!
  TString v5 = "mytime";//!
  TString v6 = "tdc";//!
  TString v7 = "charge";//!

  float tdc_max = 2047.;

  float mytime_max = 65535.;

  float channel_max  = 127;
  
  TFile *f = TFile::Open("dblpls_30k_2019801.root");
  TTree *tree= (TTree*)f->Get("ntuple");

  for (int ilbin = 0; ilbin <Nlane; ++ilbin) {
    int laneval = lane_val[ilbin];

    /*
    TH1F*h_tdc_0  =   new TH1F("h_tdc_0", "h_tdc_0", int(tdc_max)+1,0,tdc_max);
    TH1F*h_tdc_1  =   new TH1F("h_tdc_1", "h_tdc_1", int(tdc_max)+1,0,tdc_max);
    
    TH1F*h_tdc_0  =   new TH1F("h_tdc_0", "h_tdc_0", 20,0,tdc_max);
    TH1F*h_tdc_1  =   new TH1F("h_tdc_1", "h_tdc_1", 20,0,tdc_max);
    
    TH2F*h_tdc_channel_0  =   new TH2F("h_tdc_channel_0", "h_tdc_channel_0", int(channel_max)+1,0,channel_max, int(tdc_max)+1,0,tdc_max);
    TH2F*h_tdc_channel_1  =   new TH2F("h_tdc_channel_1", "h_tdc_channel_1", int(channel_max)+1,0,channel_max, int(tdc_max)+1,0,tdc_max);
    
    TH2F*h_tdc_channel_0  =   new TH2F("h_tdc_channel_0", "h_tdc_channel_0", 1,0,channel_max, 2,0,tdc_max);
    TH2F*h_tdc_channel_1  =   new TH2F("h_tdc_channel_1", "h_tdc_channel_1", 1,0,channel_max, 2,0,tdc_max);
    
    TH1F*h_mytime_0  =   new TH1F("h_mytime_0", "h_mytime_0", int(mytime_max)+1,0,mytime_max);
    TH1F*h_mytime_1  =   new TH1F("h_mytime_1", "h_mytime_1", int(mytime_max)+1,0,mytime_max);
    
    TH1F*h_mytime_0  =   new TH1F("h_mytime_0", "h_mytime_0", 655,0,mytime_max);
    TH1F*h_mytime_1  =   new TH1F("h_mytime_1", "h_mytime_1", 655,0,mytime_max);
    
      
    TH2F*h_mytime_channel_0  =   new TH2F("h_mytime_channel_0", "h_mytime_channel_0", int(channel_max)+1,0,channel_max, int(mytime_max)+1,0,mytime_max);
    TH2F*h_mytime_channel_1  =   new TH2F("h_mytime_channel_1", "h_mytime_channel_1", int(channel_max)+1,0,channel_max, int(mytime_max)+1,0,mytime_max);
    
    TH2F*h_mytime_channel_0  =   new TH2F("h_mytime_channel_0", "h_mytime_channel_0", 1,0,channel_max, 65,0,mytime_max);
    TH2F*h_mytime_channel_1  =   new TH2F("h_mytime_channel_1", "h_mytime_channel_1", 1,0,channel_max, 65,0,mytime_max);
    */
    TH1F*h_tdc_0  =   new TH1F("h_tdc_0", "h_tdc_0", (int(tdc_max)+1)/16,0,tdc_max);
    TH1F*h_tdc_1  =   new TH1F("h_tdc_1", "h_tdc_1", (int(tdc_max)+1)/16,0,tdc_max);
    
    TH2F*h_tdc_channel_0  =   new TH2F("h_tdc_channel_0", "h_tdc_channel_0", int(channel_max)+1,0,channel_max, (int(tdc_max)+1)/16,0,tdc_max);
    TH2F*h_tdc_channel_1  =   new TH2F("h_tdc_channel_1", "h_tdc_channel_1", int(channel_max)+1,0,channel_max, (int(tdc_max)+1)/16,0,tdc_max);
    
    TH1F*h_mytime_0  =   new TH1F("h_mytime_0", "h_mytime_0", (int(mytime_max)+1)/16,0,mytime_max);
    TH1F*h_mytime_1  =   new TH1F("h_mytime_1", "h_mytime_1", (int(mytime_max)+1)/16,0,mytime_max);

    TH2F*h_mytime_channel_0  =   new TH2F("h_mytime_channel_0", "h_mytime_channel_0", int(channel_max)+1,0,channel_max, (int(mytime_max)+1)/16,0,mytime_max);
    TH2F*h_mytime_channel_1  =   new TH2F("h_mytime_channel_1", "h_mytime_channel_1", int(channel_max)+1,0,channel_max, (int(mytime_max)+1)/16,0,mytime_max);
    
    
    for (int iabin = 0; iabin <Naxis; ++iabin) {
      int axisval = axis_val[iabin];
      
      if (iabin==0){
	MyProjecttdc(tree,h_tdc_0,v1.Data(),v2.Data(),v3.Data(),v4.Data(),v5.Data(),v6.Data(),v7.Data(),laneval,axisval);
	MyProjectmytime(tree,h_mytime_0,v1.Data(),v2.Data(),v3.Data(),v4.Data(),v5.Data(),v6.Data(),v7.Data(),laneval,axisval);

	MyProjecttdc2(tree,h_tdc_channel_0,v1.Data(),v2.Data(),v3.Data(),v4.Data(),v5.Data(),v6.Data(),v7.Data(),laneval,axisval);
	MyProjectmytime2(tree,h_mytime_channel_0,v1.Data(),v2.Data(),v3.Data(),v4.Data(),v5.Data(),v6.Data(),v7.Data(),laneval,axisval);

      }
      
      if (iabin==1){
	MyProjecttdc(tree,h_tdc_1,v1.Data(),v2.Data(),v3.Data(),v4.Data(),v5.Data(),v6.Data(),v7.Data(),laneval,axisval);
	MyProjectmytime(tree,h_mytime_1,v1.Data(),v2.Data(),v3.Data(),v4.Data(),v5.Data(),v6.Data(),v7.Data(),laneval,axisval);
	
	MyProjecttdc2(tree,h_tdc_channel_1,v1.Data(),v2.Data(),v3.Data(),v4.Data(),v5.Data(),v6.Data(),v7.Data(),laneval,axisval);
	MyProjectmytime2(tree,h_mytime_channel_1,v1.Data(),v2.Data(),v3.Data(),v4.Data(),v5.Data(),v6.Data(),v7.Data(),laneval,axisval);

      }
      
    }

    TCanvas* c1=new TCanvas("c1","c1",400,400);
    if (gPad) gPad->SetLeftMargin(0.15);
    h_tdc_0->SetTitle(Form("tdc (axis: 0) (lane : %d)",laneval));
    h_tdc_0->GetXaxis()->SetTitle("tdc");
    h_tdc_0->GetYaxis()->SetTitle("Number of events");
    h_tdc_0->GetYaxis()->SetTitleOffset(1.6);
    h_tdc_0->GetYaxis()->SetTitleSize(0.05);
    h_tdc_0->Draw("HIST");
    c1->Update();
    c1->SaveAs(Form("Plots/tdc_%d_0.pdf",laneval));
    delete c1;
    c1=0;
    
    TCanvas* c2=new TCanvas("c2","c2",400,400);
    if (gPad) gPad->SetLeftMargin(0.15);
    h_tdc_1->SetTitle(Form("tdc (axis: 1) (lane : %d)",laneval));
    h_tdc_1->GetXaxis()->SetTitle("tdc");
    h_tdc_1->GetYaxis()->SetTitle("Number of events");
    h_tdc_1->GetYaxis()->SetTitleOffset(1.6);
    h_tdc_1->GetYaxis()->SetTitleSize(0.05);
    h_tdc_1->Draw("HIST");
    c2->Update();
    c2->SaveAs(Form("Plots/tdc_%d_1.pdf",laneval));
    delete c2;
    c2=0;

    TCanvas* c3=new TCanvas("c3","c3",400,400);
    if (gPad) gPad->SetLeftMargin(0.15);
    h_mytime_0->SetTitle(Form("ctime (axis: 0) (lane : %d)",laneval));
    h_mytime_0->GetXaxis()->SetTitle("ctime");
    h_mytime_0->GetYaxis()->SetTitle("Number of events");
    h_mytime_0->GetYaxis()->SetTitleOffset(1.6);
    h_mytime_0->GetYaxis()->SetTitleSize(0.05);
    h_mytime_0->Draw("HIST");
    h_mytime_0->GetXaxis()->SetRangeUser(0,12000);
    c3->Update();
    c3->SaveAs(Form("Plots/ctime_%d_0.pdf",laneval));
    delete c3;
    c3=0;
    
    TCanvas* c4=new TCanvas("c4","c4",400,400);
    if (gPad) gPad->SetLeftMargin(0.15);
    h_mytime_1->SetTitle(Form("ctime (axis: 1) (lane : %d)",laneval));
    h_mytime_1->GetXaxis()->SetTitle("ctime");
    h_mytime_1->GetYaxis()->SetTitle("Number of events");
    h_mytime_1->GetYaxis()->SetTitleOffset(1.6);
    h_mytime_1->GetYaxis()->SetTitleSize(0.05);
    h_mytime_1->Draw("HIST");
    h_mytime_1->GetXaxis()->SetRangeUser(0,12000);
    c4->Update();
    c4->SaveAs(Form("Plots/ctime_%d_1.pdf",laneval));
    delete c4;
    c4=0;

    delete h_tdc_0;    h_tdc_0=0;
    delete h_tdc_1;    h_tdc_1=0;

    delete h_mytime_0; h_mytime_0=0;
    delete h_mytime_1; h_mytime_1=0;

    
    
    TCanvas* c1_2=new TCanvas("c1_2","c1_2",400,400);
    if (gPad) gPad->SetLeftMargin(0.15);
    h_tdc_channel_0->SetTitle(Form("tdc (axis: 0) (lane : %d)",laneval));
    h_tdc_channel_0->GetXaxis()->SetTitle("channel");
    h_tdc_channel_0->GetYaxis()->SetTitle("tdc");
    h_tdc_channel_0->GetYaxis()->SetTitleOffset(1.6);
    h_tdc_channel_0->GetYaxis()->SetTitleSize(0.05);
    h_tdc_channel_0->Draw("zcol");
    if(laneval == 2 || laneval == 1 ) {
      h_tdc_channel_0->GetXaxis()->SetRange(50,100);
    } else {
      h_tdc_channel_0->GetXaxis()->SetRange(22,42);
    }
    c1_2->Update();
    c1_2->SaveAs(Form("Plots/tdc_channel_%d_0.pdf",laneval));
    delete c1_2;
    c1_2=0;
    
    TCanvas* c2_2=new TCanvas("c2_2","c2_2",400,400);
    if (gPad) gPad->SetLeftMargin(0.15);
    h_tdc_channel_1->SetTitle(Form("tdc (axis: 1) (lane : %d)",laneval));
    h_tdc_channel_1->GetXaxis()->SetTitle("channel");
    h_tdc_channel_1->GetYaxis()->SetTitle("tdc"); 
    h_tdc_channel_1->GetYaxis()->SetTitleOffset(1.6);
    h_tdc_channel_1->GetYaxis()->SetTitleSize(0.05);
    h_tdc_channel_1->Draw("zcol");
    if(laneval == 2 || laneval == 1) {
      h_tdc_channel_1->GetXaxis()->SetRange(50,100);
    } else {
      h_tdc_channel_1->GetXaxis()->SetRange(22,42);
    }
    c2_2->Update();
    c2_2->SaveAs(Form("Plots/tdc_channel_%d_1.pdf",laneval));
    delete c2_2;
    c2_2=0;

    TCanvas* c3_2=new TCanvas("c3_2","c3_2",400,400);
    if (gPad) gPad->SetLeftMargin(0.15);
    h_mytime_channel_0->SetTitle(Form("ctime (axis: 0) (lane : %d)",laneval));
    h_mytime_channel_0->GetXaxis()->SetTitle("channel");
    h_mytime_channel_0->GetYaxis()->SetTitle("ctime");
    h_mytime_channel_0->GetYaxis()->SetTitleOffset(1.6);
    h_mytime_channel_0->GetYaxis()->SetTitleSize(0.05);
    h_mytime_channel_0->Draw("zcol");
    h_mytime_channel_0->GetYaxis()->SetRangeUser(0,12000);
    if(laneval == 2 || laneval == 1) {
      h_mytime_channel_0->GetXaxis()->SetRange(50,100);
    } else {
      h_mytime_channel_0->GetXaxis()->SetRange(22,42);
    }
    c3_2->Update();
    c3_2->SaveAs(Form("Plots/ctime_channel_%d_0.pdf",laneval));
    delete c3_2;
    c3_2=0;
    
    TCanvas* c4_2=new TCanvas("c4_2","c4_2",400,400);
    if (gPad) gPad->SetLeftMargin(0.15);
    h_mytime_channel_1->SetTitle(Form("ctime (axis: 1) (lane : %d)",laneval));
    h_mytime_channel_1->GetXaxis()->SetTitle("channel");
    h_mytime_channel_1->GetYaxis()->SetTitle("ctime");
    h_mytime_channel_1->GetYaxis()->SetTitleOffset(1.6);
    h_mytime_channel_1->GetYaxis()->SetTitleSize(0.05);
    h_mytime_channel_1->Draw("zcol");
    h_mytime_channel_1->GetYaxis()->SetRangeUser(0,12000);
    if(laneval == 2 || laneval == 1) {
      h_mytime_channel_1->GetXaxis()->SetRange(50,100);
    } else {
      h_mytime_channel_1->GetXaxis()->SetRange(22,42);
    }
    c4_2->Update();
    c4_2->SaveAs(Form("Plots/ctime_channel_%d_1.pdf",laneval));
    delete c4_2;
    c4_2=0;

    delete h_tdc_channel_0;    h_tdc_channel_0=0;
    delete h_tdc_channel_1;    h_tdc_channel_1=0;

    delete h_mytime_channel_0; h_mytime_channel_0=0;
    delete h_mytime_channel_1; h_mytime_channel_1=0;
    

  }
  
  f->Close();
  
  return 0;
}

