<?php
error_reporting(0);
header("Content-Type: text/html;charset=utf-8");
$newest_version = "1.1.0";
$newest_download = "http://pan.baidu.com/s/1boq8XA3";
$newest_download = iconv('gbk','utf-8',$newest_download);
$get_version = trim($_GET["version"],"V");
if (version_compare($newest_version,$get_version) == 1){
	echo json_encode(array('Version'=>'V'.$newest_version,
	'Download'=>$newest_download));
}
?>