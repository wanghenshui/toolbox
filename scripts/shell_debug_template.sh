#!/bin/bash

#do you work here...

trap 'cleanup; exit '  1 2 3 15

function cleanup(){
#do you cleanup here
}

sleep infinity
