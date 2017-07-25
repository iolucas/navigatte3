//------------------------------------------------------------------
//------------------------------------------------------------------
//--------------------- G-QUERY LIBRARY-----------------------------
//------------------------------------------------------------------
//------------------------------------------------------------------

//------------------------------------------------------------------
//-------------------- G-QUERY METHODS -----------------------------
//------------------------------------------------------------------

var $G = new function() {
	//set namespaces
	var self = this,
        gquery_xmlns = "http://www.w3.org/2000/svg",
		gquery_xlink = "http://www.w3.org/1999/xlink";  

	//function to create any graphic stuff
	this.create = function(elemName) {
		return document.createElementNS(gquery_xmlns, elemName);
	}

    this.createText = function(text, size, fontFace, weight, color, decoration) {
        var newText = $G.create("text");

        if(fontFace)
            newText.setAttribute("font-family", fontFace);
        
        if(size != undefined)
            newText.setAttribute("font-size", size);
        
        if(decoration)
            newText.setAttribute("font-decoration", decoration);

        if(weight)
            newText.setAttribute("font-weight", weight);

        if(color)
            newText.setAttribute("fill", color);

        newText.innerHTML = text;

        /*var newTextBox = newText.getBBox();
        //console.log(repeatBox);
        newText.setAttribute("y", -newTextBox.y);
        newText.setAttribute("x", -newTextBox.width);*/ 

        return newText;
    }

    this.createArc = function(x, y, radius, startAngle, endAngle) {

        var start = polarToCartesian(x, y, radius, endAngle);
        var end = polarToCartesian(x, y, radius, startAngle);

        var arcSweep = endAngle - startAngle <= 180 ? "0" : "1";

        var d = [
            "M", start.x, start.y, 
            "A", radius, radius, 0, arcSweep, 0, end.x, end.y
        ].join(" ");

        return d;       
    }

    this.createCircle = function(x,y, radius) {
        return self.createArc(x, y, radius, 0, 359.9);
    }

    function polarToCartesian(centerX, centerY, radius, angleInDegrees) {
        var angleInRadians = (angleInDegrees-90) * Math.PI / 180.0,
            resultObj = {}
        resultObj.x = centerX + (radius * Math.cos(angleInRadians));
        resultObj.y = centerY + (radius * Math.sin(angleInRadians));
        return resultObj;
    }
}

//------------------------------------------------------------------
//-------------------- G-QUERY PROTOTYPES --------------------------
//------------------------------------------------------------------

//Function to get the decimal part of a value
Number.prototype.getDecimalValue = function() {
    return this - Math.floor(this);    
}

//Function to get whether the value is even (if not is odd)
Number.prototype.isEven = function() {
    return this % 2 ? false : true;
}

//--------------------- CIRCLE ELEMENTS PROTOTYPES -----------------

//Function to set the circle radius
SVGCircleElement.prototype.setRadius = function(r) {
    this.setAttribute("r", r);     
}

//Function to get the circle radius
SVGCircleElement.prototype.getRadius = function() {
    return this.getAttribute("r");     
}

//--------------------- GEOMETRY ELEMENTS PROTOTYPES ----------------

//if svg geometry is not defined
if(!SVGGeometryElement)
    //Define it as the graphics element
    var SVGGeometryElement = SVGGraphicsElement;    

SVGGeometryElement.prototype.fill = function(color) {
    this.setAttribute("fill", color);
}
SVGGeometryElement.prototype.setFillColor = SVGGeometryElement.prototype.fill;

SVGGeometryElement.prototype.getFillColor = function() {
    return this.getAttribute("fill");
}

SVGGeometryElement.prototype.setStrokeColor = function(color) {
    this.setAttribute("stroke", color);
}

SVGGeometryElement.prototype.getStrokeColor = function() {
    return this.getAttribute("stroke");
}

SVGGeometryElement.prototype.setStrokeWidth = function(width) {
    this.setAttribute("stroke-width", width);
}

SVGGeometryElement.prototype.getStrokeWidth = function() {
    return this.getAttribute("stroke-width");
}


//--------------------- GRAPHIC ELEMENTS PROTOTYPES -----------------

