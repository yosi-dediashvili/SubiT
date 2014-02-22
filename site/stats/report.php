<?php
/*
This page is supposed to be run whenever a fresh install of SubiT is being 
uploaded. 

We collect annoymous usage statistics by counting for each month the number of
calls to this page.

We collect usage on platform base. For each day, there will be a file under 
the "stats" folder. The content of the file will simply be the number of times 
the script was called by SubiT.
*/

function get_file_path($os, $date_str = NULL) {
	$date = $date_str == NULL ? date("dmy") : $date_str;
	return "./" . $os . "/" . $date;
}

function read_usage($os, $date_str = NULL) {
	$date = $date_str == NULL ? date("dmy") : $date_str;
	return (int)file_get_contents(get_file_path($os, $date));
}

function write_usage($os, $usage) {
	file_put_contents(get_file_path($os), (string)$usage);
}

function increase_usage($os) {
	$current_usage = read_usage($os);
	write_usage($os, $current_usage + 1);
}

function show_usage($os_dir) {
	print "<br>";
	print "Usage stats for $os_dir:";
	print "<table><thead><th>Day</th><th>Count</th></thead>";
	print "<tbody>";

	$total_usage = 0;
	foreach (new DirectoryIterator("./" . $os_dir) as $fileInfo) {
	    if(!$fileInfo->isDot()) {
	    	$date = $fileInfo->getFilename();
	    	$usage = read_usage($os_dir, $date);
	    	global $total_usage;
	    	$total_usage += $usage;
	    	print "<tr><td>$date</td><td>$usage</td></tr>";
	    }
	}	
	print "</tbody></table>";
	print "Total usage: $total_usage";
}
	
	$operating_systems = array("win", "linux");
	switch ($_SERVER['REQUEST_METHOD']) {
		case "GET":
			if (isset($_GET['os_type']) && 
				in_array($_GET['os_type'], $operating_systems)) {

				show_usage($_GET['os_type']);
			}
			break;
		case "POST":
			if (isset($_POST['os_type']) && 
				in_array($_POST['os_type'], $operating_systems)) {

				increase_usage($_POST['os_type']);
			}
			break;
	}
?>