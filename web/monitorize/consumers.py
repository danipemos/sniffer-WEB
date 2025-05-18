import asyncio
import paramiko
import json
import io
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Device

class SSHConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.hostname = self.scope['url_route']['kwargs']['hostname']
        self.ssh_client = None
        self.channel = None

        # Accept the WebSocket connection FIRST
        await self.accept()

        # Obtener los detalles del dispositivo
        self.device = await sync_to_async(Device.objects.get)(hostname=self.hostname)

        private_key_str = self.device.ssh_private_key
        private_key = paramiko.RSAKey.from_private_key(io.StringIO(private_key_str))

        try:
            # Configurar la conexión SSH
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.device.ip,
                username="sniffer",
                pkey=private_key
            )

            # Abrir un canal interactivo
            self.channel = self.ssh_client.invoke_shell(term='xterm-256color', width=120, height=40)
            self.channel.settimeout(0.0)

            # Leer la salida inicial del shell
            asyncio.create_task(self.read_from_channel())
        except Exception as e:
            await self.send(text_data=f"Error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        if self.channel:
            self.channel.close()
        if self.ssh_client:
            self.ssh_client.close()

    async def receive(self, text_data):
        # Enviar cada tecla al canal SSH
        if self.channel:
            self.channel.send(text_data)

    async def read_from_channel(self):
        while True:
            if self.channel.recv_ready():
                output = self.channel.recv(1024).decode('utf-8')
                await self.send(text_data=output)  # Use text_data parameter here
            await asyncio.sleep(0.1)


class StatsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.hostname = self.scope['url_route']['kwargs']['hostname']
        self.stats_group_name = f"stats_{self.hostname}"

        # Unirse al grupo de WebSocket
        await self.channel_layer.group_add(self.stats_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo de WebSocket
        await self.channel_layer.group_discard(self.stats_group_name, self.channel_name)

    async def send_stats(self, event):
        # Enviar estadísticas al cliente
        stats = event['data']
        await self.send(text_data=json.dumps({'type': 'stats', 'data': stats}))


class FileConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.hostname = self.scope['url_route']['kwargs']['hostname']
        self.files_group_name = f"files_{self.hostname}"

        # Unirse al grupo de WebSocket
        await self.channel_layer.group_add(self.files_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo de WebSocket
        await self.channel_layer.group_discard(self.files_group_name, self.channel_name)

    async def new_file(self, event):
        # Enviar información del nuevo archivo al cliente
        file_data = event['data']
        await self.send(text_data=json.dumps({'type': 'new_file', 'data': file_data}))


class DeviceListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("devices", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("devices", self.channel_name)

    async def new_device(self, event):
        await self.send(text_data=json.dumps({
            "type": "new_device",
            "device": event["data"],
        }))
