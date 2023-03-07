odoo.define('oi_pdf_viewer.PDFController', function (require) {
"use strict";

var BasicController = require('web.BasicController');

var PDFController = BasicController.extend({
    
	init: function (parent, model, renderer, params) {
        this._super.apply(this, arguments);
        
        this.searchable = false;
        this.searchViewHidden = true;
        this.isMultiRecord = false;
    },
    
    renderPager : function () {
    	
    },

    _getPagingInfo: function (state) {
    	return {};
    }

});

return PDFController;

});