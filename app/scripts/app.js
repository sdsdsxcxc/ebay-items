'use strict';

angular.module('auctionItemsApp', [
//  'ngCookies',
//  'ngResource',
//  'ngSanitize',
  'ngRoute',
  'ui.bootstrap',
  'perfect_scrollbar',
  'wu.masonry'
])
  .config(function ($routeProvider) {
    $routeProvider
      .when('/', {
        templateUrl: 'views/main.html',
        controller: 'MainCtrl'
      })
      .when('/settings', {
        templateUrl: 'views/settings.html',
        controller: 'SettingsCtrl'
      })
      .when('/about', {
        templateUrl: 'views/about.html',
        controller: 'AboutCtrl'
      })
      .otherwise({
        redirectTo: '/'
      });
  });
