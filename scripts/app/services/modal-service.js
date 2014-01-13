myApp.service('modalService', ['$modal', '$window', 
    function ($modal, $window) {
        var modalDefaults = {
            backdrop: true,
            keyboard: true,
            modalFade: true,
            templateUrl: 'partials/modal.html',
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
            // alert("wh="+wh+"; ww="+ww);
            setTimeout(function() { $(".scroller").height(wh); }, 10);
            setTimeout(function() { $(".scroller").width(ww); }, 10);
            
            // setTimeout(function() { $(".modal-img").css('max-width', $(".left-bar").width()); }, 10);
            setTimeout(function() { $(".scroller").perfectScrollbar('update'); }, 10);
        };
        angular.element($window).bind('resize', function(){
            resize();
        });

        this.showModal = function (customModalDefaults, customModalOptions) {
            // alert("hi");
            if (!customModalDefaults) customModalDefaults = {};
            // customModalDefaults.backdrop = 'static';
            var result = this.show(customModalDefaults, customModalOptions); 
            resize();
            return result;
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
                tempModalDefaults.controller = function ($scope, $modalInstance) {
                    $scope.modalOptions = tempModalOptions;
                    $scope.modalOptions.ok = function (result) {
                        $modalInstance.close('ok');
                    };
                    $scope.modalOptions.close = function (result) {
                        $modalInstance.close('cancel');
                    };

					// +++
					// var overlay = document.querySelector( '.md-overlay' );
					// var modal = document.querySelector( '#modal-1' );
					// var close = modal.querySelector( '.md-close' );
					// classie.add( modal, 'md-show' );
					// overlay.removeEventListener( 'click', function(){classie.remove( document.querySelector( '#modal-1' ), 'md-show' );} );
					// overlay.addEventListener( 'click', function(){classie.remove( document.querySelector( '#modal-1' ), 'md-show' );} );
					// close.addEventListener( 'click', function() {classie.remove( document.querySelector( '#modal-1' ), 'md-show' );} );
					// ---

                }
            }

            return $modal.open(tempModalDefaults).result;
        }
    }]);
