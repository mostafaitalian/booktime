import asyncio
import json
import urllib
import aiohttp

import aioredis
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from channels.generic.http import AsyncHttpConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.shortcuts import get_object_or_404
from django.urls import reverse
from . import models
from django.confs import settings


class ChatConsumer(AsyncJsonWebsocketConsumer):
    EMPLOYEE = 2
    CLIENT = 1
    def get_user_type(self, user, order_id):
        order = get_object_or_404(models.Order, pk=order_id)
        if user.is_employee:
            order.last_spoken_to = user
            order.save()
            
            return ChatConsumer.EMPLOYEE
        elif order.user == user:
            return ChatConsumer.CLIENT
        else:
            return None    
    async def connect(self):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        self.room_group_name = "customer-service_%s" % self.order_id
        authorized = False
        if self.scope["user"].is_anonymous:
            await self.close()
        user_type = await database_sync_to_async(self.get_user_type)(self.scope["user"], self.order_id)
        if user_type == ChatConsumer.EMPLOYEE:
            authorized=True
        elif user_type == ChatConsumer.CLIENT:
            authorized = True
        else:
            await self.close()
        if authorized:
            self.r_conn = await aioredis.create_redis(settings.REDISURL)
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_join",
                    "username": self.scope["user"].get_full_name(),                    
                }
            )
    async def disconnect(self, code):
        if not self.scope["user"].is_anonymous:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_leave",
                    "username": self.scope["user"].get_full_name(),
                    
                }
            )
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive_json(self, content):
        typ = content.get("type")
        if typ == "message":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "username": self.scope["user"].get_full_name(),
                    "message": content["message"] + "\n"
                }
            )
        elif typ == "heartbeat":
            await self.r_conn.setex(
                "%s %s" % (self.room_group_name, self.scope["user"].email,), 10, "1"
            )   
    async def chat_join(self, event):
        await self.send_json(event)
    async def chat_leave(self, event):
        await self.send_json(event)
    async def chat_message(self, event):
        await self.send_json(event)    
class ChatNotifyConsumer(AsyncHttpConsumer):
    def is_employee_func(self, user):
        return not user.is_anonymous and user.is_employee 
    async def handle(self, body):
        is_employee = database_sync_to_async(is_employee_func)(self.scope['user'])
        if is_employee:
            await self.send_headers(
                headers=[
                    ("Cache-Control", "no-cache"), ("Content-Type", "text/event-stream"), ("Transfer-Encoding", "chunked")
                ]
            )
            self.is_streaming = True
            self.no_poll = (self.scope.get("query_string") == "nopoll")
            asyncio.get_event_loop().create_task(self.stream())
        else:
            raise StopConsumer("unthourized")
    async def stream(self):
        self.r_conn = await aioredis.create_redis(settings.REDIS_URL)
        while self.is_streaming:
            active_chats = await self.r_conn.keys("customer-service_*")
            presences = {}
            for i in active_chats:
                _, order_id, user_email = i.decode("utf8").split('_')
                if order_id in presences:
                    presences[order_id].append(user_email)
                else:
                    presences[order_id] = [user_email]
            data = []
            for order_id, emails in presences.items():
                data.append(
                    {
                        "link": reverse("main:cs_chatrooom", kwargs={"order_id": order_id}),
                        "text": "%s (%s)" % (order_id, ", ".join(emails))
                    }
                )
            payload = "data: %s\n\n" % json.dumps(data)
            if self.no_poll:
                await self.send_body(payload.encode('utf-8'))
                self.is_streaming = False
            else:
                await self.send_body(payload.encode("utf-8"), more_body=self.is_streaming)
            await asyncio.sleep(5)
    async def disconnect(self):
        self.is_streaming = False                        
class OrderTrackerConsumer(AsyncHttpConsumer):
    def verify_user(self, user, order_id):
        order = get_object_or_404(models.Order, pk=order_id)
        return user == order.user

    async def query_remote_server(self, order_id):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://www.pastepin.com/") as reps:
                return await reps.read()
    async def handle(self, body):
        self.order_id = self.scope["url_route"]["kwargs"]["order_id"]
        is_authorized = await database_sync_to_async(verify_user)(self.scope["user"], self.order_id)
        if is_authorized:
            payload = await self.query_remote_server(self.order_id)
            await self.send_response(200, payload)
        else:
            raise StopConsumer("you are not authorized")
