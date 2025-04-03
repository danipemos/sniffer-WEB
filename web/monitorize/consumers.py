import asyncio
import paramiko
import re
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class SSHConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.device_id = self.scope['url_route']['kwargs']['device_id']
        self.ssh_client = None
        self.channel = None

        # Obtener los detalles del dispositivo
        from .models import Device
        self.device = await sync_to_async(Device.objects.get)(id=self.device_id)

        try:
            # Configurar la conexión SSH
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(
                hostname=self.device.ip,
                username=self.device.username,
                password=self.device.password
            )

            # Abrir un canal interactivo
            self.channel = self.ssh_client.invoke_shell(term='xterm-256color', width=120, height=40)
            self.channel.settimeout(0.0)
            await self.accept()

            # Leer la salida inicial del shell
            asyncio.create_task(self.read_from_channel())
        except Exception as e:
            await self.send(f"Error: {str(e)}")
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
                await self.send(output)  # Enviar la salida al cliente sin filtrar
            await asyncio.sleep(0.1)
