'use client';

import { MapContainer, TileLayer, Marker, useMap, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect } from 'react';

const CARLOW_BOUND = {
    minLat: 52.48,
    maxLat: 52.92,
    minLng: -7.15,
    maxLng: -6.49
};

// Leaflet
const bounds: L.LatLngBoundsExpression = [
    [CARLOW_BOUND.minLat, CARLOW_BOUND.minLng],
    [CARLOW_BOUND.maxLat, CARLOW_BOUND.maxLng]
];

const DefaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});
L.Marker.prototype.options.icon = DefaultIcon;

function ClickHandler({ setPosition} : { setPosition: (pos: [number, number]) => void}){
    useMapEvents({
        click(e){
            const { lat, lng } = e.latlng;
            if( lat >= CARLOW_BOUND.minLat && lat <= CARLOW_BOUND.maxLat &&
                lng >= CARLOW_BOUND.minLng && lng <= CARLOW_BOUND.maxLng
            ) setPosition([e.latlng.lat, e.latlng.lng]);
        },
    });
    return null;
}

interface MapModal {
  position: [number, number];
  setPosition: (pos: [number, number]) => void;
  isSearch: boolean;
}

export default function MapContent({ position, setPosition, isSearch }: MapModal) {
  return (
    <MapContainer center={position} zoom={13} style={{ height: '100%', width: '100%' }} zoomControl={false}
    maxBounds = {bounds}
    maxBoundsViscosity={1.0}
    minZoom={10}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <ClickHandler setPosition={setPosition} />
      <Marker position={position} />
      <MapUpdater center={position} isSearch={isSearch}/>
    </MapContainer>
  );
}

function MapUpdater({ center, isSearch }: { center: [number, number], isSearch: boolean }) {
  const map = useMap();
  useEffect(() => {
    if (isSearch) {
        map.flyTo(center, 15);
    } else{
        map.setView(center, map.getZoom());
   }
 }, [center, map, isSearch]);
  return null;
}