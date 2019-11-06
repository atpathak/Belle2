from flask import Flask, render_template, request, json, redirect
from ROOT import *
import string
import random
import os
import base64

gROOT.SetBatch()
app = Flask(__name__)
app.template_folder='template'
app.static_folder='static'

file=None

@app.route("/")
def index():
    dirs=[]
    plots=[]
    global file
    file=TFile("MyPhysVal_pion_pt1.root")
    for key in file.GetListOfKeys():
        thisObject=file.Get(key.GetName())
        if isinstance(thisObject,TDirectory):
            dirs.append({'text':key.GetName(),'path':key.GetName()})
        if isinstance(thisObject,TH1) or isinstance(thisObject,TEfficiency):
            plots.append({'text':key.GetName()})
    return render_template('main.html',dirs=dirs,plots=plots)

@app.route("/browse",methods=['POST'])
def browse():
    dirs=[]
    plots=[]
    thispath=str(request.form['path'])
    tree=file.Get(thispath)
    for key in tree.GetListOfKeys():
        thisObject=tree.Get(key.GetName())
        if isinstance(thisObject,TDirectory):
            dirs.append({'text':key.GetName(),'path':thispath+"/"+key.GetName()})
        if isinstance(thisObject,TH1) or isinstance(thisObject,TEfficiency):
            plots.append({'text':key.GetName(),'path':thispath+"/"+key.GetName()})    
    return json.dumps({"dirs":dirs,"plots":plots})

@app.route("/showplot")
def showplot():
    thispath=str(request.args['path'])
    print(thispath)
    plot=file.Get(thispath)
    c=TCanvas()
    plot.Draw()
    randomname="static/tmp/"+''.join(random.choice(string.ascii_uppercase) for _ in range(8))+".png"
    c.SaveAs(randomname)
    f=open(randomname,'rb')
    data=f.read()
    f.close()
    os.remove(randomname)
    return base64.b64encode(data)

app.run()
