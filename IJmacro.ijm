//# String(label="Which data channel are you importing?", value="None") data
//# String(label="Which data are you importing as Overlay?", value="None") overlay
//# File(label="What is the reference frame for ROI?") ROI
//# File(label="What is the parent directory?", style="directory") folder

args = getArgument;
args = split(args, ",");
data = args[0];
overlay = args[1];
ROI = args[2];
folder = args[3];

data = toUpperCase(data)
overlay = toUpperCase(overlay)
dir = File.getParent(folder)+"/"

if (overlay != "None") {
	makeStack(overlay, ROI);
	measure(overlay);
	close();
}

if (data != "None") {
	makeStack(data, ROI);
	measure(data);
	close();
	close("ROI Manager");
}

run("Quit");

function makeStack(data, ROI) {
	run("Image Sequence...", "open="+folder+" file="+data+" sort");
	run("Open...", "open="+ROI);
	run("Concatenate...", "all_open title=stack"+data);
	run("8-bit");
	setOption("BlackBackground", true);
	run("Make Binary", "method=Default background=Default calculate black");
	run("Set Scale...", "distance=0 known=0 pixel=1 unit=pixel");
	n = nSlices;
	for (i=1; i<=n; i++) {
		min = 0;
		setSlice(i);
		getStatistics(area, mean, min);
		if (min == 255) {
			run("Invert", "slice");
		}
	}
	run("StackReg", "transformation=[Rigid Body]");
	if (data == "yellow") {
		run("Duplicate...", "use");
		saveAs("Tiff", dir+"ROI.tif");
		run("Analyze Particles...", "clear add");
		roiManager("Save", dir+"ROIset.zip");
		close("*ROI*");
	}
	selectWindow("stack"+data);
	run("Delete Slice");
	saveAs("Tiff", dir+"stack"+data+".tif");
}

function measure(channel) {
	roiManager("multi-measure measure_all");
	saveAs("Results", dir+"results"+channel+".csv");
	run("Close");
}
