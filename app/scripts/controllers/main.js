'use strict';

angular.module('auctionItemsApp').controller('MainCtrl', ['$scope', '$http', '$location', '$window', 'Modal', 'Post', 'Global',
  function ($scope, $http, $location, $window, Modal, Post, Global) {
    $scope.globals = Global;
//    Global.loginUrl = document.querySelector( '.login' ).href || "";
    $scope.items = [];
    $scope.terms = [];
    $scope.busy = false;
    $scope.keyword = "";
    // pagination
    $scope.currentPage = 1;

    $scope.initialize = function (is_authenticated, is_current_user_admin) {
        $scope.globals.is_authenticated = is_authenticated;
        $scope.globals.is_current_user_admin = is_current_user_admin;
    };

    // highlighting of right bar
    $scope.rightBarClass = function (filter) {
        return (filter === $scope.keyword) ? 'active' : '';
    };

    $scope.setKeyword = function(search_term) {
        $scope.currentPage = 1;
        $scope.totalItems = 1;
        $scope.items = [];
        $scope.keyword = search_term;
        // $('.masonry').scroll();
        $scope.loadPage();
    };

    $scope.setPage = function (pageNo) {
        $scope.currentPage = pageNo;
        $scope.items = [];
        $scope.loadPage();
    };

    $scope.loadPage = function() {
        if ($scope.busy) return;
        $scope.busy = true;

        Post.list($scope.keyword, $scope.currentPage).then(function(items){
            $scope.totalItems = items.TotalRecordCount;
            for (var i = 0; i < items.Records.length; i++){
                if(items.Records[i].pictureURLSuperSize == ""){
                    items.Records[i].pictureURLSuperSize = $scope.globals.defaultPicture;
                }
                $scope.items.push(items.Records[i]);
            }
            $scope.terms = items.Terms;
            $scope.busy = false;
        });
    };

    $scope.openModal = function (item) {
        // var custName = $scope.customer.firstName + ' ' + $scope.customer.lastName;
        var modalOptions = {
            closeButtonText: 'Cancel',
            actionButtonText: 'Buy Item',
            bodyText: item.description,
            imgUrl: item.pictureURLSuperSize,
            headerText: item.price
        };

        Modal.showModal({}, modalOptions).then(function (result) {
            if(result == 'ok'){
                var win = $window.open(item.viewitem, '_blank');
                win.focus();
            }
        });
    };
    $scope.loadPage();

//    var $container = $('.myMasonry');
//    $container.imagesLoaded(function(){
//        // $container.masonry('reload');
//    });

  }]);
