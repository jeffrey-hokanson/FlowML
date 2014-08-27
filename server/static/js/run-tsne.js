$(document).ready(function(){
	$("#run-tsne").click(function(){
		$.post("run-tsne",
		{
			name:"dummy data"
		},
		function(data,status){
			alert("Data: " + data + "\nStatus: " + status);
		});
	});
});
