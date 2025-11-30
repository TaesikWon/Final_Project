// frontend/src/components/MapView.jsx

import { useEffect, useRef } from "react";

function MapView({ apartments = [], radius = null }) {
  const mapRef = useRef(null);     // 지도 객체 저장
  const markersRef = useRef([]);   // 기존 마커 저장
  const circleRef = useRef(null);  // 기존 반경 원 저장

  // --------------------------------------------
  // 1) 네이버 지도 준비되면 지도 1회만 생성
  // --------------------------------------------
  useEffect(() => {
    if (!window.naver || !window.naver.maps) {
      console.warn("⚠ 네이버 지도 API가 아직 로드되지 않았습니다.");
      return;
    }

    // 지도 이미 생성돼 있으면 재생성 하지 않음
    if (!mapRef.current) {
      mapRef.current = new naver.maps.Map("map", {
        center: new naver.maps.LatLng(37.5946, 127.1290), // 구리시 중심
        zoom: 14,
      });
    }
  }, []);

  // --------------------------------------------
  // 2) 아파트 마커 및 반경 원 업데이트
  // --------------------------------------------
  useEffect(() => {
    if (!mapRef.current) return;

    const map = mapRef.current;

    // ✔ 기존 마커 제거
    markersRef.current.forEach((m) => m.setMap(null));
    markersRef.current = [];

    // ✔ 기존 반경 원 제거
    if (circleRef.current) {
      circleRef.current.setMap(null);
      circleRef.current = null;
    }

    // ------------------------
    //  아파트 마커 표시
    // ------------------------
    apartments.forEach((apt) => {
      if (!apt.lat || !apt.lng) return;

      const marker = new naver.maps.Marker({
        position: new naver.maps.LatLng(apt.lat, apt.lng),
        map,
        title: apt.apartment,
      });

      markersRef.current.push(marker);
    });

    // ------------------------
    //  반경 원 표시 (조건 기반)
    // ------------------------
    if (radius && apartments.length > 0) {
      const apt = apartments[0];

      circleRef.current = new naver.maps.Circle({
        map,
        center: new naver.maps.LatLng(apt.lat, apt.lng),
        radius: radius,
        strokeColor: "#1E90FF",
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: "#1E90FF",
        fillOpacity: 0.15,
      });
    }

  }, [apartments, radius]);

  return (
    <div
      id="map"
      style={{
        width: "100%",
        height: "400px",
        border: "1px solid #ddd",
        borderRadius: "8px",
      }}
    ></div>
  );
}

export default MapView;
