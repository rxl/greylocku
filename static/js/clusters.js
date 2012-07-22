/**
 *  Displaying clusters 
 */

function fetchInterests() {
    interests = new Array();
    var id = current_cluster_id;
    for (var j=0; j<clusters[id].members.length; j++) {
        $.ajax({
	    'url' : '',
	    'dataType' : 'JSON',
	    'success' : updateInterests,
	    'error' : null
	});
    }
}

function viewCluster(e) {
    // FIXME: super hacky...
    var id = parseInt(e.srcElement.id.split('-')[2]) - 1;
    current_cluster_id = id;
    for (var j=0; j<clusters[id].members.length; j++) {
        $.tmpl(cluster_member_template, {'i': clusters[id].members[j].i, 'name': clusters[id].members[j].name}).appendTo("#list-of-friends");
    }
    $("#viewcluster-title").html(clusters[id].members.length + ' friends in cluster');
    $("#viewcluster-modal").modal({keyboard : false, backdrop : 'static', show: true});
}

function showClustersOld(clusters) {
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

/**
 *  Loading and caching clusters
 */

function cacheClusters(clusters) {
    clusters_s = JSON.stringify(clusters);
    localStorage.setItem('clusters', clusters_s);
}

function onClustersReceive(data) {
    clearLoadingStatus();
    clusters = data.clusters;
    cacheClusters(clusters);
    showClusters(data.clusters);
} 


function graphMuseError(jqXHR, exception) {
            clearLoadingStatus();
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
            'url' : 'http://api.graphmuse.com:8081/clusters?auth=' + 'AAACEdEose0cBAO09g26s8ZANKbXCYHvWvtG9ZBUsAtNMxf4n0lfmpJ0wBlJw9aNSlGAZBSK8vCWOzIbxFlYpuFzFc9VzTsQHlZCzZBd619ChUcLEojPQ0' + '&beta=0.75',
            'dataType' : 'JSON',
            'success' : onClustersReceive,
            'error' : graphMuseError
        });
    }
}

/**
 *  Friend list creation 
 */


function createFriendList() {
    var id = current_cluster_id;
    var name = $('#cluster-name').val();
    var data = new Array();
    data['name'] = name;
    data['members'] = clusters[id].members;

    setSavingFriendList(id);
    $.ajax({
        'type' : 'POST',
        'url' : '/generatefriendlist/',
	'dataType' : 'JSON',
	'data' : {
	    'name' : name,
	    'members' : JSON.stringify(clusters[id].members)
	},
	'success' : onCreatedFriendList,
	'error' : createFriendListError
    });
}

function setSavingFriendList(id) {
    $("#loading-message-" + id).show();
}

function clearSavingFriendList(id) {
    $('#loading-message-' + id).fadeOut(1000);
}

function onCreatedFriendList(data) {
    list_id = data['friendlist_id'];
    id = data['cluster_id'];
    clearSavingFriendList(id);
    window.open('https://www.facebook.com/lists/' + list_id);
}

function createFriendListError(jqXHR, exception) {
    displayError("Could not create friend list");
}

function createFriendListNew(name, members, id) {
    setSavingFriendList(id);
    $.ajax({
        'type' : 'POST',
        'url' : '/generatefriendlist/',
        'dataType' : 'JSON',
        'data' : {
            'name' : name,
            'members' : JSON.stringify(members),
            'cluster_id' : id
        },
        'success' : onCreatedFriendList,
        'error' : createFriendListError
    });
}

/**
 *  Misc
 */

function displayError(message) {
    alert("Error: " + message);
}

/**
 *  Main
 */

$(document).ready(function() {
    $("#friendlist-button").click(createFriendList);
    loadClusters();
});
