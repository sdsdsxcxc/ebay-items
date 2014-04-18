'use strict';

angular.module('auctionItemsApp')
  .directive('topMenu', ['$location', 'Global', function($location, Global){
    return {
      template: '<nav ng-cloak>'+
            '<a href="#/" ng-class="navClass(\'home\')">Home</a>'+
            '<a href="#/settings" ng-show="globals.is_current_user_admin" ng-class="navClass(\'settings\')">Settings</a>'+
            '<a href="#/about" ng-class="navClass(\'about\')">About</a>'+
            '</nav>',
      restrict: 'AEC',
      controller: function($scope, $element){
        $scope.is_current_user_admin = Global.is_current_user_admin;
        // highlighting of navigation bar
        $scope.navClass = function (page) {
            var currentRoute = $location.path().substring(1) || 'home';
            return (page === currentRoute) ? 'active' : '';
        };

      }
    };
  }]);
