from .const import SOUND_IDS, ALARM_IDS, AVAILABLE_APP_PROPERTIES

class AppModel(object):
    """
    class representing a installed app on the LaMetric
    """
    def __init__(self, data):
        self.actions = {}
        self.package = ''
        self.vendor = ''
        self.version = ''
        self.version_code = ''
        self.widgets = ''
        
        self._set_properties(data)
                
    def _set_properties(self, data):
        if 'actions' in data.keys():
            self.actions = data['actions']
        if 'package' in data.keys():
            self.package = data['package']
        if 'vendor' in data.keys():
            self.vendor = data['vendor']
        if 'version' in data.keys():
            self.version = data['version']
        if 'version_code' in data.keys():
            self.version_code = data['version_code']
        if 'widgets' in data.keys():
            self.widgets = data['widgets']


class Frame(object):
    """
    base frame class
    """
    def __init__(self):
        pass


class SimpleFrame(Frame):
    """
    simple frame that can show and icon plus text
    (icon_id or data:image/png;base64)
    """
    def __init__(self, icon, text):
        Frame.__init__(self)
        self.icon = icon
        self.text = text

    def json(self):
        return {
            "icon": self.icon,
            "text": self.text,
        }


class GoalFrame(Frame):
    """
    goal frame that can show and icon with a goal
    """
    def __init__(self, icon, start=0, current=0, end=100, unit="%"):
        Frame.__init__(self)
        self.icon = icon
        self.start = start
        self.current = current
        self.end = end
        self.unit = unit

    def json(self):
        return {
            "icon": self.icon,
            "goalData": {
                "start": self.start,
                "current": self.current,
                "end": self.end,
                "unit": self.unit
            }
        }


class SpikeChart(Frame):
    """
    spike chart that can show a chart
    """
    def __init__(self, data):
        Frame.__init__(self)
        assert(isinstance(data, list))
        self.data = data

    def json(self):
        return {
            "chartData": self.data,
        }


class Sound(object):
    """
    a sound
    """
    def __init__(self, category, sound_id, repeat=1):
        assert(
            (category == "notification" and (sound_id in SOUND_IDS)) or
            (category == "alarms" and (sound_id in ALARM_IDS))
        )
        assert(repeat > 0)

        self.category = category
        self.sound_id = sound_id
        self.repeat = repeat

    def json(self):
        return {
            "category": self.category,
            "id": self.sound_id,
            "repeat": self.repeat,
        }


class Model(object):
    """
    a model can consist of multiple frames and a sound
    """
    def __init__(self, frames=[], cycles=1, sound=None):
        assert(cycles >= 0)
        assert(sound is None or isinstance(sound, Sound))

        self.cycles = cycles
        self.frames = frames
        self.sound = sound

    def add_frame(self, frame):
        """
        add a single frame to the model
        """
        self.frames.append(frame)

    def add_frames(self, frames):
        """
        add a list of frames to the model
        """
        for frame in frames:
            self.add_frame(frame)

    def json(self):
        j = {
            "cycles": self.cycles,
            "frames": [
                frame.json()
                for frame in self.frames
                if isinstance(frame, Frame)
            ],
        }
        if self.sound is not None:
            j["sound"] = self.sound.json()

        return j
