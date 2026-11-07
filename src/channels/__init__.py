"""
Pacote de Canais de Comunicação do Vox AI.

Exporta as integrações oficiais com canais externos:
- Telegram Bot
- WhatsApp Cloud API / Webhook
- VoxChannelCore (Adaptador Unificado)
"""

from src.channels.core_adapter import VoxChannelCore, channel_core
from src.channels.telegram_bot import TelegramBot
from src.channels.whatsapp_bot import WhatsAppBot, whatsapp_bot

__all__ = [
    "VoxChannelCore",
    "channel_core",
    "TelegramBot",
    "WhatsAppBot",
    "whatsapp_bot",
]
