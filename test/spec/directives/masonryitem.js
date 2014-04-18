'use strict';

describe('Directive: masonryItem', function () {

  // load the directive's module
  beforeEach(module('auctionItemsApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<masonry-item></masonry-item>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the masonryItem directive');
  }));
});
