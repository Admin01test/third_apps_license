odoo.define('oi_pdf_viewer.PDFRenderer', function (require) {
    'use strict';

    var BasicRenderer = require('web.BasicRenderer');
    var core = require('web.core');
    var QWeb = require('web.QWeb');
    var session = require('web.session');
    var utils = require('web.utils');
    var Widget = require('web.Widget');

    var qweb = core.qweb;

    var PDFRenderer = BasicRenderer.extend({
        className: 'o_pdf_view',
        /**
         * @override
         */
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.datasField = state.context.pdf_datasField || params.arch.attrs.datas  || 'datas';
        },
        /**
         * @override
         */
        _renderView: function () {        	
            var self = this;
            return this._super.apply(this, arguments)
            	.then(self._renderPDFViewer.bind(self))
            	;
            
        },
                
        _renderPDFViewer : function () {
           var url = null;
           var type = this.state.context.html ? "html" : "pdf";
           if (this.state.res_id) {
        	   url = _.str.sprintf("/web/content/%s/%s/%s/file.%s", this.state.model, this.state.res_id, this.datasField, type);
           }
           else {
        	   var docids = this.state.context.docids || this.state.context.active_ids;
        	   docids = _.str.join(",",docids);
        	   var report_name = this.state.context.report_name;        	   
        	   url = _.str.sprintf("/report/%s/%s/%s", type, report_name, docids);   
           }
           var src = null;           
           if (this.state.context.html) {
        	   src = url;
           }
           else {
        	   src = _.str.sprintf("/web/static/lib/pdfjs/web/viewer.html?file=%s", url);        	  
           }
           
           this.$el.html(qweb.render('ViewPDFViewer', {
        	   src : src
           }));
           
           var $iFrame = this.$('.o_view_pdfviewer_iframe');
           var self = this;
           
           $iFrame.on('load', function () {
               self.PDFViewerApplication = this.contentWindow.window.PDFViewerApplication;
           });
        }
    });

    return PDFRenderer;

});