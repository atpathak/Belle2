function draw_histo(name,id,copt,hopt,tprefix) {
	name=name.replace("[","_");
	name=name.replace("]","_");
	JSROOT.NewHttpRequest(name, 'object', function(obj) {
		if (!obj) {
			document.getElementById(id).innerHTML="<h3>Can not get " + name + "</h3>";
			return;
		}
		if (copt=="logy")
			obj.fLogy=1;
		if (hopt!="") {
			obj.fPrimitives.arr[1].fOption=hopt;
		}
		obj.fPrimitives.arr[1].fTitle=tprefix+obj.fPrimitives.arr[1].fTitle;
		JSROOT.cleanup(id);
		JSROOT.redraw(id, obj,copt);
	}).send();
}

function update_info() {
	var type='/'+JSROOT.GetUrlOption("type")+'/';
	var jsonfile=JSROOT.GetUrlOption("jsonfile");
	var title=""
	if (jsonfile!=null) {
		jsonfile=jsonfile.split('/');
		title=jsonfile[jsonfile.length-1].split('.')[0];
	}
	JSROOT.NewHttpRequest(type+'DQMInfo/c_info/root.json', 'object', function(obj) {
		document.getElementById("info").innerHTML="<h5>"+"<font color=\"red\">"+title+"</font>"+"     "+obj.fTitle+", Release 03-01-04</h5>";
			}).send();
}

function update_histos(inputs,type) {
	suffix='/root.json';
	ilen=inputs.length;
	for (i=0;i<ilen;i++) {
		if (inputs[i].length<3)
			draw_histo(type+inputs[i][0]+suffix,inputs[i][1],"","","");
		else if (inputs[i].length==3)
			draw_histo(type+inputs[i][0]+suffix,inputs[i][1],inputs[i][2],"","");
		else if (inputs[i].length==4)
			draw_histo(type+inputs[i][0]+suffix,inputs[i][1],inputs[i][2],inputs[i][3],"");
		else if (inputs[i].length==5)
			draw_histo(type+inputs[i][0]+suffix,inputs[i][1],inputs[i][2],inputs[i][3],inputs[i][4]+": ");
	}
	update_info();
}

function parse_json(obj) {
	var type='/'+JSROOT.GetUrlOption("type")+'/';
	var cssfile=obj.cssfile;
	var histos=obj.histos;
	var fileref=document.createElement("link");
	fileref.setAttribute("rel", "stylesheet");
	fileref.setAttribute("type", "text/css");
	fileref.setAttribute("href", "css/"+cssfile);
	document.getElementsByTagName("head")[0].appendChild(fileref);
	for (j in histos) {
		document.getElementById("wrapper").innerHTML += "<div class=" + histos[j][1] + " id=" + histos[j][1] + "></div>\n";
	}
	update_histos(histos,type);
	setInterval(function() { update_histos(histos,type); }, 20000);
}

function page_load(jfile="") {
	var jsonfile=jfile;
	if (jsonfile=="")
		jsonfile=JSROOT.GetUrlOption("jsonfile");
	if (jsonfile==null) return;
	JSROOT.NewHttpRequest(jsonfile,'object',function(obj) {
		if (!obj) {
			return;
		}
		parse_json(obj);
	}).send();
}

function update_dir(dirname,cssfile,limit,prefix) {
	JSROOT.NewHttpRequest(dirname+'/root.json','object',function(dir) {
		if (!dir) {
			return;
		}
		var list_of_obj=dir.fFolders.arr;
		var n=list_of_obj.length;
		var type='/'+JSROOT.GetUrlOption("type")+'/';

		var fileref=document.createElement("link");
		fileref.setAttribute("rel", "stylesheet");
		fileref.setAttribute("type", "text/css");
		fileref.setAttribute("href", "css/"+cssfile);
		document.getElementsByTagName("head")[0].appendChild(fileref);

		var count=0;
		var histos=[];
		for (var i=0; i<n; i++) {
			var obj=list_of_obj[i];
			var name=obj.fName;
			if (prefix!=null && name.match(new RegExp('^'+prefix)) == null) continue;
			var canvas="canvas";
			if (count+1<10) canvas+=('0'+(count+1).toString());
			else canvas+=(count+1).toString();
			document.getElementById("wrapper").innerHTML += "<div class=" + canvas + " id=" + canvas + "></div>\n";
			histos.push([dirname+'/'+name,canvas]);
			count+=1;
			if (count==limit) break;
		}
		update_histos(histos,type);
		setInterval(function() { update_histos(histos,type); }, 20000);
	}).send();
}

function dir_load() {
	var dirname=JSROOT.GetUrlOption("directory");
	var cssfile=JSROOT.GetUrlOption("layout");
	var limit=JSROOT.GetUrlOption("limit");
	var prefix=JSROOT.GetUrlOption("prefix");
	if (cssfile==null) cssfile="grid3x4.css";
	if (limit==null) limit=12;

	update_dir(dirname,cssfile,limit,prefix);
}

function make_index() {
	var jsonfile=JSROOT.GetUrlOption("jsonfile");
	if (jsonfile==null) return;
	if (jsonfile[0]=='/') jsonfile=jsonfile.substring(1,jsonfile.length);
	var item=(jsonfile.split('/')[1]).split('.')[0];
	document.getElementById(item).classList.add('w3-black');
}

function parse_json_image(obj) {
	var type=JSROOT.GetUrlOption("type");
	var dirname=JSROOT.GetUrlOption("dirname");
	//if (type=='hlt') dirname="HLT";
	//else if (type=="reco") dirname="ExpressReco";
	//else return;
	var cssfile=obj.cssfile;
	var histos=obj.histos;
	var fileref=document.createElement("link");
	fileref.setAttribute("rel", "stylesheet");
	fileref.setAttribute("type", "text/css");
	fileref.setAttribute("href", "/css/"+cssfile);
	document.getElementsByTagName("head")[0].appendChild(fileref);
	for (j in histos) {
		var subname=histos[j][0].split('/')[0];
		var name=histos[j][0].split('/')[1];
		var hname=name.substring(2,name.length);
		hname=hname.replace('v_','');
		document.getElementById("wrapper").innerHTML += "<div class=" + histos[j][1] + " id=" + histos[j][1] + "><img src=\"/history/"+dirname+"/"+subname+"_"+hname+".png\"></div>\n";
	}
	//update_histos(histos,type);
	//setInterval(function() { update_histos(histos,type); }, 20000);
}

function image_load() {
	var jsonfile=JSROOT.GetUrlOption("jsonfile");
	if (jsonfile==null) return;
	JSROOT.NewHttpRequest(jsonfile,'object',function(obj) {
		if (!obj) {
			return;
		}
		parse_json_image(obj);
	}).send();

}
