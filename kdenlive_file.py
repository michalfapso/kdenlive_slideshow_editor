import opentimelineio as otio
import re
from PyQt5.QtCore import QRectF
import subprocess
import os

def clips_overlap(clipA, timeClipAStart, clipB, timeClipBStart):
	clipA_dur = clipA.source_range.duration
	clipB_dur = clipB.source_range.duration

	timeClipAEnd = timeClipAStart + clipA_dur
	timeClipBEnd = timeClipBStart + clipB_dur
	#print('clips_overlap() clipA:', clipA)
	#print('clips_overlap() clipB:', clipB)
	#print('clips_overlap() timeClipA:', timeClipAStart, timeClipAEnd)
	#print('clips_overlap() timeClipB:', timeClipBStart, timeClipBEnd)
	overlap = timeClipAStart < timeClipBEnd and timeClipAEnd > timeClipBStart
	#print('clips_overlap() res:', overlap)
	return overlap

def adjust_clip_duration(clip, durationDiff):
	clip.source_range = otio.opentime.TimeRange(clip.source_range.start_time, clip.source_range.duration + durationDiff)

def is_image(path):
	return re.match(r'.*\.(jpg|png)', path)

def is_music(path):
	return re.match(r'.*\.(mp3|webm)', path)

class KdenliveFile:
	DBNDownBeatTracker_script = 'DBNDownBeatTracker' # /home/miso/install/madmom/bin/DBNDownBeatTracker

	def __init__(self):
		self.timeline = None
		self.inputFilename = ''
		self.beatFiles = []
		self.beats = []

	def Load(self, filename):
		self.timeline = otio.adapters.read_from_file(filename)
		self.inputFilename = filename
	#mytimeline = otio.adapters.read_from_file("/media/miso/data/foto/2016-08-24..27 Torquay 1/premiere/export_seq.edl", rate=25)

	def AddBeats(self, filenameAudio, filenameBeats):
		self.beats = []
		self.beatFiles.append({
			'filenameAudio': filenameAudio,
			'filenameBeats': filenameBeats
		})
		print('AddBeats() beatFiles:', self.beatFiles)
		for beatFile in self.beatFiles:
			match = self.FindClip('.*' + re.escape(beatFile['filenameAudio']))
			if match is None:
				print('AddBeats() clip not found for ', beatFile['filenameAudio'])
				continue
			for beat in self.ParseBeats(beatFile['filenameBeats']):
				if beat['nr'] != 1:
					print('AddBeats() skipping beat ', beat['nr'])
					continue
				# Skip beats outside of the clip's in-out boundaries
				if (beat['t'] < match['item'].source_range.start_time) or (beat['t'] > match['item'].source_range.start_time + match['item'].source_range.duration):
					print('AddBeats() skipping beat t:', beat['t'])
					continue
				beat_global = {
					't': match['tStart'] - match['item'].source_range.start_time + beat['t'],
					'nr': beat['nr'],
				}
				self.beats.append(beat_global)
		self.beats.sort(key=lambda beat: beat['t'])
		print('AddBeats() beats_count:', len(self.beats), ' beats:', self.beats)

	def AddBeatsForAllMusicClips(self):
		for track in self.timeline.tracks:
			for item in track:
				if isinstance(item, otio.schema.Clip) and isinstance(item.media_reference, otio.schema.ExternalReference):
					resource = item.media_reference.target_url
					if is_music(resource):
						print('AddBeatsForAllMusicClips() music clip found:', resource)
						resource_beats = resource + '.downbeats'
						if not os.path.exists(resource_beats) or os.path.getsize(resource_beats) == 0:
							command = [self.DBNDownBeatTracker_script, 'single', resource]
							print('AddBeatsForAllMusicClips() Running command: ', command)
							f_out = open(resource_beats, "w")
							process = subprocess.Popen(command, stdout=f_out)
							process.wait()
							print('AddBeatsForAllMusicClips() Command returned with exit code:', process.returncode)
						self.AddBeats(os.path.basename(resource), resource_beats)

	def ParseBeats(self, filename):
		print('ParseBeats() filename:', filename)
		beats = []
		rate = self.timeline.duration().rate
		print('ParseBeats() rate:', rate)
		with open(filename, "r") as f:
			line = f.readline()
			while line:
				[seconds, beat_nr] = line.split()
				beats.append({
					't': otio.opentime.RationalTime.from_seconds(float(seconds)).rescaled_to(rate),
					'nr': int(beat_nr),
				})
				line = f.readline()
		print('ParseBeats() beats:', beats)
		return beats

	def FindClip(self, rxFilename):
		rate = self.timeline.duration().rate
		for track in self.timeline.tracks:
			t = otio.opentime.RationalTime.from_seconds(0.0).rescaled_to(rate) # start time of the current clip
			for item in track:
				if isinstance(item, otio.schema.Clip) and isinstance(item.media_reference, otio.schema.ExternalReference):
					resource = item.media_reference.target_url
					if re.match(rxFilename, resource):
						return {'track': track, 'item': item, 'tStart': t}
				t += item.source_range.duration
		return None


	def AddBeatGuides(self):
		if 'guides' not in self.timeline.metadata:
			self.timeline.metadata['guides'] = []
		guides = self.timeline.metadata['guides']
		for beat in self.beats:
			if beat['nr'] != 1:
				continue
			guides.append({
				'comment': 'guide_beat',
				'pos': beat['t'],
				'type': beat['nr'],
			})
		print('AddBeatGuides() guides:', self.timeline.metadata['guides'])

	def GroupClipsWithSameBoundaries(self):
		rate = self.timeline.duration().rate
		idx = []
		t = []
		for track in self.timeline.tracks:
			idx.append(0)
			t.append(otio.opentime.RationalTime(0, rate))

		N = len(idx)
		groups = []

		done = False
		while not done:
			g = {}
			i_min = -1
			t_min = otio.opentime.RationalTime(0, rate)
			done = True
			for i in range(0, N):
				if idx[i] >= len(self.timeline.tracks[i]):
					continue
				# Skip gaps:
				while isinstance(self.timeline.tracks[i][idx[i]], otio.schema.Gap):
					t[i] += self.timeline.tracks[i][idx[i]].source_range.duration
					idx[i] += 1
				print('GroupClipsWithSameBoundaries() i:', i, 'idx:', idx[i])
				clip_dur = self.timeline.tracks[i][idx[i]].source_range.duration
				if idx[i]+1 < len(self.timeline.tracks[i]):
					done = False
					if i_min < 0 or t[i] < t[i_min]:
						i_min = i
						t_min = t[i_min] + clip_dur
				key = str(t[i].to_frames()) + '_' + str(clip_dur.to_frames())
				if key not in g:
					g[key] = []
				g[key].append({'data': str(i) + ':' + str(t[i].to_frames()), 'leaf': 'clip', 'type': 'Leaf'})
			print('GroupClipsWithSameBoundaries() g:', g)
			for gi in g:
				if len(g[gi]) > 1:
					group = {'children': g[gi], 'type': 'AVSplit'}
					print('GroupClipsWithSameBoundaries() append group:', group)
					groups.append(group)
			t[i_min] = t_min
			idx[i_min] += 1
		print('GroupClipsWithSameBoundaries() groups:', groups)
		self.timeline.metadata['groups'] = groups


	def ShiftGroupsTime(self, timeOld, timeNew):
		print('ShiftGroupsTime() timeOld:', timeOld, 'timeNew:', timeNew)
		frames_diff = (timeNew - timeOld).to_frames()
		if 'groups' not in self.timeline.metadata:
			return
		for group in self.timeline.metadata['groups']:
			print('ShiftGroupsTime() group:', group)
			if group['type'] == 'AVSplit':
				for child in group['children']:
					print('ShiftGroupsTime() child:', child)
					[track_num, frame] = child['data'].split(':')
					frame = int(frame)
					print('ShiftGroupsTime() track_num:', track_num, 'frame:', frame)
					if frame >= timeOld.to_frames():
						frame += frames_diff
						print('ShiftGroupsTime() shift frame -> ', frame)
					child['data'] = ':'.join([track_num, str(frame)])

	def SynchronizeToBeats(self):
		if len(self.beats) == 0:
			print('SynchronizeToBeats(): ERROR: No beats found')
			return
		print('SynchronizeToBeats() BEGIN --------------------------------------------------')
		tracks = ['main_v', 'main_a'] #
		PHOTO_DURATION_MIN = 2
		PHOTO_DURATION_MAX = 4
		SHIFT_MAX = 2
		rate = self.timeline.duration().rate

		# Find master and slave tracks
		track_master = None
		track_slave  = None
		for track in self.timeline.tracks:
			print('SynchronizeToBeats() track:', track)
			print('SynchronizeToBeats() track name:', track.name)
			if track.name == tracks[0]:
				track_master = track
			if track.name == tracks[1]:
				track_slave = track

		i_beat  = 0 # beats index
		i_slave = 0 # track_slave index
		t_slave = otio.opentime.RationalTime.from_seconds(0.0).rescaled_to(rate) # start time of the current slave clip
		t       = otio.opentime.RationalTime.from_seconds(0.0).rescaled_to(rate) # start time of the current master clip
		for item in track_master:
			print('SynchronizeToBeats() --------------------------------------------------')
			print('SynchronizeToBeats() item:', item)
			resource = ''
			if isinstance(item, otio.schema.Clip) and isinstance(item.media_reference, otio.schema.ExternalReference):
				resource = item.media_reference.target_url
			print('SynchronizeToBeats() clip metadata:', item.metadata)
			clip_in  = item.source_range.start_time
			clip_dur = item.source_range.duration
			clip_out = clip_in + clip_dur
			print('SynchronizeToBeats() t:', t, 'clip_in:', clip_in, 'clip_dur:', clip_dur, 'clip_out:', clip_out)
			ref_is_expandable = False
			if isinstance(item, otio.schema.Gap):
				ref_out = clip_out
				ref_is_expandable = True
				print('SynchronizeToBeats() Gap ref_out:', ref_out)
			else:
				print('SynchronizeToBeats() NonGap item:', item)
				print('SynchronizeToBeats() NonGap item.metadata:', item.metadata)
				print('SynchronizeToBeats() NonGap item.metadata["length"]:', item.metadata['length'])
				print('SynchronizeToBeats() NonGap item.media_reference:', item.media_reference)
				print('SynchronizeToBeats() NonGap item.media_reference.available_range:', item.media_reference.available_range)
				print('SynchronizeToBeats() NonGap item.media_reference.available_range.start_time:', item.media_reference.available_range.start_time)
				ref_in  = item.media_reference.available_range.start_time
				ref_dur = item.media_reference.available_range.duration
				ref_out = ref_in + ref_dur
				if is_image(resource):
					ref_is_expandable = True
				print('SynchronizeToBeats() ref_in:', ref_in, 'ref_dur:', ref_dur, 'ref_out:', ref_out, 'ref_is_expandable:', ref_is_expandable)
			t_next = t + clip_dur
			#i_beat = self.GetClosestBeatIdxForTime(self.beats, i_beat, t_next)
			print('SynchronizeToBeats() t_next:', t_next, 'i_beat:', i_beat, 'len(beats):', len(self.beats))
			if self.beats[i_beat]['t'] < t_next:
				while (i_beat + 1 < len(self.beats)) and (self.beats[i_beat + 1]['t'] < t_next):
					i_beat += 1
				if i_beat + 1 < len(self.beats):
					if t_next - self.beats[i_beat]['t'] > self.beats[i_beat + 1]['t'] - t_next:
						i_beat += 1
			t_diff = self.beats[i_beat]['t'] - t_next
			print('SynchronizeToBeats() i_beat:', i_beat, 'beat:', self.beats[i_beat], self.beats[i_beat]['t'].to_timecode(), 't_diff:', t_diff)
			if abs(t_diff.to_seconds()) < SHIFT_MAX:
				# Round the beat time to integer frames count
				t_next_old = t_next
				t_next = otio.opentime.RationalTime(int(self.beats[i_beat]['t'].to_frames()), rate)
				clip_dur_old = clip_dur
				clip_dur = t_next - t
				clip_out = clip_in + clip_dur
				if ref_out < clip_out and not ref_is_expandable:
					print('SynchronizeToBeats() Reference media too short -> can not extend the clip')
					clip_dur = clip_dur_old
					clip_out = clip_in + clip_dur
					t_next = t_next_old
				else:
					#clip_dur = clip_dur - otio.opentime.RationalTime(1, rate)
					print('SynchronizeToBeats() clip_dur:', clip_dur_old, '->', clip_dur)
					print('SynchronizeToBeats() t_next:', t_next, 'clip_dur:', item.source_range.duration)
					#item.set_source_range(otio.opentime.TimeRange(t, clip_dur))

					# Find a matching clip in the slave track
					while (i_slave + 1 < len(track_slave)) and (not clips_overlap(item, t, track_slave[i_slave], t_slave)):
						print('SynchronizeToBeats() skipping slave t:', t_slave, 'item:', track_slave[i_slave])
						t_slave += track_slave[i_slave].source_range.duration
						i_slave += 1

					self.synchronize_slave_to_the_beats(clip_dur, clip_dur_old, i_slave, item, t,
														t_slave, track_slave)

					# Master clip can be modified after the slave clip
					item.source_range = otio.opentime.TimeRange(clip_in, clip_dur)
					print('SynchronizeToBeats() master clip modified:', item)
					self.ShiftGroupsTime(t_next_old, t_next)
					#item.source_range.duration = clip_dur

			print('SynchronizeToBeats() item out:', item)
			print('SynchronizeToBeats() item duration:', item.source_range.duration)
			t = t_next
			# if (resource == "clips/3508_IMG.jpg"):
			# 	print('SynchronizeToBeats() BREAK')
			# 	break


		print('SynchronizeToBeats() END --------------------------------------------------')

	def synchronize_slave_to_the_beats(self, clip_dur, clip_dur_old, i_slave, item, t, t_slave,
									   track_slave):
		"""Synchronize the slave clip to the beats.

		If there is no clip in the slave track skip this step.
		"""
		if len(track_slave) > 0:
			print('SynchronizeToBeats() slave t:', t_slave, 'item:', track_slave[i_slave])
			# Detect overlaps before the master clip is changed
			if clips_overlap(item, t, track_slave[i_slave], t_slave):
				print('SynchronizeToBeats() slave overlaps')
				clip_dur_diff = clip_dur - clip_dur_old
				print('SynchronizeToBeats() slave adjust_clip_duration() clip in :',
					  track_slave[i_slave], ' durationDiff:', clip_dur_diff)
				adjust_clip_duration(track_slave[i_slave], clip_dur_diff)
				print('SynchronizeToBeats() slave adjust_clip_duration() clip out:',
					  track_slave[i_slave], ' durationDiff:', clip_dur_diff)
		else:
			print('Skipped SynchronizeToBeats() for slave track - it is empty (no clips)')

	def GetImagesData(self):
		print('')
		print('--------------------------------------------------')
		print('KdenliveFile::GetImagesData()')
		images_data = {}
		rate = self.timeline.duration().rate
		for track in self.timeline.tracks:
			print('GetImagesData() track:', track)
			for item in track:
				if isinstance(item, otio.schema.Clip) and isinstance(item.media_reference, otio.schema.ExternalReference):
					resource = item.media_reference.target_url
					print('GetImagesData() resource:', resource)
					images_data[resource] = {'stay_inside_image': False, 'bboxes':[]}
					clip_in = item.source_range.start_time
					clip_out = item.source_range.duration + clip_in
					print('GetImagesData() clip_in :', clip_in)
					print('GetImagesData() clip_out:', clip_out)
					for effect in item.effects:
						print('GetImagesData() effect:', effect)
						if effect.effect_name == 'qtblend':
							rect = effect.metadata['rect']
							print('GetImagesData() rect:', rect)
							keyframes = KdenliveFile.keyframes_from_string(rect, rate)
							print('GetImagesData() keyframes:', keyframes)
							print('GetImagesData() keyframes_str:', KdenliveFile.keyframes_to_string(keyframes))
							if re.match('.*\.jpg', resource, re.IGNORECASE):
								if len(keyframes) == 0 or len(keyframes) == 2:
									for keyframe_time in keyframes:
										keyframe = keyframes[keyframe_time]
										bbox = keyframe['val'].split(' ')
										print('GetImagesData() bbox:', bbox)
										bbox01 = KdenliveFile.bbox_keyframe_to_01(bbox)
										images_data[resource]['bboxes'].append(bbox01)
										print('GetImagesData() bbox01:', bbox01)
										print('GetImagesData() bbox01 back to keyframe:', KdenliveFile.bbox_01_to_keyframe(bbox01))

		print('GetImagesData() images_data:', images_data)
		print('--------------------------------------------------')
		return images_data

	def SetImagesData(self, imagesData):
		print('')
		print('--------------------------------------------------')
		print('KdenliveFile::SetImagesData()')
		rate = self.timeline.duration().rate
		for track in self.timeline.tracks:
			print('SetImagesData() track:', track)
			for item in track:
				if isinstance(item, otio.schema.Clip) and isinstance(item.media_reference, otio.schema.ExternalReference):
					resource = item.media_reference.target_url
					print('SetImagesData() resource:', resource)
					if not resource in imagesData:
						continue
					clip_in = item.source_range.start_time
					clip_out = clip_in + item.source_range.duration - otio.opentime.RationalTime(1, rate)
					print('SetImagesData() clip_in :', clip_in)
					print('SetImagesData() clip_out:', clip_out)
					if not 'bboxes' in imagesData[resource]:
						continue
					bboxes = imagesData[resource]['bboxes']
					print('SetImagesData() bboxes:', bboxes)
					if len(bboxes) == 2:
						print('SetImagesData() transform clip_out to_time_string():', clip_out.to_time_string(), 'to_timecode():', clip_out.to_timecode())
						transform_rect_str = \
							'00:00:00,000~=' + ' '.join(str(int(x)) for x in KdenliveFile.bbox_01_to_keyframe(bboxes[0])) + ' 1;' + \
							clip_out.to_time_string().replace(',', '.') + '~=' + ' '.join(str(int(x)) for x in KdenliveFile.bbox_01_to_keyframe(bboxes[1])) + ' 1;'
						transform_found = False
						for effect in item.effects:
							print('SetImagesData() effect:', effect)
							if effect.effect_name == 'qtblend':
								transform_found = True
								rect = effect.metadata['rect']

								effect.metadata['rect'] = transform_rect_str

								print('SetImagesData() rect:', effect.metadata['rect'])

						if not transform_found:
							item.effects.append(otio.schema.Effect(
								effect_name='qtblend',
								metadata={'compositing': '0', 'distort': '0', 'kdenlive:collapsed': '0', 'kdenlive_id': 'qtblend', 'mlt_service': 'qtblend', 'rect': transform_rect_str, 'rotate_center': '1', 'rotation': '0'}))
					print('SetImagesData() resource:', resource)
					print('SetImagesData() effects:', item.effects)

		print('--------------------------------------------------')

	def DumpClipsLength(self):
		print('--------------------------------------------------')
		print('DumpClipsLength() BEGIN')
		for track in self.timeline.tracks:
			for item in track:
				name='unknown'
				if isinstance(item, otio.schema.Clip) and isinstance(item.media_reference, otio.schema.ExternalReference):
					name = 'clip:' + item.media_reference.target_url
				elif isinstance(item, otio.schema.Gap):
					name = 'gap'

				print('DumpClipsLength() ' + name + ' duration:', item.source_range.duration.to_frames())
		print('DumpClipsLength() END')
		print('--------------------------------------------------')


	def Save(self, filename):
		otio.adapters.write_to_file(self.timeline, filename)


	@staticmethod
	def time(clock, fps):
		"""Decode an MLT time
		which is either a frame count or a timecode string
		after format hours:minutes:seconds.floatpart"""
		hms = [float(x) for x in clock.replace(',', '.').split(':')]
		f = 0
		m = fps if len(hms) > 1 else 1  # no delimiter, it is a frame number
		for x in reversed(hms):
			f = f + x * m
			m = m * 60
		return otio.opentime.RationalTime(round(f, 3), fps)

	@staticmethod
	def keyframes_from_string(s, rate):
		kfdict = dict((KdenliveFile.time(t, rate), {'interp':interp, 'val':v}) for (t, interp, v) in re.findall('([^|~=;]*)([|~]?=)([^;]*)', s))
		print('keyframes_from_string() kfdict:', kfdict)
		return kfdict;
		#for u in s.split(';'):

	@staticmethod
	def keyframes_to_string(kfdict):
		"""Build a MLT keyframe string"""
		print('keyframes_to_string() kfdict.items:', kfdict.items())
		out = []
		for t, v in kfdict.items():
			out.append(str(int(t.value)) + v['interp'] + v['val'])
		return ';'.join(out)

	@staticmethod
	def bbox_keyframe_to_01(bboxKeyframe):
		bbox01 = QRectF(
			-int(bboxKeyframe[0]) / int(bboxKeyframe[2]),
			-int(bboxKeyframe[1]) / int(bboxKeyframe[3]),
			1920 / int(bboxKeyframe[2]),
			1080 / int(bboxKeyframe[3]),
		)
		return bbox01

	@staticmethod
	def bbox_01_to_keyframe(bbox01):
		w = 1920 / bbox01.width ()
		h = 1080 / bbox01.height()
		bbox_keyframe = [
			-(bbox01.x() * w),
			-(bbox01.y() * h),
			w,
			h,
		]
		return bbox_keyframe
