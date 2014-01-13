myApp.factory('PostService', ['$http', '$q', '$location', 'GlobalService', function ($http, $q, $location, GlobalService) {
    // var api_url = "/posts/";
    return {
        list: function (keyword, page) {
            var defer = $q.defer();
            var startIndex = (page-1) * GlobalService.pageSize;
		    var params = {'PageSize': GlobalService.pageSize,
		                  'StartIndex': startIndex,
		                  'keyword': keyword};
		    $http.get(GlobalService.baseUrl, {'params': params}).
                success(function (data, status, headers, config) {
                    defer.resolve(data);
                }).error(function (data, status, headers, config) {
                    defer.reject(status);
                });
            return defer.promise;
        },
        saveSettings: function (params) {
            var defer = $q.defer();
            $http({method: 'POST',
                   url: GlobalService.settingsUrl,
                   data: params,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                success(function (data, status, headers, config) {
                    defer.resolve(data);
                }).error(function (data, status, headers, config) {
                    defer.reject(status);
                });
            return defer.promise;
        },
        getSettings: function(){
            var defer = $q.defer();
            $http({method: 'GET', url: GlobalService.settingsUrl}).
                success(function (data, status, headers, config) {
                    // alert(status);
                    // alert(headers);
                    // alert(data);
                    // alert(Object.keys(config));
                    if(typeof(data) == "object"){
                        defer.resolve(data);
                    }else{
                        // alert('hi');
                        defer.reject(status);
                        window.location.replace(GlobalService.loginUrl)
                        // $location.url("/settings");
                    }
                }).error(function (data, status, headers, config) {
                    defer.reject(status);
                    window.location.replace(GlobalService.loginUrl)
                });
            return defer.promise;
        }
    }
}]);