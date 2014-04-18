'use strict';

angular.module('auctionItemsApp')
  .service('Modal', ['$modal', '$window',
    function ($modal, $window) {
    // AngularJS will instantiate a singleton by calling "new" on this function
        var modalDefaults = {
            backdrop: true,
            keyboard: true,
            modalFade: true,
            templateUrl: 'views/modal.html',
            windowClass: 'md-effect-1 md-show'
        };

        var modalOptions = {
            closeButtonText: 'Close',
            actionButtonText: 'OK',
            headerText: 'Proceed?',
            bodyText: 'Perform this action?'
        };

        // resize modal window when it's needed
        var resize = function(){
            var wh = $( window ).height(),
                ww = $( window ).width();
            wh = ((wh<750) ? (wh-60) : 700);
            ww = ((ww<1350) ? (ww-60) : 1300);
//            alert("before wh="+wh+"; ww="+ww);
            // http://stackoverflow.com/questions/622122/how-can-i-change-the-css-class-rules-using-jquery/7810217#7810217
            $("<style type='text/css'> .scroller { height: "+wh+"px !important; width: "+ww+"px !important;} </style>")
                .appendTo("head");
            $("<style type='text/css'> .modal { height: "+wh+"px !important; width: "+ww+"px !important;} </style>")
                .appendTo("head");
            setTimeout(function() { $(".scroller").perfectScrollbar('update'); }, 50);
        };

        angular.element($window).bind('resize', resize);
        this.showModal = function (customModalDefaults, customModalOptions) {
            // alert("hi");
            if (!customModalDefaults) customModalDefaults = {};
            // customModalDefaults.backdrop = 'static';
            var modalInstance = this.show(customModalDefaults, customModalOptions);
            modalInstance.opened.then(resize);
            return modalInstance.result;
        };

        this.show = function (customModalDefaults, customModalOptions) {
            //Create temp objects to work with since we're in a singleton service
            var tempModalDefaults = {};
            var tempModalOptions = {};

            //Map angular-ui modal custom defaults to modal defaults defined in this service
            angular.extend(tempModalDefaults, modalDefaults, customModalDefaults);

            //Map modal.html $scope custom properties to defaults defined in this service
            angular.extend(tempModalOptions, modalOptions, customModalOptions);

            if (!tempModalDefaults.controller) {
                tempModalDefaults.controller = ['$scope', '$modalInstance', function ($scope, $modalInstance) {
                    $scope.modalOptions = tempModalOptions;
                    $scope.modalOptions.ok = function (result) {
                        $modalInstance.close('ok');
                    };
                    $scope.modalOptions.close = function (result) {
                        $modalInstance.close('cancel');
                    };
                }]
            }

            return $modal.open(tempModalDefaults);
        }
  }]);
