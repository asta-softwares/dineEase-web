from channels.generic.websocket import AsyncWebsocketConsumer
import json

# For Restaurant Owners
class RestaurantOrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.restaurant_id = self.scope['url_route']['kwargs']['restaurant_id']
        self.group_name = f"restaurant_{self.restaurant_id}"

        # Join the restaurant group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the restaurant group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_new_order(self, event):
        await self.send(text_data=json.dumps({
            'status': event['status'],
            'message': 'New Order Received',
            'order_id': event['order_id'],
            'order_details': event['order_details'],
        }))


# For Customers
class OrderStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"order_{self.order_id}"

        # Join the order group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the order group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_order_status(self, event):
        await self.send(text_data=json.dumps({
            'message': 'Order Status Updated',
            'status': event['status'],
        }))
