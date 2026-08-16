const apiKey = process.env.REACT_APP_GOOGLE_MAPS_API_KEY;

export function getDriveTime(origin, destination) {
  return new Promise((resolve, reject) => {
    if (!apiKey) {
      return reject(new Error('REACT_APP_GOOGLE_MAPS_API_KEY is not configured'));
    }
    if (!window.google?.maps) {
      return reject(new Error('Maps API not loaded'));
    }
    new window.google.maps.DirectionsService().route(
      { origin, destination, travelMode: window.google.maps.TravelMode.DRIVING },
      (result, status) => {
        if (status === 'OK') {
          const leg = result.routes[0].legs[0];
          const durationSec = leg.duration.value;
          const distanceKm  = leg.distance.value / 1000;
          resolve({ durationSec, distanceKm });
        } else if (status === 'ZERO_RESULTS') {
          // no drivable route—resolve to null so your UI can handle it
          resolve(null);
        } else {
          reject(new Error(`Directions failed: ${status}`));
        }
      }
    );
  });
}

