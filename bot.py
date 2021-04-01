from discord.ext import commands
from model.models import *
from tortoise import run_async

run_async(init_db())
allowedRoles = ['tBTC Contributors (Team)', 'Admin', ':european_castle: keep team', ':european_castle: keep admins']

bot = commands.Bot(command_prefix='!')


@commands.has_any_role(*allowedRoles)
@bot.command(name='relay.help')
async def relay_help(ctx):
    await ctx.send("**Relay commands:**\n"
                   "🧾`[!relay.list]` - The list of groups of relay channels\n"
                   "🆕`[!relay.create_group GROUP_NAME]` - Create new channel group\n"
                   "🖇`[!relay.add GROUP_ID]` - Add current channel to group with following ID\n"
                   "❌`[!relay.delete]` - Delete relay for the current channel\n"
                   "♻️`[!relay.delete_group GROUP_ID]` - Delete group and all related relays\n")
    return


@commands.has_any_role(*allowedRoles)
@bot.command(name='relay.list')
async def relay_list(ctx):
    if not (groups := await Group.all()):
        await ctx.send("The list of groups is empty. Create new group using `!relay.create_group 'GROUP_NAME'`🤖")
        return
    result_list = ""
    for group in groups:
        result_list += f"""**{group.name} [ID {str(group.id)}]**:\n"""
        if not (channels := await Channel.filter(group_id=group.id)):
            result_list += "```empty group```"
            continue
        channel_list = []
        for i in channels:
            channel = bot.get_channel(i.channel_id)
            channel_list.append(f"""{channel.guild.name}[{channel.name}]""")
        channel_list = ', '.join(channel_list)
        result_list += '```' + channel_list + '```\n'
    await ctx.send(result_list)


@commands.has_any_role(*allowedRoles)
@bot.command(name='relay.delete')
async def relay_delete(ctx):
    if channel := await Channel.get(channel_id=ctx.message.channel.id):
        await channel.delete()
    if webhook := await bot.fetch_webhook(webhook_id=channel.hook):
        await webhook.delete()
    await ctx.send("Relay successfully deleted!🤖")
    return


@commands.has_any_role(*allowedRoles)
@bot.command(name='relay.delete_group')
async def relay_delete_group(ctx, id_group: int):
    if not (group := await Group.get_or_none(id=id_group)):
        await ctx.send(f"""Group with ID {id_group} does not exist🤖️""")
        return
    channels = await Channel.filter(group=id_group)
    for channel in channels:
        if webhook := await bot.fetch_webhook(webhook_id=channel.hook):
            await webhook.delete()
        await channel.delete()
    await group.delete()
    await ctx.send(f"""Group with ID {id_group} was successful deleted🤖️""")
    return


@commands.has_any_role(*allowedRoles)
@bot.command(name='relay.create_group')
async def relay_create_group(ctx, arg):
    if not (group := await Group.get_or_none(name=arg)):
        group = await Group.create(name=arg)
        await ctx.send(f"""Group with name {group.name} was succesfully created with ID {group.id}🤖""")
    else:
        await ctx.send(f"""Group with name {group.name} already exists🤖""")
    return


@commands.has_any_role(*allowedRoles)
@bot.command(name='relay.add')
async def relay_add(ctx, id_group: int):
    channel = ctx.message.channel
    webhooks = await channel.webhooks()
    if not (group := await Group.get_or_none(id=id_group)):
        await ctx.send("The specified group does not exist🤖")
        return
    if any(i.name == "Relay" for i in webhooks):
        if exists := await group[0].channels.filter(channel_id=ctx.message.channel.id):
            await ctx.send("Relay already exists🤖")
            return
    webhook = await channel.create_webhook(name="Relay", reason="For Relay-Bot")
    relay = await Channel.create(name=channel.name, guild_id=ctx.message.guild.id, channel_id=ctx.message.channel.id,
                                 group_id=id_group, hook=webhook.id)
    await webhook.send('Relay successfully created🤖')


@bot.listen('on_message')
async def relay_processor(message):
    if message.author.bot is True or message.content.startswith('!relay'):
        return
    user = bot.get_user(message.author.id)
    if channel := await Channel.get_or_none(channel_id=message.channel.id):
        channels = await Channel.filter(group=channel.group_id)
        for i in channels:
            if i.channel_id == message.channel.id:
                continue
            webhook = await bot.fetch_webhook(i.hook)
            files = [await pp.to_file() for pp in message.attachments]
            await webhook.send(username=user.name + ' | ' + message.channel.guild.name, content=message.content,
                               avatar_url=user.avatar_url, files=files)




if __name__ == "__main__":
    bot.loop.run_until_complete(Tortoise.init(db_url='sqlite://relays.sqlite3', modules={'models': ['model.models']}))
    bot.run(config.TOKEN)