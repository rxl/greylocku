function viewCluster(e) {
    // FIXME: super hacky...
    var id = parseInt(e.srcElement.id.split('-')[2]) - 1;
    for (var j=0; j<clusters[id].members.length; j++) {
        $.tmpl(cluster_member_template, {'i': clusters[id].members[j].i, 'name': clusters[id].members[j].name}).appendTo("#list-of-friends");
    }
    $("#viewcluster-title").html(clusters[id].members.length + ' friends in cluster');
    $("#viewcluster-modal").modal({keyboard : false, backdrop : 'static', show: true});
}

function cacheClusters(clusters) {
    clusters_s = JSON.stringify(clusters);
    localStorage.setItem('clusters', clusters_s);
}

function showClusters(clusters) {
    var cluster_template = '<div class="cluster"><div class="cluster-info"><div class="cluster-title title"><span class="cluster-bullet">&bull;</span><span class="cluster-bullet">&bull;</span><span class="cluster-bullet">&bull;</span>Cluster ${i}<span class="cluster-bullet">&bull;</span><span class="cluster-bullet">&bull;</span><span class="cluster-bullet">&bull;</span></div></div><ul class="list-of-friends" id="cluster_${i}"></ul></div>'
    + '<p class="button"><a class="btn btn-large" id="viewcluster-button-${i}">Expand Cluster</a></p>';

    cluster_member_template = '<li><div class="friend-picture"><img src="http://graph.facebook.com/${i}/picture?type=large" width="80" class="picx80"></div><div class="friend-name">${name}</div></li>';

    for (var i=0; i<clusters.length; i++) {
        $.tmpl(cluster_template, {'alpha': parseInt(clusters[i].alpha*100), 'beta': parseInt(clusters[i].beta*100), 'i': parseInt(i+1)}).appendTo("#clusterDiv");
	var obj = { cluster_id: i };
	$("#viewcluster-button-" + (i+1)).click(viewCluster);
    }

   for (var i=0; i<clusters.length; i++) {
        var cluster_size = clusters[i].members.length;
	if (cluster_size > 10) cluster_size = 10;
        for (var j=0; j<cluster_size; j++) {
	    $.tmpl(cluster_member_template, {'i': clusters[i].members[j].i, 'name': clusters[i].members[j].name}).appendTo("#cluster_" + parseInt(i+1));
	}
    }
}

function onClustersReceive(data) {
    clearLoadingStatus();
    clusters = data.clusters;
    cacheClusters(clusters);
    showClusters(data.clusters);
} 


function graphMuseError(jqXHR, exception) {
            clearLoadingStatus();

            if (jqXHR.status === 0) {
                document.getElementById("loading").innerHTML = 'Not connected. Verify network.';
            } else if (jqXHR.status == 404) {
                document.getElementById("loading").innerHTML = 'Requested page not found. [404]';
            } else if (jqXHR.status == 500) {
                document.getElementById("loading").innerHTML = 'Internal Server Error [500].';
            } else if (exception === 'parsererror') {
                document.getElementById("loading").innerHTML = 'Requested JSON parse failed.';
            } else if (exception === 'timeout') {
                document.getElementById("loading").innerHTML = 'Time out error.';
            } else if (exception === 'abort') {
                document.getElementById("loading").innerHTML = 'Ajax request aborted.';
            } else {
                document.getElementById("loading").innerHTML = 'Uncaught Error. ' + jqXHR.responseText;
            }
}

function setLoadingStatus() {
    $("#loading-message").show();
}

function clearLoadingStatus() {
    $("#loading-message").fadeOut(1000);
}

function loadClusters() {
    clusters_s = localStorage.getItem('clusters');
    if (clusters_s) {
        clusters = JSON.parse(clusters_s);
	showClusters(clusters);
    } else {
        setLoadingStatus();
        $.ajax({
            'url' : 'http://api.graphmuse.com:8081/clusters?auth=AAAB01zpxDDcBAGZAl5GXrPqqepF0ZAdzs7CysuZAkj6pK2LH96vh8MLnUT0CVrGq2hI8IfXUIYwcrxGG0zzEu0ez2O4z6GbtWEfq08CQAZDZD&beta=0.75',
            'dataType' : 'JSON',
            'success' : onClustersReceive,
            'error' : graphMuseError
        });
    }
}

$(document).ready(function() {

    loadClusters();

});