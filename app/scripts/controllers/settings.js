'use strict';

angular.module('auctionItemsApp').controller('SettingsCtrl', ['$scope', 'Post',
  function ($scope, Post) {
      $scope.base_url = "/settings";
      $scope.data = {operation_success: false};
      $scope.result = "";

      $scope.loadSettings = function(){
          Post.getSettings().then(function(data){
              $scope.data = data;
          });
      };
      $scope.saveSettings = function(){
          $scope.data.operation_success = "wait...";
          var params = $scope.data;
          Post.saveSettings(params).then(function(data){
              $scope.data = data;
          });
      };
      $scope.loadSettings();
}]);
