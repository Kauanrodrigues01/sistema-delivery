import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class OrdersConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket APENAS para o Dashboard (Admin).

    - Clientes NÃO precisam estar conectados ao WebSocket
    - Quando um cliente cria/cancela pedido, o servidor envia via group_send()
    - Apenas admins conectados ao dashboard recebem as notificações em tempo real
    """

    async def connect(self):
        # Inicializar group_name antes de qualquer verificação
        self.group_name = "orders_updates"

        # Verificar se o usuário está autenticado
        user = self.scope.get("user")

        logger.info(
            f"WebSocket connection attempt - "
            f"User: {user}, "
            f"Authenticated: {user.is_authenticated if user else False}, "
            f"Staff: {user.is_staff if user and user.is_authenticated else False}"
        )

        # Rejeitar se não autenticado ou anônimo
        if not user or user.is_anonymous:
            logger.warning(
                "WebSocket rejected - User not authenticated (dashboard requires login)"
            )
            await self.close(code=4003)
            return

        # Verificar se é staff (admin do dashboard)
        # IMPORTANTE: Apenas admins do dashboard precisam do WebSocket
        # Clientes criam pedidos via POST (checkout/views.py) sem WebSocket
        if not user.is_staff:
            logger.warning(
                f"WebSocket rejected - User '{user.username}' is not staff (dashboard only)"
            )
            await self.close(code=4003)
            return

        # Adicionar ao grupo de pedidos
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        logger.info(
            f"✅ WebSocket connected - Admin '{user.username}' joined '{self.group_name}' group"
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Remover do grupo apenas se foi adicionado (group_name existe e conexão foi aceita)
        if hasattr(self, "group_name"):
            user = self.scope.get("user")
            username = user.username if user and user.is_authenticated else "Anonymous"
            logger.info(
                f"WebSocket disconnected - User: {username}, Code: {close_code}"
            )
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Não precisamos processar mensagens do cliente para este caso
        pass

    # Receber mensagem de atualização de pedido
    async def order_update(self, event):
        # Enviar mensagem para WebSocket
        await self.send(
            text_data=json.dumps({"type": "order_update", "data": event["data"]})
        )

    # Receber mensagem de novo pedido
    async def new_order(self, event):
        # Enviar mensagem para WebSocket
        await self.send(
            text_data=json.dumps({"type": "new_order", "data": event["data"]})
        )
    
    # Receber mensagem de pedido cancelado pelo cliente
    async def order_cancelled(self, event):
        # Enviar mensagem para WebSocket
        await self.send(
            text_data=json.dumps({"type": "order_cancelled", "data": event["data"]})
        )

    async def order_payment_paid(self, event):
        # Enviar mensagem para WebSocket
        await self.send(
            text_data=json.dumps({"type": "order_payment_paid", "data": event["data"]})
        )

    async def order_payment_cancelled(self, event):
        # Enviar mensagem para WebSocket
        await self.send(
            text_data=json.dumps({"type": "order_payment_cancelled", "data": event["data"]})
        )

    # Receber mensagem de item adicionado
    async def order_item_added(self, event):
        # Enviar mensagem para WebSocket
        await self.send(
            text_data=json.dumps({"type": "order_item_added", "data": event["data"]})
        )

    # Receber mensagem de item removido
    async def order_item_removed(self, event):
        # Enviar mensagem para WebSocket
        await self.send(
            text_data=json.dumps({"type": "order_item_removed", "data": event["data"]})
        )
