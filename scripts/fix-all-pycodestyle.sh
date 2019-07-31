ls |awk -F ' ' '{print $NF}'|while read line
do 
    autopep8 --in-place  $line
done
