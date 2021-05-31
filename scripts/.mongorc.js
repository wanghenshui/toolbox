prompt = function(){
	return (new Date())+">";
}

try{
	db.runCommand({getLastError:1});
}
catch(e){
	print(e);
}