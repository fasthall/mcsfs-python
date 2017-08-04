#!/bin/bash

pkgs=mcsfs/lib/python2.7/site-packages/

rm -f lambda.zip
zip -r9 lambda.zip lambda_function.py gochariots.py
current_path=$PWD
cd $pkgs
zip -ur $current_path/lambda.zip *
cd $current_path
echo 'lambda_function.lambda_handler'

