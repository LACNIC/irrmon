<!doctype html>
<html lang="en">

<head>
  <meta charset="utf-8">
</head>

<body>

<?php
    
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
	
	function get_data() {
            // $datae = array();
            // $datae[] = array(
	    $stack = array();
	    foreach($_POST['mirrors_list'] as $checkbox) {
		    //echo $checkbox;
		    array_push($stack, $checkbox);
            }
	    //echo $stack;
            $datae = array(
                'querySourceIRR' => $_POST['querySourceIRR'],
                'queryObjectType' => $_POST['queryObjectType'],
                'queryObject' => $_POST['queryObject'],
                'queryInterval' => $_POST['queryInterval'],
                'queryTimeout' => $_POST['queryTimeout'],
	        'queryMirrorsList' => $stack
            );
	    // loop over checked checkboxes
	    //$datae['queryMirrorsList'] => $stack;
	    return json_encode($datae);
        }
          
        $name = "irr_input";
        $file_name = 'input/' . $name . '.json';
      	
	file_put_contents("$file_name", get_data());
		
	//if(file_put_contents(
        //    "$file_name", get_data())) {
        //        echo $file_name .' file created';
        //    }
        //else {
        //    echo 'There is some error';
        //}
	
    }
?>

<form accept-charset="UTF-8" target="_self" autocomplete="off" action="<?php echo htmlspecialchars($_SERVER['PHP_SELF']); ?>" method="post">
	<fieldset>
	<h1>IRR Object Monitoring</h1>
	<h3>Select Registry iof IRR Object Source</h3> 
	<input name="querySourceIRR" type="radio" value="AFRINIC" /> AFRINIC  
	<input name="querySourceIRR" type="radio" value="APNIC" /> APNIC  
	<input name="querySourceIRR" type="radio" value="ARIN" /> ARIN   
	<input name="querySourceIRR" type="radio" value="LACNIC" /> LACNIC   
	<input name="querySourceIRR" type="radio" value="RIPE" /> RIPE <br />  
        <hr />
	<h3>Select IRR Object Type</h3> 
	<select name="queryObjectType">
	<option selected="selected" value="mntner"> mntner </option> 
	<option value="aut-num"> aut-num </option> 
	<option value="as-set"> as-set </option> 
	</select><br /> 
        <hr />
	<h3>Enter IRR Object Query</h3> 
	<label> AS65000, MNT-AR-COLO22-LACNIC, AS65000:AS-CUSTOMERS</label><br />
	<input name="queryObject" cols="30" type="text" value="" /> <br /> 
        <hr />
	<h3>Query Time Interval</h3> 
	<label>Time interval between each query: 300 (5 min)</label><br /> 
	<input type="number" name="queryInterval" access="false" value="300" min="60" step="1" id="queryInterval" required="required" aria-required="true"><br />
        <hr />
	<h3>Timeout Response</h3> 
	<label>Maximum timeout in seconds if no response is received: 10 seconds</label><br /> 
	<input type="number" name="queryTimeout" access="false" value="10" min="5" max="30" step="1" id="queryTimeout" required="required" aria-required="true"><br />
        <hr />
	<h3>Select Multiples Mirrors to Query</h3>
	<input name="mirrors_list[]" type="checkbox" value="NTT" /> NTT 
	<input name="mirrors_list[]" type="checkbox" value="RADB" /> RADB  
	<input name="mirrors_list[]" type="checkbox" value="LEVEL3" /> LEVEL3  
	<input name="mirrors_list[]" type="checkbox" value="ROGERS" /> ROGERS <br /><br /> 
	<input name="mirrors_list[]" type="checkbox" value="ALTDB" /> ALTDB
	<input name="mirrors_list[]" type="checkbox" value="AOLTW" /> AOLTW
	<input name="mirrors_list[]" type="checkbox" value="BELL" /> BELL
	<input name="mirrors_list[]" type="checkbox" value="BBOI" /> BBOI
	<input name="mirrors_list[]" type="checkbox" value="CANARIE" /> CANARIE
	<input name="mirrors_list[]" type="checkbox" value="EPOCH" /> EPOCH
	<input name="mirrors_list[]" type="checkbox" value="IDNIC" /> IDNIC
	<input name="mirrors_list[]" type="checkbox" value="JPIRR" /> JPIRR
	<input name="mirrors_list[]" type="checkbox" value="NESTEGG" /> NESTEGG
	<input name="mirrors_list[]" type="checkbox" value="PANIX" /> PANIX
	<input name="mirrors_list[]" type="checkbox" value="REACH" /> REACH
	<input name="mirrors_list[]" type="checkbox" value="TC" /> TC <br /> 
        <hr />
	<button type="submit" value="Submit">Submit</button>
	</fieldset>
</form>
</body>
</html>

