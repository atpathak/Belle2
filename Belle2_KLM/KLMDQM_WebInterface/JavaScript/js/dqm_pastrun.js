var root_file;
var ref_file;
var canvas_file;

function draw_canvas(name, id) {
	canvas_file.ReadObject(name, function(obj) {
		if (!obj) return;
		JSROOT.draw(id, obj);
	});
}

//function draw_histo(name,id,copt,hopt,tprefix) {
//	dirname=name.split('/')[0];
//	histoname=name.split('/')[1];
//	if (histoname.startsWith('c_')) histoname=histoname.substring(2,histoname.length);
//	fullname=dirname+'/'+histoname;
//	root_file.ReadObject(fullname, function(obj) {
//		if (obj==null) {
//			document.getElementById(id).innerHTML = "Can't find " + name;
//			return;
//		}
//		if (obj._typename.startsWith('TH1'))
//			JSROOT.redraw(id, obj, 'hist');
//		else if (obj._typename.startsWith('TH2'))
//			JSROOT.redraw(id, obj, 'colz');
//	});
//}

function draw_histo(name,id,copt="",hopt="",tprefix="") {
	var dirname=name.split('/')[0];
	var histoname=name.split('/')[1];
	if (histoname.startsWith('c_')) histoname=histoname.substring(2,histoname.length);
	//if (histoname='hitsPerEvent_top') histoname='hitsPerEvent'
	//if (histoname='xvsz_bklm') histoname='xvsz'
	var fullname=dirname+'/'+histoname;
	var ref_fullname='ref/'+dirname+'/'+histoname;

	root_file.ReadObject(fullname, function(obj) {
		if (!obj) {
			draw_canvas(name,id);
			return;
		}

		if (obj._typename.startsWith('TH1')) {

			ref_file.ReadObject(ref_fullname, function(obj_ref) {
				if (!obj_ref || obj_ref.fEntries == 0) {
					JSROOT.redraw(id, obj, 'hist');
					//console.log("draw directly " + fullname);
					return;
				}
				var fac=obj.fEntries/obj_ref.fEntries;
				var max0=0;
				var max1=0;
				for (var ix=0; ix<=obj_ref.fNcells; ix++) {
					var val = obj_ref.getBinContent(ix)*fac;
					obj_ref.setBinContent(ix, val);
					if (obj.getBinContent(ix) > max0) max0 = obj.getBinContent(ix);
					if (val > max1) max1 = val;
				}
				obj_ref.fLineColor = 3;
				obj_ref.fLineStyle = 2;
				obj_ref.fTitle = obj.fTitle;
				if (max1 > max0) {
					JSROOT.draw(id, obj_ref, 'hist');
					JSROOT.draw(id, obj, 'same');
				} else {
					JSROOT.draw(id, obj, 'hist');
					JSROOT.draw(id, obj_ref, 'same');
				}
			});
		} else if (obj._typename.startsWith('TH2')) {
			JSROOT.redraw(id, obj, 'colz');
		}
	});
}

function update_histos(inputs) {
	prefix='';
	suffix='';
	ilen=inputs.length;
	for (i=0;i<ilen;i++) {
		if (inputs[i][0] == 'TOP/c_hitsPerEvent_top') {
			draw_histo(prefix+'TOP/c_hitsPerEvent'+suffix,inputs[i][1]);
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
	fileref.setAttribute("href", "/css/"+cssfile);
	document.getElementsByTagName("head")[0].appendChild(fileref);
	document.getElementById("wrapper").innerHTML = "";
	for (j in histos) {
		document.getElementById("wrapper").innerHTML += "<div class=" + histos[j][1] + " id=" + histos[j][1] + "></div>\n";
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
		var item_id=(jsonfile.split('/')[2]).split('.')[0];
		//console.log("jsonfile: "+jsonfile+", item_id: "+item_id);
		make_index(item_id);
	}).send();
}

//function page_initialize(name="") {
//	var rootfile=name;
//	if (rootfile=="")
//		rootfile=JSROOT.GetUrlOption("rootfile");
//
//	JSROOT.OpenFile(rootfile, function(file) {
//		root_file = file;
//	});
//}

//function page_initialize(filename="",refname="",canvasname="",index_json="") {
//	var rootfile=filename;
//	if (rootfile=="")
//		rootfile=JSROOT.GetUrlOption("rootfile");
//
//	JSROOT.OpenFile(rootfile, function(file) {
//		root_file = file;
//		load_ref(refname);
//		load_canvas(canvasname);
//		build_menu(index_json);
//	});
//}

function page_initialize(filename="",refname="",canvasname="",index_json="") {
	var rootfile=filename;
	if (rootfile=="")
		rootfile=JSROOT.GetUrlOption("rootfile");

	JSROOT.OpenFile(rootfile, function(file) {
		root_file = file;

		var cname=canvasname;
		if (cname=="")
			cname=JSROOT.GetUrlOption("canvasfile");

		JSROOT.OpenFile(cname, function(cfile) {
			canvas_file = cfile;

			var rname=refname;
			if (rname=="")
				rname=JSROOT.GetUrlOption("reffile");

			JSROOT.OpenFile(rname, function(rfile) {
				ref_file = rfile;

				build_menu(index_json);
			});
		});

	});
}
								  
function load_ref(name="") {
	var refname=name;
	if (refname=="")
		refname=JSROOT.GetUrlOption("reffile");

	JSROOT.OpenFile(refname, function(file) {
		ref_file = file;
	});
}

function load_canvas(name="") {
	var cname=name;
	if (cname=="")
		cname=JSROOT.GetUrlOption("canvasfile");

	JSROOT.OpenFile(cname, function(file) {
		canvas_file = file;
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
		menu.innerHTML += '<font color="red">Run: ' + runno +'</font><br/>\n';
		for (var i=0; i<items.length; i++) {
			var item=items[i];
			if (item.dir != null) {
				menu.innerHTML += item.dir+'<br/>\n';
				for (var j=0; j<item.items.length; j++) {
					var subitem = item.items[j];
					menu.innerHTML += '<a href="#" onclick=page_load("/' + subitem.jsonfile + '") id="' + subitem.jsonfile.split('.')[0].split('/')[1] + '" class="w3-bar-item w3-button">' + subitem.title + '</a><br/>\n';
				}
			} else {
					menu.innerHTML += '<a href="#" onclick=page_load("/' + item.jsonfile + '") id="' + item.jsonfile.split('.')[0].split('/')[1] + '" class="w3-bar-item w3-button">' + item.title + '</a><br/>\n';
			}
		}
	}).send();
}

function make_index(id_name) {
	//console.log("id_name: "+id_name);
	var all_links = document.getElementsByTagName("a");
	for (var i=0; i<all_links.length; i++) {
		var link = all_links[i];
		if (link.id == id_name) {
			//console.log("link.id: "+link.id);
			document.getElementById(link.id).classList.add('w3-black');
		} else {
			document.getElementById(link.id).classList.remove('w3-black');
		}
	}
}
