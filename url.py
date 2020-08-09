from uniborg.util import admin_cmd

@borg.on(admin_cmd(pattern=".url ?(.*)", allow_sudo=True))
async def url(event):
	uinp = event.pattern_match.group(1)

	if not uinp:
		get = await event.get_reply_message()
		if not get:
			await event.delete()
			return
		uinp = get.text
	try:
		await event.client.send_file(event.chat_id, uinp)
	except:
		await event.edit("**Хуйня, не вышло**")
	await event.delete()
	

@borg.on(admin_cmd(pattern=".screen ?(.*)", allow_sudo=True))
async def screen(event):
	uinp = event.pattern_match.group(1)

	if not uinp:
		get = await event.get_reply_message()
		if not get:
			await event.delete()
			return
		uinp = get.text
	try:
		await event.client.send_file(event.chat_id, "http://api.screenshotmachine.com/?key=b645b8&size=X&url="+uinp)
	except:
		await event.edit("**Хуйня, не вышло**")
	await event.delete()
	

