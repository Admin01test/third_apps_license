odoo.define('oi_action_file.FileDownload', function (require) {
"use strict";

var core = require('web.core');

var framework = require('web.framework');
var session = require('web.session');

var _t = core._t;
var _lt = core._lt;

var FileDownload = function (parent, action) {
    framework.blockUI();
    var self = parent;
    var blocked = !session.get_file({
        url: '/web/content',
        data: action.params,
        complete: framework.unblockUI,
        error: (error) => {
            self.call('crash_manager', 'rpc_error', error);
        },
    });
    if (blocked) {
        // AAB: this check should be done in get_file service directly,
        // should not be the concern of the caller (and that way, get_file
        // could return a promise)
        var message = _t('A popup window with your report was blocked. You ' +
                         'may need to change your browser settings to allow ' +
                         'popup windows for this page.');
        self.do_warn(_t('Warning'), message, true);
    }    
    return {
    	type : 'ir.actions.act_window_close'
    }
}

core.action_registry.add('file_download', FileDownload);

});