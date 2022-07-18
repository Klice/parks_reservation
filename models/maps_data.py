from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from dataclasses_json import LetterCase, config, dataclass_json
from marshmallow import fields


@dataclass
class Color:
    r_value: int
    g_value: int
    b_value: int


@dataclass
class MapPoint:
    x_coordinate: int
    y_coordinate: int


@dataclass
class FontStyle:
    is_bold: bool
    is_italics: bool


@dataclass
class Font:
    font_size: int
    font: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AreaPoint(MapPoint):
    order: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MapLocalizedValue:
    culture_name: str
    title: str
    description: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MapLabelLocalizedValue:
    culture_name: str
    label: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MapLegend(MapPoint, Color):
    map_legend_item_id: int
    legend_item_type: int
    icon_type: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class LocalizationPoint(MapPoint, Color):
    justification: int


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AccessPoint(MapPoint):
    width: int
    height: int
    resource_id: int
    icon_type: int
    localization_point: LocalizationPoint
    transactionLocationTypes: List[int]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class AccessPointResource(AccessPoint):
    registration_actions: List[int]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MapResource(MapPoint):
    resource_id: int
    icon_type: int
    localization_point: LocalizationPoint
    registration_actions: List[int]
    transaction_location_types: List[int]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MapLink(Color, MapPoint, Font):
    child_map_id: int
    localization_point: LocalizationPoint
    transaction_location_types: List[int]
    registration_actions: List[int]
    area_points: List[AreaPoint]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MapLabel(Color, Font, FontStyle):
    map_label_id: int
    localization_point: LocalizationPoint
    localized_values: List[MapLabelLocalizedValue]


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Map:
    map_id: int
    version_id: int
    versionDate: datetime = field(
        metadata=config(
            encoder=datetime.isoformat,
            decoder=datetime.fromisoformat,
            mm_field=fields.DateTime(format='iso')
        )
    )
    is_disabled: bool
    map_image_uid: str
    map_image_format: int
    x_dimension: int
    y_dimension: int
    localized_values: List[MapLocalizedValue]
    is_resource_location_root_map: bool
    map_access_point_resources: List[AccessPointResource]
    map_legend_items: List[MapLegend]
    parent_maps: List[int]
    map_global_style_legends: List[int]
    map_resources: List[MapResource]
    map_links: List[MapLink]
    map_labels: List[MapLabel]
    resource_location_id: Optional[int] = None
