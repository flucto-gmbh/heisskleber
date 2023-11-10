from dataclasses import dataclass


@dataclass
class ResamplerConf:
    resample_rate: int = 1000
