var myApp = angular.module('MyApp', ['ui.bootstrap', 'perfect_scrollbar', 'ngRoute', 'wu.masonry']);

myApp.config(['$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {
        $routeProvider.
          when('/', {
            templateUrl: 'partials/main.html',
            controller: 'MainController'
          }).
          when('/settings', {
            templateUrl: 'partials/settings.html',
            controller: 'SettingsController'
          }).
          when('/about', {
            templateUrl: 'partials/about.html',
            controller: 'MainController'
          }).
          otherwise({
            redirectTo: '/'
          });
          // $locationProvider.html5Mode(true);
    }
]);
// myApp.value("GlobalConfig",{
    // pageSize: 40,
    // baseUrl: "/PersonActions?action=list&category=default&",
    // defaultPicture: "/images/ebay_market_182x76.gif"
// });