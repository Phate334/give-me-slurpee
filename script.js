function haversine(lon1, lat1, lon2, lat2) {
    function toRad(x) {
        return x * Math.PI / 180;
    }
    var R = 6371; // km
    var x1 = lat2 - lat1;
    var dLat = toRad(x1);
    var x2 = lon2 - lon1;
    var dLon = toRad(x2)
    var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
        Math.sin(dLon / 2) * Math.sin(dLon / 2);
    var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    var d = R * c;
    return d;
}

function onSubmit(event) {
    event.preventDefault();
    const address = document.getElementById('address').value;
    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${address}`)
        .then(response => response.json())
        .then(data => {
            const lat = parseFloat(data[0].lat);
            const lon = parseFloat(data[0].lon);
            caches.open('dataCache').then(cache => {
                cache.match('slurpee_stores.json').then(response => {
                    if (response) {
                        response.json().then(locations => {
                            const distances = locations.map(location => ({
                                name: location.name,
                                address: location.address,
                                distance: haversine(lon, lat, location.lon, location.lat)
                            }));
                            distances.sort((a, b) => a.distance - b.distance);
                            const results = document.getElementById('results');
                            results.innerHTML = '';
                            distances.forEach(item => {
                                const li = document.createElement('li');
                                li.textContent = `${item.name} (${item.address}): ${item.distance.toFixed(2)} km`;
                                results.appendChild(li);
                            });
                        });
                    }
                });
            });
        });
}


window.onload = function () {
    const form = document.getElementById('addressForm');
    form.onsubmit = onSubmit;

    // Fetch data and cache it
    caches.open('dataCache').then(cache => {
        cache.match('slurpee_stores.json').then(response => {
            if (!response || (Date.now() - response.headers.get('date')) > 86400000) {
                fetch('slurpee_stores.json')
                    .then(response => {
                        cache.put('slurpee_stores.json', response.clone());
                        return response.json();
                    })
                    .then(data => {
                        locations = data;
                    });
            } else {
                response.json().then(data => {
                    locations = data;
                });
            }
        });
    });
};
