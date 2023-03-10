import os
import pandas as pd
import dotenv
from telethon import TelegramClient, functions
from telethon.tl.types import InputUserEmpty, InputPeerChannel, InputUser
import asyncio

dotenv.load_dotenv()

chat_id = os.getenv('CHANNEL_CHAT_ID')
api_id = os.getenv('API_ID')
api_hash = os.getenv("API_HASH")
user_id = int(os.getenv('USER_CHAT_ID'))

client = TelegramClient('test', int(api_id), api_hash)


async def get_invite_importers():
    await client.start()
    answer = []
    response = await client.get_entity(int(chat_id))
    user_account = await client.get_entity(user_id)
    links = []
    from telethon.tl.types import ChannelParticipantsAdmins
    async for user in client.iter_participants(response.id, filter=ChannelParticipantsAdmins):
        l = await client(functions.messages.GetExportedChatInvitesRequest(
            admin_id=InputUser(access_hash=user.access_hash, user_id=user.id),
            limit=100000,
            peer=InputPeerChannel(access_hash=response.access_hash, channel_id=response.id)
        ))
        links += l.invites

    for link in links:
        link = link.link
        print(link)
        result = await client(functions.messages.GetChatInviteImportersRequest(
            limit=100000,
            link=link,
            offset_date=None,
            offset_user=InputUserEmpty(),
            peer=InputPeerChannel(access_hash=response.access_hash, channel_id=response.id)
        ))

        for user in result.users:
            user_info = user.to_dict()
            user_info['link'] = link
            user_info['user_id'] = result.importers[0].user_id
            user_info['date'] = result.importers[0].date
            user_info['date'] = user_info['date'].replace(tzinfo=None)
            answer.append(user_info)
    await client.disconnect()
    df = pd.DataFrame(answer)
    df.to_excel('result.xlsx', index=False)


loop = asyncio.get_event_loop()
result = loop.run_until_complete(get_invite_importers())
print(result)
