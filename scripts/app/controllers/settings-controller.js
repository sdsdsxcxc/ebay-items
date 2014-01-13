myApp.controller('SettingsController', ['$scope', '$routeParams', '$http', 'PostService',
    function($scope, $routeParams, $http, PostService){
        $scope.base_url = "/settings";
        $scope.data = {operation_success: false};
        $scope.result = "";
        
        $scope.loadSettings = function(){
            PostService.getSettings().then(function(data){
                $scope.data = data;
            });
        };
        $scope.saveSettings = function(){
            $scope.data.operation_success = "wait...";
            params = $scope.data;
            PostService.saveSettings(params).then(function(data){
                $scope.data = data;
            });
        };
        $scope.loadSettings();
    }
]);