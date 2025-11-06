/** @odoo-module **/
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";

export class ModifierDialog extends Component {
    setup() {
        const last = JSON.parse(localStorage.getItem("beverage_last_selection") || "{}");
        this.state = useState({
            tab: "sweetness",
            sweetness: last.sweetness || null,
            temperature: last.temperature || null,
            size: last.size || null,
            canConfirm: false,
            timer: null,
        });

        onMounted(() => {
            this._updateConfirm();
            this._startAutoClose();
            setTimeout(() => document.getElementById("modifierDialogTitle")?.focus(), 0);
        });
        onWillUnmount(() => {
            if (this.state.timer) clearTimeout(this.state.timer);
        });
    }

    _updateConfirm() {
        this.state.canConfirm = !!(this.state.sweetness && this.state.temperature && this.state.size);
    }
    _startAutoClose() {
        if (this.state.timer) clearTimeout(this.state.timer);
        this.state.timer = setTimeout(() => this.props.close?.(), 10000);
    }
    onInteract() { this._startAutoClose(); }
    onPick(group, value) { this.state[group] = value; this._updateConfirm(); this.onInteract(); }
    onReset() {
        this.state.sweetness = null;
        this.state.temperature = null;
        this.state.size = null;
        this._updateConfirm();
        this.onInteract();
    }
    onConfirm() {
        if (!this.state.canConfirm) return;
        this.props.onConfirm?.({
            sweetness: this.state.sweetness,
            temperature: this.state.temperature,
            size: this.state.size,
        });
        this.props.close?.();
    }
}

ModifierDialog.template = "pos_beverage_modifier.ModifierDialog";

