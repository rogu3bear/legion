class BaseAgent:
    def __init__(self, name, client, channel_id):
        self.name = name
        self.client = client
        self.channel_id = channel_id

    async def post_to_discord(self, message):
        channel = self.client.get_channel(self.channel_id)
        if channel:
            await channel.send(f"[{self.name}]: {message}")

    async def self_assess(self):
        await self.post_to_discord("[Assessment] This is a placeholder self-assessment.") 