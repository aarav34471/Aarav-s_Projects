import { useEffect, useState } from 'react';

const apiKey = "AIzaSyBMSK_uKvcJXdsLsFV38Vx_Yx5XGub5R-s";

export function getDriveTime(origin, destination) {
  return new Promise((resolve, reject) => {
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
  
  
