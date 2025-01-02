var map;
var currentPosition;
var markers = [];
var infoWindows = [];

// 지도 초기화 및 현재 위치 표시 함수
function my_location_map() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            currentPosition = new naver.maps.LatLng(position.coords.latitude, position.coords.longitude);
            console.log("현재 위치:", currentPosition.toString());
            
            // 네이버 지도 생성
            map = new naver.maps.Map('map', {
                center: currentPosition,
                zoom: 14
            });

            // 현재 위치에 마커 추가
            new naver.maps.Marker({
                position: currentPosition,
                map: map,
                icon: {
                    content: '<div style="background-color:blue;width:20px;height:20px;border-radius:50%;"></div>',
                    anchor: new naver.maps.Point(10, 10)
                }
            });

            showAllRestaurants();
        }, function(error) {
            console.error("위치 정보를 가져오는 데 실패했습니다:", error);
        });
    } else {
        alert("이 브라우저는 위치 정보를 지원하지 않습니다.");
    }
}

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

// 모든 식당 표시 함수
function showAllRestaurants() {
    var restaurantList = document.getElementById('restaurant-list');
    if (!restaurantList) {
        console.error("'restaurant-list' 요소를 찾을 수 없습니다.");
        return;
    }
    restaurantList.innerHTML = '<h2>주변 3km 내 식당 목록</h2>';

    if (!restaurants || restaurants.length === 0) {
        console.error("식당 데이터가 없습니다.");
        restaurantList.innerHTML += '<p>주변에 식당이 없습니다.</p>';
        return;
    }

    let restaurantsInRange = 0;

    restaurants.forEach(function(restaurant, index) {
        if (restaurant.lat && restaurant.lng) {
            var restaurantPosition = new naver.maps.LatLng(restaurant.lat, restaurant.lng);
            var distance = map.getProjection().getDistance(currentPosition, restaurantPosition);

            var marker = new naver.maps.Marker({
                position: restaurantPosition,
                map: map,
                icon: {
                    content: createMarkerIcon(restaurant.name),
                    anchor: new naver.maps.Point(15, 20)
                }
            });

            markers.push(marker);

            naver.maps.Event.addListener(marker, 'click', function() {
                window.location.href = `/board/info2/${restaurant.id}/`;
            });

            naver.maps.Event.addListener(marker, 'mouseover', function() {
                marker.setIcon({
                    content: createMarkerIcon(restaurant.name, true),
                    anchor: new naver.maps.Point(15, 20)
                });
            });

            naver.maps.Event.addListener(marker, 'mouseout', function() {
                marker.setIcon({
                    content: createMarkerIcon(restaurant.name),
                    anchor: new naver.maps.Point(15, 20)
                });
            });

            // 3km 이내 식당만 목록에 추가
            if (distance <= 3000) {
                restaurantsInRange++;
                var listItem = document.createElement('div');
                listItem.className = 'restaurant-item';
                listItem.innerHTML = `<strong>${restaurant.name}</strong><br>${restaurant.address}<br>거리: ${Math.round(distance)}m`;
                listItem.onclick = function() {
                    window.location.href = `/board/info2/${restaurant.id}/`; 
                };
                restaurantList.appendChild(listItem);
            }
        } else {
            console.warn(`식당 ${restaurant.name}의 위치 정보가 없습니다.`);
        }
    });

    if (restaurantsInRange === 0) {
        restaurantList.innerHTML += '<p>3km 내에 식당이 없습니다.</p>';
    }

    var listItems = Array.from(restaurantList.getElementsByClassName('restaurant-item'));
    listItems.sort((a, b) => {
        var distanceA = parseInt(a.innerHTML.split('거리: ')[1]);
        var distanceB = parseInt(b.innerHTML.split('거리: ')[1]);
        return distanceA - distanceB;
    });

    listItems.forEach(item => restaurantList.appendChild(item));
}

// 페이지 로드 시 지도 초기화
window.onload = my_location_map;