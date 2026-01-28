/** @odoo-module **/

import { jsonrpc } from "@web/core/network/rpc_service";

document.addEventListener('DOMContentLoaded', () => {
    const btnSend = document.getElementById('btn_send');
    const chatInput = document.getElementById('chat_input');
    const chatMessages = document.getElementById('chat_messages');

    if (btnSend && chatInput) {
        btnSend.addEventListener('click', async () => {
            const message = chatInput.value.trim();
            if (!message) return;

            chatInput.value = '';

            try {
                const result = await jsonrpc('/my/community/chat/send', {
                    message: message
                });

                if (result.status === 'success') {
                    // Append user message
                    const userMsgHtml = `
                        <div class="mb-3 d-flex justify-content-end">
                            <div class="p-2 rounded bg-primary text-white" style="max-width: 80%;">
                                <small class="d-block font-weight-bold">${result.author}</small>
                                <span>${result.message}</span>
                            </div>
                        </div>
                    `;
                    chatMessages.insertAdjacentHTML('beforeend', userMsgHtml);
                    chatMessages.scrollTop = chatMessages.scrollHeight;

                    // Reload to show AI response if triggered, or just wait for bus
                    // For this demo, we'll just reload the messages after a short delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                }
            } catch (error) {
                console.error("Chat Error:", error);
            }
        });
    }
});
