from dataclasses import dataclass, field
from typing import List, Optional
from dataclasses_json import LetterCase, config, dataclass_json


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ParkAlert:
    culture_name: str
    html_message_text: str
    message_title: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ParkAlerts:
    en_CA: List[ParkAlert] = field(metadata=config(field_name="en-CA"))
    fr_CA: List[ParkAlert] = field(metadata=config(field_name="fr-CA"))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ResourceLocationLocalizedValues:
    en_CA: str = field(metadata=config(field_name="en-CA"))
    fr_CA: str = field(metadata=config(field_name="fr-CA"))


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class RootMap:
    map_id: int
    resource_location_localized_values: ResourceLocationLocalizedValues
    resource_category_ids: Optional[List[int]] = None
    park_alerts: Optional[ParkAlerts] = None
    resource_location_id: Optional[int] = None
