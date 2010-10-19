this.nextmuni = this.nextmuni || {};


nextmuni.saveMapCenter = function(center) {
    console.log('saving map center');
    nextmuni.saveMapCenter.center = center;
};


nextmuni.setMapCenter = function(center) {
    console.log('setting map center to', center);

    google.maps.event.addListenerOnce(nextmuni.map, 'idle', function() {
        nextmuni.queryBounds();
    });

    nextmuni.map.setCenter(center);

    if (nextmuni.centerMarker) {
        nextmuni.centerMarker.setMap(null);
    }
    nextmuni.centerMarker = new google.maps.Marker({
        'map': nextmuni.map,
        'position': center,
        'title': 'You are here.'
    });
};


nextmuni.setCenter = nextmuni.saveMapCenter;


nextmuni.getCurrentPosition = function(fun) {
    navigator.geolocation.getCurrentPosition(function(position) {
        console.log('current location', position);
        var center = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
        fun.call(this, center);
    }, function() {
        console.error('geolocation failed');
    });
};
/*nextmuni.getCurrentPosition = function(fun) { // XXX mock
    console.log('mock getCurrentPosition()');
    var center = new google.maps.LatLng(37.7867656, -122.4580752);
    fun.call(navigator.geolocation, center);
};*/


nextmuni.queryBounds = function() {
    console.log('queryBounds()');
    var bounds = nextmuni.map.getBounds();
    $.ajax({
        'url': '/api/stops',
        'data': {
            'n': bounds.getNorthEast().lat(),
            'e': bounds.getNorthEast().lng(),
            's': bounds.getSouthWest().lat(),
            'w': bounds.getSouthWest().lng()
        },
        'success': function(data, status, xhr) {
            console.log('/api/stops', 'success', data);
            data.stops.forEach(function(stop) {
                var position = new google.maps.LatLng(stop.location.lat, stop.location.lng);
                var marker = new google.maps.Marker({
                    'map': nextmuni.map,
                    'position': position,
                    'title': stop.title
                });
                google.maps.event.addListener(marker, 'click', function(e) {
                    $.ajax({
                        'url': '/api/stop/' + stop.key,
                        'success': function(data, status, xhr) {
                            console.log('stop', stop, data);
                        }
                    });
                });
            });
        }
    });
};


//
// init
//


$(function() {
    console.log('initializing map');
    nextmuni.map = new google.maps.Map($('#map').get(0), {
        'mapTypeId': google.maps.MapTypeId.ROADMAP,
        'zoom': 16
    });
    nextmuni.setCenter = nextmuni.setMapCenter;
    nextmuni.saveMapCenter.center && nextmuni.setMapCenter(nextmuni.saveMapCenter.center);
});


if (navigator.geolocation) {
    console.log('browser has geolocation');
    nextmuni.getCurrentPosition(function(center) {
        nextmuni.setCenter(center);
    });
}