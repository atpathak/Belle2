var root_file;

function draw_histo(name,id,copt,hopt,tprefix) {
	dirname=name.split('/')[0];
	histoname=name.split('/')[1];
	if (histoname.startsWith('c_')) histoname=histoname.substring(2,histoname.length);
	fullname=dirname+'/'+histoname;
	root_file.ReadObject(fullname, function(obj) {
		if (obj==null) {
			document.getElementById(id).innerHTML = "Can't find " + name;
			return;
		}
		//console.log("draw directly " + fullname);
		if (fullname.startsWith('RawKLM')) {
			//console.log(" hey " + id)
			if (obj._typename.startsWith('TH1')) {
				if (id.endsWith('02')) {
					JSROOT.redraw(id, obj, 'hist');
				}
				else {
					//if (copt=="logy")
					//var ymin = .fMinimum;
					JSROOT.redraw(id, obj, 'logy');
					//var stac = obj.fHistogram;
					//console.log(" ymin :" +ymin)
				}
			}
                	else if (obj._typename.startsWith('TH2'))
                        	JSROOT.redraw(id, obj, 'colz');
		}
		else {
			if (obj._typename.startsWith('TH1'))
				JSROOT.redraw(id, obj, 'hist');
			else if (obj._typename.startsWith('TH2'))
				JSROOT.redraw(id, obj, 'colz');
		}
	});
}

function update_histos(inputs) {
	prefix='';
	suffix='';
	ilen=inputs.length;
	for (i=0;i<ilen;i++) {
		if (inputs[i][3] == 'RawKLM/NRawKLM') {
			draw_histo(prefix+'RawKLM/NRawKLM'+suffix,inputs[i][3],"hist","hist","hist");
		} else if (inputs[i][0] == 'BKLM/c_xvsz_bklm') {
			draw_histo(prefix+'BKLM/c_xvsz'+suffix,inputs[i][1]);
		} else {
			draw_histo(prefix+inputs[i][0]+suffix,inputs[i][1]);
		}
		//if (inputs[i].length<3)
		//	draw_histo(prefix+inputs[i][0]+suffix,inputs[i][1],"","","");
		//else if (inputs[i].length==3)
		//	draw_histo(prefix+inputs[i][0]+suffix,inputs[i][1],inputs[i][2],"","");
		//else if (inputs[i].length==4)
		//	draw_histo(prefix+inputs[i][0]+suffix,inputs[i][1],inputs[i][2],inputs[i][3],"");
		//else if (inputs[i].length==5)
		//	draw_histo(prefix+inputs[i][0]+suffix,inputs[i][1],inputs[i][2],inputs[i][3],inputs[i][4]+": ");
	}
}

function parse_json(obj) {
	var cssfile=obj.cssfile;
	var histos=obj.histos;
	var page_head = document.getElementsByTagName("head")[0];
	var head_len = page_head.childNodes.length;
	for (var i = 0; i< head_len; i++) {
		if (page_head.childNodes[i].nodeName == 'LINK' && page_head.childNodes[i].getAttribute('type') == 'text/css') {
			css_name = page_head.childNodes[i].getAttribute('href');
			if (css_name.startsWith('/css/')) {
				page_head.removeChild(page_head.childNodes[i]);
				break;
			}
		}
	}
	var fileref=document.createElement("link");
	fileref.setAttribute("rel", "stylesheet");
	fileref.setAttribute("type", "text/css");
	fileref.setAttribute("href", "/klm/css/"+cssfile);
	document.getElementsByTagName("head")[0].appendChild(fileref);
	document.getElementById("wrapper").innerHTML = ""; //'<div> <button class="openbtn" onclick="openNav()">☰ </button> </div>\n';
	for (j in histos) {
		document.getElementById("wrapper").innerHTML += '<div class=' + histos[j][1] + ' id=' + histos[j][1] + '></div>\n';
	}
	update_histos(histos);
}

