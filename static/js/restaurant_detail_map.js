// 마커 아이콘 생성 함수
function createMarkerIcon(name, isHovered = false) {
    const color = isHovered ? '#FF69B4' : '#4B89DC';
    return `
        <div style="display: flex; align-items: center; background-color: white; padding: 5px 10px; border-radius: 20px; white-space: nowrap; border: 2px solid ${color}; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
            <div style="width: 10px; height: 10px; background-color: ${color}; border-radius: 50%; margin-right: 8px;"></div>
            <span style="font-weight: bold; color: #333;">${name}</span>
        </div>
    `;
}

// 식당 상세 페이지 지도 표시 함수
function restaurantMap(restaurantName, latitude, longitude) {
    var mapOptions = {
        center: new naver.maps.LatLng(latitude, longitude),
        zoom: 15
    };

    var map = new naver.maps.Map('map', mapOptions);

    // 식당 위치에 마커 추가
    var marker = new naver.maps.Marker({
        position: new naver.maps.LatLng(latitude, longitude),
        map: map,
        icon: {
            content: createMarkerIcon(restaurantName),
            anchor: new naver.maps.Point(15, 20)
        }
    });

    // 마커에 마우스오버 이벤트 추가
    naver.maps.Event.addListener(marker, 'mouseover', function() {
        marker.setIcon({
            content: createMarkerIcon(restaurantName, true),
            anchor: new naver.maps.Point(15, 20)
        });
    });

    // 마커에 마우스아웃 이벤트 추가
    naver.maps.Event.addListener(marker, 'mouseout', function() {
        marker.setIcon({
            content: createMarkerIcon(restaurantName),
            anchor: new naver.maps.Point(15, 20)
        });
    });
}