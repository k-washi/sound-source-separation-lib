from dataclasses import dataclass

@dataclass
class AudioOutputStruct():
    sample_rate: int
    sample_width: int
    ch_num: int
    sample_num: int
