all : Ntuple_analysis
Ntuple_analysis: Ntuple_analysis.cc
	g++ -g -O2 -fPIC -Wno-deprecated -D__USE_XOPEN2K8 -o Ntuple_analysis Ntuple_analysis.cc `root-config --cflags --libs --ldflags` -L${ROOTSYS}/lib -lHistFactory -lXMLParser -lRooStats -lRooFit -lRooFitCore -lThread -lMinuit -lFoam -lMathMore -lHtml -lGpad -lm
clean:
	rm -f Ntuple_analysis
