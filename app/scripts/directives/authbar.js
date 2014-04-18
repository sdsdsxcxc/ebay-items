'use strict';

angular.module('auctionItemsApp')
  .directive('authBar', ['Global', function (Global) {
    return {
      templateUrl: 'views/templates/authbar.html',
      restrict: 'AEC',
      link: function postLink(scope, element, attrs) {
          Global.is_authenticated = attrs["user"];
          Global.is_current_user_admin = attrs["isAdmin"];
          Global.loginUrl = attrs["loginUrl"];
          Global.logoutUrl = attrs["logoutUrl"];
          scope.globals = Global;
          scope.name = (attrs["user"] == "false") ? "Anonymous" : attrs["user"];
      }
    };
  }]);
