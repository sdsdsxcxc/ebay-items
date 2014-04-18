'use strict';

angular.module('auctionItemsApp').factory('Post', ['$http', '$q', '$location', 'Global',
  function ($http, $q, $location, Global) {
    return {
        list: function (keyword, page) {
            var defer = $q.defer();
            var startIndex = (page-1) * Global.pageSize;
            var params = {'PageSize': Global.pageSize,
                          'StartIndex': startIndex,
                          'keyword': keyword};
            $http.get(Global.baseUrl, {'params': params}).
                success(function (data) {
                    defer.resolve(data);
                }).error(function (data, status) {
                    defer.reject(status);
                });
            return defer.promise;
        },
        saveSettings: function (params) {
            var defer = $q.defer();
            $http({method: 'POST',
                   url: Global.settingsUrl,
                   data: params,
                   headers: {'Content-Type': 'application/x-www-form-urlencoded'}}).
                success(function (data) {
                    defer.resolve(data);
                }).error(function (data, status) {
                    defer.reject(status);
                });
            return defer.promise;
        },
        getSettings: function(){
            var defer = $q.defer();
            $http({method: 'GET', url: Global.settingsUrl}).
                success(function (data, status) {
                    if(typeof(data) == "object"){
                        defer.resolve(data);
                    }else{
                        // alert('hi');
                        defer.reject(status);
                        window.location.replace(Global.loginUrl)
                        // $location.url("/settings");
                    }
                }).error(function (data, status) {
                    defer.reject(status);
                    window.location.replace(Global.loginUrl)
                });
            return defer.promise;
        }
    }
  }]);
