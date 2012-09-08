// Classes for the link and the visible dropdown
var eS_selectclass='enhance'; 					// class to identify selects
var eS_boxclass='selectparent'; 				// parent element
var eS_triggeron='enhancedtriggeractive'; 		// class for the active trigger link
var eS_triggeroff='enhancedtrigger';			// class for the inactive trigger link
var eS_dropdownclosed='dropdownreplacement'; 	// closed dropdown
var eS_dropdownopen='enhanceddropdownvisible';	// open dropdown

var eS_listclass='turnintoselect';				// class to identify ULs

function enhanceSelect()
{
/*
	Turn all selects into DOM dropdowns
*/
	var sels,i,hiddenfield,j,trigger,replaceUL,newli,newa,uls,newform,newselect,newopt;
	var count=0;
	var toreplace=new Array();
	var replaceULs=new Array();

	sels=document.getElementsByTagName('select');
	for(i=0;i<sels.length;i++){
		if (checkClass(sels[i],eS_selectclass))
		{
			hiddenfield=document.createElement('input');
			hiddenfield.name=sels[i].name;
			hiddenfield.type='hidden';
			hiddenfield.id=sels[i].id;
			hiddenfield.value=sels[i].options[0].value;
			sels[i].parentNode.insertBefore(hiddenfield,sels[i])
			trigger=document.createElement('a');
			trigger.href='#';
			trigger.className=eS_triggeroff;
			trigger.onclick=function(){eS_showSel(this);return false;}
			trigger.appendChild(document.createTextNode(sels[i].options[0].text));
			sels[i].parentNode.insertBefore(trigger,sels[i]);
			replaceUL=document.createElement('ul');
			for(j=0;j<sels[i].getElementsByTagName('option').length;j++)
			{
				newli=document.createElement('li');
				newa=document.createElement('a');
				newa.href='#';
				newli.v=sels[i].getElementsByTagName('option')[j].value;
				newli.elm=hiddenfield;
				newli.istrigger=trigger;
				newa.appendChild(document.createTextNode(
				sels[i].getElementsByTagName('option')[j].text));
				newli.onclick=function(){ 
					var txt=this.getElementsByTagName('a')[0].firstChild.nodeValue;		
					eS_setVal(this.v,this.elm,this.istrigger,txt);return false;
					}
				newli.appendChild(newa);
				replaceUL.appendChild(newli);
			}
			replaceUL.className=eS_dropdownclosed;
			toreplace[count]=sels[i];
			replaceULs[count]=replaceUL;
			count++;
		}
	}
	for(i=0;i<count;i++)
	{
		var div=document.createElement('div');
		div.appendChild(replaceULs[i]);
		div.className=eS_boxclass;
		toreplace[i].parentNode.insertBefore(div,toreplace[i])
		toreplace[i].parentNode.removeChild(toreplace[i])
	}
	
/*
	Turn all ULs with the class defined above into dropdown navigations
*/	
	count=0;
	toreplace.length=0;
	replaceULs.length=0;

	uls=document.getElementsByTagName('ul');
	for(i=0;i<uls.length;i++)
	{
		if(checkClass(uls[i],eS_listclass))
		{
			newform=document.createElement('form');
			newselect=document.createElement('select');
			alla=uls[i].getElementsByTagName('a');
			for(j=0;j<alla.length;j++)
			{
				newopt=document.createElement('option');
				newopt.setAttribute('value',alla[j].href);	
				newopt.appendChild(document.createTextNode(alla[j].innerHTML));	
				newselect.appendChild(newopt);
			}
			newform.appendChild(newselect);
			replaceULs[count]=newform;
			toreplace[count]=uls[i];
			count++;
		}
	}
	for(i=0;i<count;i++)
	{
		toreplace[i].parentNode.insertBefore(replaceULs[i],toreplace[i])
		toreplace[i].parentNode.removeChild(toreplace[i])
		replaceULs[i].getElementsByTagName('select')[0].onchange=function()
			{
				self.location=this.options[this.selectedIndex].value;
			}
	}
}

/*
	Show or hide the replacement UL
*/
function eS_showSel(o){
	var drop=o.parentNode.getElementsByTagName('ul')[0];
	if(checkClass(o,eS_triggeron))
	{
		juggleClass(o,eS_triggeron,0)
		juggleClass(o,eS_triggeroff,1)
		juggleClass(drop,eS_dropdownopen,0)
	} else {
		if(o.getElementsByTagName('span')[0])
		{
			o.removeChild(o.getElementsByTagName('span')[0]);
		}
		juggleClass(o,eS_triggeroff,0)
		juggleClass(o,eS_triggeron,1)
		juggleClass(drop,eS_dropdownopen,1)
	}
}

/*
	Set the value when a link in the UL gets clicked
*/
function eS_setVal(val,el,o,txt)
{
	el.value=val;
	o.firstChild.nodeValue=txt;
	eS_showSel(o);
}

// Help functions to check for a class and to add or remove a class
function juggleClass(o,c,s)
{
	o.className=s==1?o.className+' '+c:o.className.replace(' '+c,'');	
}
function checkClass(o,c)
{
	var re=new RegExp('\\b'+c+'\\b');
	return re.test(o.className);
}

// Check if DOM is avaiable, and if so, start enhanceSelect
if(document.getElementById && document.createTextNode)
{
	window.onload=enhanceSelect;
}