function page_load(jfile) {
	var jsonfile=jfile;

	if (jsonfile==null) return;
	JSROOT.NewHttpRequest(jsonfile,'object',function(obj) {
		if (!obj) {
			return;
		}
		parse_json(obj);
		var item_id=(jsonfile.split('/')[1]).split('.')[0];
		make_index(item_id);
	}).send();
}

function page_initialize(name="") {
	var rootfile=name;
	if (rootfile=="")
		rootfile=JSROOT.GetUrlOption("rootfile");

	JSROOT.OpenFile(rootfile, function(file) {
		root_file = file;
	});
}

function build_menu(index_json="") {
	if (index_json==null) return;
	JSROOT.NewHttpRequest(index_json,'object',function(obj) {
		if (!obj) {
			return;
		}
		//parse_json(obj);
		items = obj.items;
		menu = document.getElementById('menu');
		filename=JSROOT.GetUrlOption("rootfile");
		runno = filename.replace('#','').split('/').reverse()[0].split('.')[0].split('r')[1];
		while (runno[0]=='0') {
			runno = runno.substring(1,runno.length);
		}
		//menu.innerHTML += '<font color="red">Run: 3123 </font><br/>\n';
		menu.innerHTML += '<font color="red">Run: ' + runno +'</font><br/>\n';
		for (var i=0; i<items.length; i++) {
			var item=items[i];
			if (item.dir != null) {
				menu.innerHTML += item.dir+'<br/>\n';
				for (var j=0; j<item.items.length; j++) {
					var subitem = item.items[j];
					menu.innerHTML += '<a href="#" onclick=myFunction();page_load("/' + subitem.jsonfile + '") id="' + subitem.jsonfile.split('.')[0].split('/')[1] + '" class="w3-bar-item w3-button tablink">' + subitem.title + '</a><br/>\n';
				}
			} else {
					menu.innerHTML += '<a href="#" onclick=myFunction();page_load("/' + item.jsonfile + '") id="' + item.jsonfile.split('.')[0].split('/')[1] + '" class="w3-bar-item w3-button tablink">' + item.title + '</a><br/>\n';
			}
		}
	}).send();
}
function myFunction() {
  //var element = document.getElementById("phase3");
  //element.classList.add("active");
 //var btns = element.getElementsByTagName("a");
 // console.log("btns length:" +btns.length) 
// for (var i = 0; i < 4; i++) {
	//console.log("btns:" +btns[i])
	//var current = document.getElementsByClassName("active");
	//current[0].className = current[0].className.replace(" active", "");
	//this.className += " active";
//}
 // var current = document.getElementsByClassName("active");
  //current[0].className = current[0].className.replace(" active", "");
  //this.className += " active";
 // var btns = header.getElementsByClassName("w3-button");
 // consol.log(btns.length);
	var header = document.getElementById("phase3");
	var btns = document.getElementsByClassName("tablink");
	//console.log(btns);
	for (var i = 0; i < btns.length; i++) {
  		btns[i].addEventListener("click", function() {
 		 var current = document.getElementsByClassName("w3-green");
 		 if (current.length > 0) { 
    			current[0].className = current[0].className.replace(" w3-green", "");
 		 }
  		this.className += " w3-green";
  		});
	}

}

function mypropagation() {
	var container = document.querySelector('testing');

	container.addEventListener('click', function(e) {
  	if (e.target != e.currentTarget) {
    		e.preventDefault();
    		// e.target is the image inside the link we just clicked.
 	 }
 	 e.stopPropagation();
	}, false);
}

function make_index(id_name) {
	var all_links = document.getElementsByTagName("a");
	for (var i=0; i<all_links.length; i++) {
		var link = all_links[i];
		if (link.id == id_name) {
			document.getElementById(link.id).classList.add('w3-black');
		} else {
			document.getElementById(link.id).classList.remove('w3-black');
		}
	}
}
