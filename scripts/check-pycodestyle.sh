ls |awk -F ' ' '{print $NF}'|while read line
do 
    pycodestyle $line  --ignore=E501
done