//Set an enhanced "getBBox()" method to ensure bboxes even with the element not appended to the final document
SVGGraphicsElement.prototype.__oldGetBBox = SVGGraphicsElement.prototype.getBBox;	//store the old getbbox
SVGGraphicsElement.prototype.getBBox = function () {	//set the new one
    var bBox;
    try {
        bBox = this.__oldGetBBox();   //try to get element bBox
        if(bBox.x || bBox.y || bBox.width || bBox.height) //if any of the members are valid,
            return bBox;    //return the gotten bbox cause it is valid
        else //if not suceed
            throw "BBOX_NOT_VALID";	//crash the try block (firefox crashes automatically, chrome doesn't)
    } catch(e) { //if it is not valid,

        //recursively checks the parent element of the current element to find the highest not null
        var higherNotNullElement = this;
        for(;;) {
            if(higherNotNullElement.parentElement)
                higherNotNullElement = higherNotNullElement.parentElement;
            else
                break;               
        }

        //if the last element is one of the root tags, means the element is completely appended and the bbox cleared is the right one
        if(higherNotNullElement.tagName == "HTML" || higherNotNullElement.tagName == "svg")
            return { width: 0, height: 0, x: 0, y: 0 };    //return a cleared bBox obj

        var auxParent;  //aux parent to append the element for get its bbBox

        //if the root document is already a svg, 
        if(document.documentElement.tagName == "svg")
            auxParent = document.documentElement; //set the svg doc parent element as the auxParent
        else if(document.documentElement.tagName == "HTML") { //if is a HTML
            auxParent = $G.create("svg");   //creates a svg doc for it
            document.body.appendChild(auxParent);   //append the svg doc to the html doc body
        }
        else //if neither one of them, throw error
            throw "G-QUERY_ERROR__UNKNOWN_DOC_TYPE";

        //append the higher element to the auxiliar parent to be able to get this element bbox
        auxParent.appendChild(higherNotNullElement);  
        bBox = this.__oldGetBBox();   //get this element bBox

        //remove higher element from its aux parent
        auxParent.removeChild(higherNotNullElement); 

        if(auxParent.parentElement)
            auxParent.parentElement.removeChild(auxParent);

        delete auxParent;
        return bBox;
    }
}

/*SVGGraphicsElement.prototype.GetAbsWidth = function() {
    var elemBox = this.getBBox();
    return elemBox.width - elemBox.x;
}*/

//Set a translate function for easily set the transform attribute to the element
SVGGraphicsElement.prototype.translate = function(x, y) {
	//get the transform string
    var oldValues = this.getAttribute("transform");
    if (!oldValues) //if the string were not found
        oldValues = "";//clear variable

    //Clear the current transform value word
    //get the start index of the current transform prop
    var startIndex = oldValues.indexOf("translate");
    if (startIndex > -1) {
        var endIndex = oldValues.indexOf(")", startIndex);  //get the end index
        //Clear the old value for the given transform
        oldValues = oldValues.replace(oldValues.substring(startIndex, endIndex + 1), "");
    }

    //if the angle hasn't been informed, return
	if(x == undefined) {
		this.setAttribute("transform", oldValues);	
		return;		
	}	

    var transStr = "translate(" + x;
    
    if(y)	
    	transStr += " " + y;

	transStr += ")";

    oldValues += transStr;

    this.setAttribute("transform", oldValues);
}

//Set a rotate function for easily set the transform attribute to the element
SVGGraphicsElement.prototype.rotate = function(angle, x, y) {
	//get the transform string
    var oldValues = this.getAttribute("transform");
    if (!oldValues) //if the string were not found
        oldValues = "";//clear variable

	//Clear the current rotate transform string
    //get the start index of the current transform prop
    var startIndex = oldValues.indexOf("rotate");
    if (startIndex > -1) {
        var endIndex = oldValues.indexOf(")", startIndex);  //get the end index
        //Clear the old value for the given transform
        oldValues = oldValues.replace(oldValues.substring(startIndex, endIndex + 1), "");
    }

    //if the angle hasn't been informed, return
	if(angle == undefined) {
		this.setAttribute("transform", oldValues);	
		return;		
	}		

    var transStr = "rotate(" + angle;
    
    if(typeof x == "number" && typeof y == "number")	
    	transStr += " " + x + " " + y;

	transStr += ")";

    oldValues += transStr;	//append the transform string to the old values

    this.setAttribute("transform", oldValues);
}

//Set a translate function for easily set the transform attribute to the element
SVGGraphicsElement.prototype.scale = function(x, y) {
	//get the transform string
    var oldValues = this.getAttribute("transform");
    if (!oldValues) //if the string were not found
        oldValues = "";//clear variable

    //Clear the current transform value word
    //get the start index of the current transform prop
    var startIndex = oldValues.indexOf("scale");
    if (startIndex > -1) {
        var endIndex = oldValues.indexOf(")", startIndex);  //get the end index
        //Clear the old value for the given transform
        oldValues = oldValues.replace(oldValues.substring(startIndex, endIndex + 1), "");
    }

    //if the x value hasn't been informed, return
	if(x == undefined) {
		this.setAttribute("transform", oldValues);	
		return;		
	}	

    var transStr = "scale(" + x;
    
    if(y)	
    	transStr += " " + y;

	transStr += ")";

    oldValues += transStr;

    this.setAttribute("transform", oldValues);
}

