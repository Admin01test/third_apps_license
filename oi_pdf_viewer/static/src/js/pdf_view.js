odoo.define('oi_pdf_viewer.PDFView', function (require) {
    'use strict';

    var BasicView = require('web.BasicView');
    var core = require('web.core');
    var utils = require('web.utils');
    var config = require('web.config');
    var view_registry = require('web.view_registry');

    var PDFModel = require('oi_pdf_viewer.PDFModel');
    var PDFRenderer = require('oi_pdf_viewer.PDFRenderer');
    var PDFController = require('oi_pdf_viewer.PDFController');

    var _lt = core._lt;

    var PDFView = BasicView.extend({
        accesskey: 'p',
        display_name: _lt('PDF'),
        icon: 'fa-file-pdf-o',
        withSearchBar : false,
        withSearchPanel : false,
        searchMenuTypes : [],
        jsLibs: [
        	
        ],
        cssLibs: [
            '/oi_pdf_viewer/static/src/css/custom.css'
        ],
        config: _.extend({}, BasicView.prototype.config, {
            Model: PDFModel,
            Renderer: PDFRenderer,
            Controller: PDFController,
        }),
        viewType: 'pdf',
        
        init: function (viewInfo, params) {
            this._super.apply(this, arguments);

            var arch = viewInfo.arch;
            var attrs = arch.attrs;
            var fields = viewInfo.fields;


        },
    });
    
    view_registry.add('pdf', PDFView);

    return PDFView;

});