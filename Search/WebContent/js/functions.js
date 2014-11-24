/**
 * 
 */

function doQuery() {
	alert("!!!");
	var query = $("#query_input").val();
	if (query == "")
		return;
	alert(query);
	$.get("/esp/ESPServlet", {q : query} );
}

function showResults(data) {
	var html = "";
	for (var i = 0; i < data.length; i++) {
		var res = data[i];
		html += "<div> " + "<p> title: " + res.title + "</p> </div>";
		html += "<div>";
		for (var j = 0; j < res.body.length; j++) {
			html += "<div> " + res.body[j] + " </div> ";
		}
		html += "</div>";
	}
	$("#result").html(html);

}