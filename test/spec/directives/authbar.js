'use strict';

describe('Directive: authBar', function () {

  // load the directive's module
  beforeEach(module('auctionItemsApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<auth-bar></auth-bar>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the authBar directive');
  }));
});
