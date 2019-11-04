all : dblpls_30k_2019801 
dblpls_30k_2019801: dblpls_30k_2019801.cc
	g++ -g -O2 -fPIC -Wno-deprecated -D__USE_XOPEN2K8 -o dblpls_30k_2019801 dblpls_30k_2019801.cc `root-config --cflags --libs --ldflags` -L${ROOTSYS}/lib -lHistFactory -lXMLParser -lRooStats -lRooFit -lRooFitCore -lThread -lMinuit -lFoam -lMathMore -lHtml -lGpad -lm
clean: 
	rm -f dblpls_30k_2019801
