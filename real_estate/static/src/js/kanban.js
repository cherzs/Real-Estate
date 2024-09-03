odoo.define('estate.property.estate_property_kanban', function (require) {
    'use strict';

    const KanbanView = require('web.KanbanView');
    const core = require('web.core');
    const _t = core._t;

    KanbanView.include({
        events: _.extend({}, KanbanView.prototype.events, {
            'click .btn-primary': '_onMarkAsSold',
            'click .btn-secondary': '_onCancel',
        }),

        _onMarkAsSold: function (ev) {
            ev.preventDefault();
            const recordId = $(ev.currentTarget).closest('.oe_kanban_global_click').data('id');
            this._rpc({
                model: 'estate.property',
                method: 'action_sold',
                args: [recordId],
            }).then(() => {
                this.reload();
            }).catch(error => {
                this.do_warn(_t("Error"), error.data.message);
            });
        },

        _onCancel: function (ev) {
            ev.preventDefault();
            const recordId = $(ev.currentTarget).closest('.oe_kanban_global_click').data('id');
            this._rpc({
                model: 'estate.property',
                method: 'action_cancel',
                args: [recordId],
            }).then(() => {
                this.reload();
            }).catch(error => {
                this.do_warn(_t("Error"), error.data.message);
            });
        },
    });
});