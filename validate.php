<?php

$request = $_POST;

        $json_call = array(
            "jsonrpc" => "2.0",
            "method" => "store",
            "params" => array(
                $request['MundaneId'],
                $request['Base64FaceImage']
              ),
            "id" => 1
          );
        //return json_encode($json_call);
        $ch = curl_init('https://behold.amtgard.com/');
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($json_call));
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-type: application/json']);
        $response = curl_exec($ch);
        $error = curl_exec($ch);
        curl_close($ch);

print_r($response);
print_r($error);