//Function to get the transform attribute for a given element
SVGGraphicsElement.prototype.getTransform = function (property) {
    var tString = this.getAttribute("transform");
    if (!tString) return null;  //if no transform has been applied

    var pIndex = tString.indexOf(property);
    if (pIndex == -1) return null;  //if the prop is not found, return null

    var sIndex = tString.indexOf("(", pIndex),
        eIndex = tString.indexOf(")", pIndex);

    vArray = tString.substring(sIndex + 1, eIndex).split(" ");
    for (var i = 0; i < vArray.length; i++)
        vArray[i] = parseFloat(vArray[i], 10);

    return vArray;
}

SVGGraphicsElement.prototype.translateRel = function(relX, relY) {
    var currTranslateValues = this.getTransform("translate");
    if(!currTranslateValues)
        currTranslateValues = [0,0];
    else if(currTranslateValues.length == 1)
        currTranslateValues.push(0);

    this.translate(currTranslateValues[0] + relX, currTranslateValues[1] + relY);        
}

SVGGraphicsElement.prototype.enableDrag = function() {
    //If the mouse drag routine has been set, means this function has already been called
    if(this._objDragToken)  
        return; //do nothig else and return

    var self = this;

    //Object to store information about the drag event
    self._objDragToken = {}

    //Use parent to fix bug case mouse move out the element because movement too fast
    self._objDragToken.parent = self.parentElement;

    self._objDragToken.mouseDownEvent = function(mouseEvent) {
        self._objDragToken.mouseDown = true;
        self._objDragToken.oldX = mouseEvent.clientX;
        self._objDragToken.oldY = mouseEvent.clientY;
        self._objDragToken.parent.style.cursor = "move";
    }

    self._objDragToken.mouseMoveEvent = function(mouseEvent) {
        if(self._objDragToken.mouseDown) {
            self.translateRel(mouseEvent.clientX - self._objDragToken.oldX, mouseEvent.clientY - self._objDragToken.oldY);
            self._objDragToken.oldX = mouseEvent.clientX;
            self._objDragToken.oldY = mouseEvent.clientY;
        }
    }

    self._objDragToken.mouseUpEvent = function(mouseEvent) {
        self._objDragToken.mouseDown = false;
        self._objDragToken.parent.style.cursor = "";
    }

    self.addEventListener("mousedown", self._objDragToken.mouseDownEvent, true);
    self._objDragToken.parent.addEventListener("mousemove", self._objDragToken.mouseMoveEvent, true);
    self.addEventListener("mouseup", self._objDragToken.mouseUpEvent, true);
    //self.addEventListener("mouseout", self._objDragToken.mouseUpEvent, true);
}

SVGGraphicsElement.prototype.disableDrag = function() {
    //If the mouse drag token hasn't been set, means nothing to do
    if(!this._objDragToken)  
        return; //do nothig else and return

    this.removeEventListener("mousedown", self._objDragToken.mouseDownEvent, true);
    this._objDragToken.parent.removeEventListener("mousemove", self._objDragToken.mouseMoveEvent, true);
    this.removeEventListener("mouseup", self._objDragToken.mouseUpEvent, true);
    //this.removeEventListener("mouseout", self._objDragToken.mouseUpEvent, true);

    delete this._objDragToken;  //delete obj drag token
}

SVGTextElement.prototype.SetText = function(text) {
    this.innerHTML = text;
}

SVGTextElement.prototype.GetText = function() {
    return this.innerHTML;
}


//MAYBE THESE ARRAY FUNCTIONS SHOULDN'T BE HERE SINCE THIS IS ONLY FOR GRAPHICS

//Set method to an array get its true valid length
Array.prototype.getValidLength = function() {
	var length = 0;
    for(var i = 0; i < this.length; i++)
        if(this[i] != undefined)
            length++;
    return length;
}





//--------------- DEBUG AREA --------------------------------

//console.log(document.documentElement.tagName);

/*
var test = $G.create("rect");

//var svgDoc123 = $G.create("svg");
//svgDoc123.appendChild(test);
//document.body.appendChild(svgDoc123);


test.setAttribute("width", 100);
test.setAttribute("height", 100);
test.setAttribute("fill", "#000");

console.log(test.getBBox());*/

/*
var oi = $G.create("g");
oi.appendChild(test);




oi.translate(300, 300);
oi.scale(2, 1);
console.log(oi);
//console.log([test]);

var circ = $G.create("circle");
circ.setAttribute("r", 100);
circ.setAttribute("fill","yellow");
circ.translate(300,300);
document.documentElement.appendChild(circ);
document.documentElement.appendChild(oi);*/