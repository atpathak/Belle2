void Draw_tt_ctime(TString s1="dblpls_30k_fine_20190109")
{
  TFile*f = TFile::Open(Form("%s.root",s1.Data()));
  TTree *tree= (TTree*)f->Get("KLM_raw_hits");
  TCanvas*c1=new TCanvas("c1");
  tree->Draw("tt_ctime");
  c1->SaveAs(Form("%s_tt_ctime.png",s1.Data()));
}
