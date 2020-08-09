# requires: pydub
from pydub import AudioSegment
from pydub import effects
from .. import loader, utils
import io
import os
import requests
def register(cb):
	cb(AudioEditorMod())
class AudioEditorMod(loader.Module):
	"""AudioEditor"""
	strings = {'name': 'AudioEditor'}
	def __init__(self):
		self.name = self.strings['name']
		self._me = None
		self._ratelimit = []
	async def client_ready(self, client, db):
		self._db = db
		self._client = client
		self.me = await client.get_me()
	async def volupcmd(self, message):
		""".volup <reply to audio>
		    Увеличить громкость на 10dB
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Vol'им...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			audio = AudioSegment.from_file(fname).apply_gain(+10)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			audio = AudioSegment.from_file(fname).apply_gain(+10)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		m = io.BytesIO()
		await message.edit("Отправляем...")
		if v:
			m.name="voice.ogg" 
			audio.split_to_mono()
			audio.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="VolUp.mp3"
			audio.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
		os.remove(fname)
	async def voldwcmd(self, message):
		""".voldw <reply to audio>
		    Уменьшить громкость на 10dB
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Vol'им...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			audio = AudioSegment.from_file(fname).apply_gain(-10)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			audio = AudioSegment.from_file(fname).apply_gain(-10)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		m = io.BytesIO()
		await message.edit("Отправляем...")
		if v:
			m.name="voice.ogg" 
			audio.split_to_mono()
			audio.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="VolDown.mp3"
			audio.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
		os.remove(fname)
	async def revscmd(self, message):
		""".revs <reply to audio>
		    Развернуть аудио
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Reverse'им...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			audio = AudioSegment.from_file(fname)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			audio = AudioSegment.from_file(fname)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		rev = audio.reverse()
		audio = rev
		m = io.BytesIO()
		await message.edit("Отправляем...")
		if v:
			m.name="voice.ogg" 
			audio.split_to_mono()
			audio.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="Reversed.mp3"
			audio.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
		os.remove(fname)
	async def repscmd(self, message):
		""".reps <reply to audio>
		    Повторить аудио (2 раза подряд)
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Repeat'им...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			audio = AudioSegment.from_file(fname)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			audio = AudioSegment.from_file(fname)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		audio = audio * 2
		m = io.BytesIO()
		await message.edit("Отправляем...")
		if v:
			m.name="voice.ogg" 
			audio.split_to_mono()
			audio.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="Repeated.mp3"
			audio.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
		os.remove(fname)
	async def slowscmd(self, message):
		""".slows <reply to audio>
		    Замедлить аудио 0.5x
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Замедляем...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			audio = AudioSegment.from_file(fname)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			audio = AudioSegment.from_file(fname)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		sound = AudioSegment.from_file(fname)
		sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * 0.5)
    	})
		sound = sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
		await message.edit("Отправляем...")
		m = io.BytesIO()
		if v:
			m.name="voice.ogg" 
			audio.split_to_mono()
			sound.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="Slow.mp3"
			sound.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
	async def fastscmd(self, message):

		""".fasts <reply to audio>
		    Ускорить аудио 1.5x
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Ускоряем...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			audio = AudioSegment.from_file(fname)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			audio = AudioSegment.from_file(fname)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		sound = AudioSegment.from_file(fname)
		sound_with_altered_frame_rate = sound._spawn(sound.raw_data, overrides={
        "frame_rate": int(sound.frame_rate * 1.5)
    	})
		sound = sound_with_altered_frame_rate.set_frame_rate(sound.frame_rate)
		await message.edit("Отправляем...")
		m = io.BytesIO()
		if v:
			m.name="voice.ogg" 
			audio.split_to_mono()
			sound.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="Fast.mp3"
			sound.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
	async def leftscmd(self, message):
		""".lefts <reply to audio>
		    Весь звук в левый канал
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Pan'им...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			sound = AudioSegment.from_file(fname)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			sound = AudioSegment.from_file(fname)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		sound = AudioSegment.from_file(fname)
		sound = effects.pan(sound, -1.0)
		await message.edit("Отправляем...")
		m = io.BytesIO()
		if v:
			m.name="voice.ogg" 
			sound.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="Left.mp3"
			sound.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
	async def rightscmd(self, message):
		""".rights <reply to audio>
		    Весь звук в правый канал
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Pan'им...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			sound = AudioSegment.from_file(fname)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			sound = AudioSegment.from_file(fname)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		sound = AudioSegment.from_file(fname)
		sound = effects.pan(sound, +1.0)
		await message.edit("Отправляем...")
		m = io.BytesIO()
		if v:
			m.name="voice.ogg" 
			sound.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="Right.mp3"
			sound.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
	async def normscmd(self, message):
		""".norms <reply to audio>
		    Нормализовать звук (Из тихого - нормальный)
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Нормализуем звук...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			audio = AudioSegment.from_file(fname)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			audio = AudioSegment.from_file(fname)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		sound = AudioSegment.from_file(fname)
		sound = effects.normalize(sound)
		await message.edit("Отправляем...")
		m = io.BytesIO()
		if v:
			m.name="voice.ogg" 
			audio.split_to_mono()
			sound.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="Normalized.mp3"
			sound.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
	async def byrobertscmd(self, message):
		""".byroberts <reply to audio>
		    Добавить в конец аудио "Directed by Robert B Weide"
		"""
		v = False
		reply = await message.get_reply_message()
		if not reply:
			await message.edit("А где реплай?")
			return
		await message.edit("Скачиваем...")
		fname = await message.client.download_media(message=reply.media)
		await message.edit("Делаем магию...")
		if fname.endswith(".oga") or fname.endswith(".ogg"):
			v = True
			audio = AudioSegment.from_file(fname)
		elif fname.endswith(".mp3") or fname.endswith(".m4a") or fname.endswith(".wav"):
			audio = AudioSegment.from_file(fname)
		else:
			await message.edit("<b>Unsupported format!</b>")
			os.remove(fname)
			return
		if os.path.isfile("directed.mp3") == False:
			open("directed.mp3", "wb").write(requests.get("https://raw.githubusercontent.com/GitAlterHell/Modules-ftg/master/directed.mp3").content)
		audio.export("temp.mp3", format="mp3")
		os.remove(fname)
		out = AudioSegment.empty()
		out += AudioSegment.from_file("temp.mp3")
		out += AudioSegment.from_file("directed.mp3").apply_gain(+10)
		await message.edit("Отправляем...")
		m = io.BytesIO()
		if v:
			m.name="voice.ogg" 
			audio.split_to_mono()
			out.export(m, format="ogg", bitrate="64k", codec="libopus")
			await message.client.send_file(message.to_id, m, reply_to=reply.id, voice_note=True)
		else:
			m.name="DirectedAudio.mp3"
			out.export(m, format="mp3")
			await message.client.send_file(message.to_id, m, reply_to=reply.id)
		await message.delete()
		os.remove("temp.mp3")
		os.remove("directed.mp3")