// 사용자의 위치 정보 가져오기
function getLocation() {
    if (navigator.geolocation) {
        const options = {
            enableHighAccuracy: true,
            timeout: 5000,
            maximumAge: 0
        };
        navigator.geolocation.getCurrentPosition(showPosition, showError, options);
    } else {
        alert("이 브라우저는 위치 정보를 지원하지 않습니다.");
    }
}

// 위치 정보를 폼에 표시
function showPosition(position) {
    document.getElementById("my_latitude").value = position.coords.latitude;
    document.getElementById("my_longitude").value = position.coords.longitude;
    console.log("위도:", position.coords.latitude, "경도:", position.coords.longitude);
}

// 위치 정보 오류 처리
function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("사용자가 위치 정보 요청을 거부했습니다.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("위치 정보를 사용할 수 없습니다.");
            break;
        case error.TIMEOUT:
            alert("위치 정보 요청 시간이 초과되었습니다.");
            break;
        case error.UNKNOWN_ERROR:
            alert("알 수 없는 오류가 발생했습니다.");
            break;
    }
}

// 폼 제출 전 위치 정보 유효성 검사
function validateForm() {
    var latitude = document.getElementById("my_latitude").value;
    var longitude = document.getElementById("my_longitude").value;
    if (latitude === "" || longitude === "") {
        alert("위치 정보를 가져오는 중입니다. 잠시 후 다시 시도해주세요.");
        return false;
    }
    return true;
}
