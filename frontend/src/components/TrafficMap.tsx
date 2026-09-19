"use client";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
} from "react-leaflet";

import L from "leaflet";
import { useEffect } from "react";

import "leaflet/dist/leaflet.css";

interface TrafficJam {
  id: number;
  street: string;
  city: string;
  level: number;
  length_meters: number;
  speed_kmh: number;
  latitude: number;
  longitude: number;
  end_node: string | null;
  update_millis: number;
}

interface TrafficMapProps {
  jams: TrafficJam[];
  selectedJamId?: number | null;
  onSelectJam?: (jam: TrafficJam) => void;
}

function createMarkerIcon(level: number, selected: boolean) {
  let color = "#10b981";

  if (level >= 4) {
    color = "#ef4444";
  } else if (level === 3) {
    color = "#f97316";
  } else if (level === 2) {
    color = "#eab308";
  }

  return L.divIcon({
    className: "",
    html: `
      <div
        style="
          width: ${selected ? "24px" : "18px"};
          height: ${selected ? "24px" : "18px"};
          background: ${color};
          border: ${selected ? "4px" : "3px"} solid white;
          border-radius: 9999px;
          box-shadow: ${
            selected
              ? "0 0 0 5px rgba(15,23,42,0.18), 0 3px 12px rgba(0,0,0,0.4)"
              : "0 2px 8px rgba(0,0,0,0.35)"
          };
          transition: all 0.2s ease;
        "
      ></div>
    `,
    iconSize: selected ? [24, 24] : [18, 18],
    iconAnchor: selected ? [12, 12] : [9, 9],
    popupAnchor: [0, selected ? -14 : -10],
  });
}

function MapUpdater({
  jams,
  selectedJamId,
}: TrafficMapProps) {
  const map = useMap();

  useEffect(() => {
    if (!jams.length) {
      map.setView([24.8607, 67.0011], 11);
      return;
    }

    const validJams = jams.filter(
      (jam) =>
        Number.isFinite(jam.latitude) &&
        Number.isFinite(jam.longitude),
    );

    if (!validJams.length) {
      return;
    }

    const selectedJam = selectedJamId
      ? validJams.find((jam) => jam.id === selectedJamId)
      : null;

    if (selectedJam) {
      map.flyTo(
        [selectedJam.latitude, selectedJam.longitude],
        15,
        {
          duration: 0.8,
        },
      );

      return;
    }

    const bounds = L.latLngBounds(
      validJams.map((jam) => [
        jam.latitude,
        jam.longitude,
      ]),
    );

    map.fitBounds(bounds, {
      padding: [50, 50],
      maxZoom: 14,
    });
  }, [jams, selectedJamId, map]);

  return null;
}

function getSeverity(level: number) {
  if (level >= 4) {
    return "Severe";
  }

  if (level === 3) {
    return "Heavy";
  }

  if (level === 2) {
    return "Moderate";
  }

  return "Light";
}

function formatLength(meters: number) {
  if (meters >= 1000) {
    return `${(meters / 1000).toFixed(1)} km`;
  }

  return `${Math.round(meters)} m`;
}

export default function TrafficMap({
  jams,
  selectedJamId = null,
  onSelectJam,
}: TrafficMapProps) {
  return (
    <MapContainer
      center={[24.8607, 67.0011]}
      zoom={11}
      scrollWheelZoom={true}
      className="h-full w-full"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapUpdater
        jams={jams}
        selectedJamId={selectedJamId}
      />

      {jams.map((jam) => (
        <Marker
          key={jam.id}
          position={[
            jam.latitude,
            jam.longitude,
          ]}
          icon={createMarkerIcon(
            jam.level,
            selectedJamId === jam.id,
          )}
          eventHandlers={{
            click: () => {
              onSelectJam?.(jam);
            },
          }}
        >
          <Popup>
            <div className="min-w-[220px]">
              <h3 className="text-base font-bold">
                {jam.street || "Unnamed Road"}
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                {jam.city || "Karachi"}
                {jam.end_node
                  ? ` • ${jam.end_node}`
                  : ""}
              </p>

              <div className="mt-3 space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <span>Severity</span>
                  <strong>
                    {getSeverity(jam.level)}
                  </strong>
                </div>

                <div className="flex justify-between gap-4">
                  <span>Level</span>
                  <strong>{jam.level}</strong>
                </div>

                <div className="flex justify-between gap-4">
                  <span>Speed</span>
                  <strong>
                    {jam.speed_kmh.toFixed(1)} km/h
                  </strong>
                </div>

                <div className="flex justify-between gap-4">
                  <span>Jam Length</span>
                  <strong>
                    {formatLength(
                      jam.length_meters,
                    )}
                  </strong>
                </div>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}