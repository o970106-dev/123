/** @odoo-module **/
import { Component, useState, onMounted, onWillUnmount } from "@odoo/owl";

export class ModifierDialog extends Component {
    setup() {
        const lastIds = JSON.parse(localStorage.getItem("beverage_last_selection_ids") || "{}");

        const sweetnessLines = this.props.configLines.filter(l => l.attribute_type === 'sweetness');
        const temperatureLines = this.props.configLines.filter(l => l.attribute_type === 'temperature');
        const sizeLines = this.props.configLines.filter(l => l.attribute_type === 'size');

        this.state = useState({
            tab: sweetnessLines.length ? "sweetness" : (sizeLines.length ? "size" : "temperature"),
            sweetness: sweetnessLines.find(l => l.id === lastIds.sweetness) || sweetnessLines.find(l => l.selected) || null,
            temperature: temperatureLines.find(l => l.id === lastIds.temperature) || temperatureLines.find(l => l.selected) || null,
            size: sizeLines.find(l => l.id === lastIds.size) || sizeLines.find(l => l.selected) || null,
            canConfirm: false,
            timer: null,
        });

        this.sweetnessLines = sweetnessLines;
        this.temperatureLines = temperatureLines;
        this.sizeLines = sizeLines;

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
        const needsSweetness = this.sweetnessLines.length > 0;
        const needsTemperature = this.temperatureLines.length > 0;
        const needsSize = this.sizeLines.length > 0;

        this.state.canConfirm = (!needsSweetness || this.state.sweetness) &&
                               (!needsTemperature || this.state.temperature) &&
                               (!needsSize || this.state.size);
    }
    _startAutoClose() {
        if (this.state.timer) clearTimeout(this.state.timer);
        this.state.timer = setTimeout(() => this.props.close?.(), 15000); // 15s for data-driven
    }
    onInteract() { this._startAutoClose(); }
    onPick(group, line) {
        this.state[group] = line;
        this._updateConfirm();
        this.onInteract();
    }
    onReset() {
        this.state.sweetness = this.sweetnessLines.find(l => l.selected) || null;
        this.state.temperature = this.temperatureLines.find(l => l.selected) || null;
        this.state.size = this.sizeLines.find(l => l.selected) || null;
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
