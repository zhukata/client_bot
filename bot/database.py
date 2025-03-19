from django_app.clients.models import Client


async def create_client(tg_id, tg_username):
    client = await Client.objects.acreate(tg_id=tg_id, username=tg_username)
    await client.asave()
    return client

async def get_client(tg_id):
    return await Client.objects.aget(tg_id=tg_id)
