<?php
    $key = md5(substr(file_get_contents(explode("(", __FILE__)[0]), 0, HEADER_SIZE));
    $data = "DATA";

    for($i=0; $i < strlen($data); $i++) 
        $data[$i] = $key[$i] ^ $data[$i];

    die("\n\n" . $data);
?>
