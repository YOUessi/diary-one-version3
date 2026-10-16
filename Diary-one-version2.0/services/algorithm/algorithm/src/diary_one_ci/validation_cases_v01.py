"""Reference semantic-day cases for Diary One Validation V01/V02.

The compact segment definitions below expand to explicit two-minute timeline
windows.  They are design scenarios, not captured user data or accuracy gold.
"""

from __future__ import annotations

import copy
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from .validation_v01 import DAY_CASE_CONTRACT_VERSION, SUITE_CONTRACT_VERSION


def _segment(
    start: int,
    end: int,
    atoms: Sequence[str],
    *,
    source_kind: str = "AUTO",
    support: str = "STRONG",
    import_batch_id: str = "B1",
) -> Dict[str, object]:
    return {
        "start": start,
        "end": end,
        "atoms": list(atoms),
        "source_kind": source_kind,
        "support": support,
        "import_batch_id": import_batch_id,
    }


def _timeline(day_id: str, segments: Iterable[Mapping[str, object]]) -> List[Dict[str, object]]:
    windows: List[Dict[str, object]] = []
    seen_minutes = set()
    for segment in segments:
        start = int(segment["start"])
        end = int(segment["end"])
        if start % 2 or end % 2 or start > end:
            raise ValueError(f"invalid two-minute segment: {day_id}:{start}:{end}")
        for minute in range(start, end + 1, 2):
            if minute in seen_minutes:
                raise ValueError(f"overlapping timeline minute: {day_id}:{minute}")
            seen_minutes.add(minute)
            windows.append(
                {
                    "window_id": f"{day_id}-W{len(windows) + 1:03d}",
                    "capture_minute": minute,
                    "source_kind": segment["source_kind"],
                    "semantic_atoms": list(segment["atoms"]),
                    "evidence_support": segment["support"],
                    "import_batch_id": segment["import_batch_id"],
                }
            )
    return sorted(windows, key=lambda item: int(item["capture_minute"]))


def _gold_memory(
    memory_id: str,
    memory_type: str,
    span: Sequence[int],
    identity_atoms: Sequence[str],
    required_atoms: Sequence[str],
    *,
    optional_atoms: Sequence[str] = (),
    forbidden_atoms: Sequence[str] = (),
    required_concepts: Sequence[str] = (),
    allowed_concepts: Sequence[str] = (),
    forbidden_concepts: Sequence[str] = (),
    required_media_atoms: Sequence[str] = (),
    requirement: str = "REQUIRED",
    story_role: str = "PRIMARY_DAY_MEMORY",
) -> Dict[str, object]:
    return {
        "gold_memory_id": memory_id,
        "memory_type": memory_type,
        "requirement": requirement,
        "story_role": story_role,
        "acceptable_span_minute": list(span),
        "minimum_overlap_ratio": 0.50,
        "identity_atoms": list(identity_atoms),
        "required_atoms": list(required_atoms),
        "optional_atoms": list(optional_atoms),
        "forbidden_atoms": list(forbidden_atoms),
        "required_concept_ids": list(required_concepts),
        "allowed_concept_ids": list(allowed_concepts),
        "forbidden_concept_ids": list(forbidden_concepts),
        "allowed_entity_ids": [],
        "media_policy": "STANDARD_3_TO_5" if memory_type == "CHAPTER" else "AHA_SINGLE",
        "media_count_range": [3, 5] if memory_type == "CHAPTER" else [1, 1],
        "required_media_atoms": list(required_media_atoms),
        "allowed_media_formats": (
            ["PHOTO", "LIVE_2S", "VIDEO_5S"]
            if memory_type == "CHAPTER"
            else ["PHOTO", "LIVE_2S"]
        ),
    }


def _media(memory_id: str, atoms: Sequence[str], memory_type: str) -> List[Dict[str, object]]:
    result = []
    for index, atom in enumerate(atoms):
        result.append(
            {
                "media_id": f"{memory_id}-M{index + 1}",
                "semantic_atom": atom,
                "format": "PHOTO" if memory_type == "AHA" else "LIVE_2S",
                "is_hero": memory_type == "CHAPTER" and index == 0,
            }
        )
    return result


def _prediction_memory(
    memory_id: str,
    memory_type: str,
    span: Sequence[int],
    atoms: Sequence[str],
    media_atoms: Sequence[str],
    *,
    concepts: Sequence[str] = (),
    asserted_atoms: Optional[Sequence[str]] = None,
    title: str = "",
    story: str = "",
    moment_line: str = "",
    time_label: str = "",
) -> Dict[str, object]:
    return {
        "memory_id": memory_id,
        "memory_type": memory_type,
        "span_minute": list(span),
        "semantic_atoms": list(atoms),
        "asserted_atoms": list(asserted_atoms if asserted_atoms is not None else atoms),
        "canonical_concept_ids": list(concepts),
        "entity_ids": [],
        "media": _media(memory_id, media_atoms, memory_type),
        "narrative": {
            "title": title,
            "story": story,
            "moment_line": moment_line,
            "time_label": time_label,
        },
    }


def _day(
    day_id: str,
    title: str,
    profile_id: str,
    segments: Sequence[Mapping[str, object]],
    day_state: str,
    chapter_range: Sequence[int],
    aha_range: Sequence[int],
    memories: Sequence[Mapping[str, object]],
    *,
    forbidden_patterns: Sequence[Mapping[str, object]] = (),
    distinct_pairs: Sequence[Mapping[str, object]] = (),
    review_prompts: Sequence[str] = (),
) -> Dict[str, object]:
    return {
        "contract_version": DAY_CASE_CONTRACT_VERSION,
        "day_id": day_id,
        "title": title,
        "profile_id": profile_id,
        "evidence_mode": "SEMANTIC_TIMELINE_ONLY",
        "timeline_step_minutes": 2,
        "timeline": _timeline(day_id, segments),
        "gold": {
            "label_origin": "DESIGN_GOLD",
            "label_status": "DESIGN_REVIEWED",
            "accuracy_eligible": False,
            "day_state": day_state,
            "chapter_count_range": list(chapter_range),
            "aha_count_range": list(aha_range),
            "memories": [copy.deepcopy(dict(memory)) for memory in memories],
            "forbidden_memory_patterns": [
                copy.deepcopy(dict(pattern)) for pattern in forbidden_patterns
            ],
            "distinct_story_pairs": [copy.deepcopy(dict(pair)) for pair in distinct_pairs],
        },
        "human_review_prompts": list(review_prompts),
    }


def _trial(
    trial_id: str,
    day_id: str,
    day_state: str,
    memories: Sequence[Mapping[str, object]],
    *,
    trial_kind: str = "NOMINAL_REFERENCE",
    expected_status: str = "PASS",
    required_error_codes: Sequence[str] = (),
) -> Dict[str, object]:
    return {
        "trial_id": trial_id,
        "day_id": day_id,
        "trial_kind": trial_kind,
        "prediction": {
            "day_state": day_state,
            "memories": [copy.deepcopy(dict(memory)) for memory in memories],
        },
        "expected_evaluation": {
            "status": expected_status,
            "required_error_codes": list(required_error_codes),
        },
    }


def build_reference_suite() -> Dict[str, object]:
    """Build the 12-day, 16-trial V01/V02 conformance suite."""

    days: List[Dict[str, object]] = []
    trials: List[Dict[str, object]] = []

    d01_chapter_gold = _gold_memory(
        "D01-G-CH1",
        "CHAPTER",
        [540, 604],
        ["ancient_town_walk"],
        ["ancient_town_walk", "historic_architecture", "stone_lane"],
        optional_atoms=["historic_gate", "wood_carving"],
        required_concepts=["ACTIVITY.CITY_WALK"],
        allowed_concepts=[
            "ACTIVITY.CITY_WALK",
            "SETTING.TRADITIONAL_HISTORIC_DISTRICT",
            "CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE",
            "OCCASION.TRAVEL_OUTING",
        ],
        required_media_atoms=["historic_gate", "wood_carving", "stone_lane"],
    )
    d01_aha_gold = _gold_memory(
        "D01-G-AH1",
        "AHA",
        [578, 588],
        ["cat_jump_table"],
        ["cat_jump_table", "playful_cat"],
        optional_atoms=["tea_shop_visit"],
        required_concepts=["CENTRAL_SUBJECT.CAT"],
        allowed_concepts=[
            "SETTING.CAFE_OR_TEA_SHOP",
            "CENTRAL_SUBJECT.CAT",
        ],
        required_media_atoms=["cat_jump_table"],
        story_role="EMBEDDED_DISTINCT_PEAK",
    )
    days.append(
        _day(
            "D01",
            "古镇漫步与奶茶店小猫",
            "TRAVEL_CITYWALK",
            [
                _segment(540, 548, ["ancient_town_walk", "historic_gate", "stone_lane", "historic_architecture"]),
                _segment(550, 558, ["ancient_town_walk", "stone_lane", "historic_architecture"]),
                _segment(560, 570, ["ancient_town_walk", "historic_architecture", "wood_carving"]),
                _segment(572, 576, ["tea_shop_visit", "cafe_interior", "dessert_display"]),
                _segment(578, 586, ["tea_shop_visit", "cat_jump_table", "playful_cat"]),
                _segment(588, 592, ["tea_shop_visit", "tea_drink", "dessert"]),
                _segment(594, 602, ["ancient_town_walk", "stone_lane", "historic_architecture"]),
            ],
            "CHAPTER_DAY",
            [1, 1],
            [1, 1],
            [d01_chapter_gold, d01_aha_gold],
            distinct_pairs=[
                {
                    "chapter_gold_id": "D01-G-CH1",
                    "aha_gold_id": "D01-G-AH1",
                    "chapter_forbidden_atoms": ["cat_jump_table", "playful_cat"],
                    "aha_forbidden_atoms": ["historic_gate", "wood_carving", "stone_lane"],
                }
            ],
        )
    )
    d01_chapter = _prediction_memory(
        "D01-P-CH1",
        "CHAPTER",
        [540, 604],
        ["ancient_town_walk", "historic_architecture", "stone_lane", "historic_gate", "wood_carving"],
        ["historic_gate", "wood_carving", "stone_lane"],
        concepts=[
            "ACTIVITY.CITY_WALK",
            "SETTING.TRADITIONAL_HISTORIC_DISTRICT",
            "CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE",
            "OCCASION.TRAVEL_OUTING",
        ],
        title="古镇慢行",
        story="石板路一路向前，牌坊与木雕在转角慢慢展开。",
        time_label="上午",
    )
    d01_aha = _prediction_memory(
        "D01-P-AH1",
        "AHA",
        [578, 588],
        ["cat_jump_table", "playful_cat", "tea_shop_visit"],
        ["cat_jump_table"],
        concepts=["SETTING.CAFE_OR_TEA_SHOP", "CENTRAL_SUBJECT.CAT"],
        moment_line="调皮小猫突然跳上桌。",
        time_label="09:38",
    )
    trials.append(_trial("T-D01-NOMINAL", "D01", "CHAPTER_DAY", [d01_chapter, d01_aha]))

    d02_gold = _gold_memory(
        "D02-G-CH1",
        "CHAPTER",
        [1080, 1122],
        ["birthday_gathering"],
        ["birthday_gathering", "birthday_cake", "candle_blowing", "birthday_applause"],
        required_concepts=["OCCASION.BIRTHDAY"],
        allowed_concepts=["ACTIVITY.SHARED_MEAL", "SETTING.HOME", "OCCASION.BIRTHDAY", "OCCASION.FAMILY_GATHERING"],
        required_media_atoms=["birthday_cake", "candle_blowing", "birthday_applause"],
    )
    days.append(
        _day(
            "D02",
            "家庭生日晚餐",
            "FAMILY_OCCASION",
            [
                _segment(1080, 1090, ["birthday_gathering", "family_dinner", "table_setting"]),
                _segment(1092, 1100, ["birthday_gathering", "birthday_cake", "candles_lit"]),
                _segment(1102, 1108, ["birthday_gathering", "birthday_cake", "candle_blowing"]),
                _segment(1110, 1114, ["birthday_gathering", "birthday_applause", "family_smiles"]),
                _segment(1116, 1120, ["birthday_gathering", "cake_serving", "family_dinner"]),
            ],
            "CHAPTER_DAY",
            [1, 1],
            [0, 0],
            [d02_gold],
            forbidden_patterns=[
                {
                    "memory_type": "AHA",
                    "any_atoms": ["candle_blowing", "birthday_applause"],
                    "error_code": "SAME_STORY_AHA",
                }
            ],
        )
    )
    d02_chapter = _prediction_memory(
        "D02-P-CH1",
        "CHAPTER",
        [1080, 1122],
        ["birthday_gathering", "birthday_cake", "candle_blowing", "birthday_applause"],
        ["birthday_cake", "candle_blowing", "birthday_applause"],
        concepts=["ACTIVITY.SHARED_MEAL", "SETTING.HOME", "OCCASION.BIRTHDAY", "OCCASION.FAMILY_GATHERING"],
        title="生日烛光",
        story="烛光亮起后，笑声和掌声围住了这一桌晚餐。",
        time_label="晚上",
    )
    trials.append(_trial("T-D02-NOMINAL", "D02", "CHAPTER_DAY", [d02_chapter]))

    d03_chapter_gold = _gold_memory(
        "D03-G-CH1",
        "CHAPTER",
        [420, 482],
        ["mountain_hike"],
        ["mountain_hike", "forest_trail", "ridge_view"],
        required_concepts=["ACTIVITY.WALKING"],
        allowed_concepts=["ACTIVITY.WALKING", "SETTING.OUTDOOR_NATURE"],
        required_media_atoms=["forest_trail", "ridge_view"],
    )
    d03_aha_gold = _gold_memory(
        "D03-G-AH1",
        "AHA",
        [456, 466],
        ["rainbow_appears"],
        ["rainbow_appears", "rainbow_over_valley"],
        allowed_concepts=["SETTING.OUTDOOR_NATURE"],
        required_media_atoms=["rainbow_over_valley"],
        story_role="EMBEDDED_DISTINCT_PEAK",
    )
    days.append(
        _day(
            "D03",
            "晨间徒步遇见彩虹",
            "OUTDOOR_EXPLORER",
            [
                _segment(420, 432, ["mountain_hike", "forest_trail", "morning_mist"]),
                _segment(434, 446, ["mountain_hike", "uphill_steps", "forest_trail"]),
                _segment(448, 454, ["mountain_hike", "ridge_view", "cloud_break"]),
                _segment(456, 464, ["rainbow_appears", "rainbow_over_valley", "ridge_view"]),
                _segment(466, 480, ["mountain_hike", "ridge_view", "descent_trail"]),
            ],
            "CHAPTER_DAY",
            [1, 1],
            [1, 1],
            [d03_chapter_gold, d03_aha_gold],
            distinct_pairs=[
                {
                    "chapter_gold_id": "D03-G-CH1",
                    "aha_gold_id": "D03-G-AH1",
                    "chapter_forbidden_atoms": ["rainbow_appears", "rainbow_over_valley"],
                    "aha_forbidden_atoms": ["forest_trail", "descent_trail"],
                }
            ],
        )
    )
    d03_chapter = _prediction_memory(
        "D03-P-CH1",
        "CHAPTER",
        [420, 482],
        ["mountain_hike", "forest_trail", "ridge_view", "descent_trail"],
        ["forest_trail", "ridge_view", "descent_trail"],
        concepts=["ACTIVITY.WALKING", "SETTING.OUTDOOR_NATURE"],
        title="山路清晨",
        story="雾气沿着山路散开，登上山脊时视野也亮了起来。",
        time_label="清晨",
    )
    d03_aha = _prediction_memory(
        "D03-P-AH1",
        "AHA",
        [456, 466],
        ["rainbow_appears", "rainbow_over_valley"],
        ["rainbow_over_valley"],
        concepts=["SETTING.OUTDOOR_NATURE"],
        moment_line="彩虹忽然横过山谷。",
        time_label="07:36",
    )
    trials.append(_trial("T-D03-NOMINAL", "D03", "CHAPTER_DAY", [d03_chapter, d03_aha]))

    days.append(
        _day(
            "D04",
            "普通通勤与重复办公",
            "URBAN_WORKER",
            [
                _segment(480, 492, ["routine_commute", "subway_interior"], support="MODERATE"),
                _segment(540, 558, ["routine_desk_work", "computer_screen"], support="MODERATE"),
                _segment(720, 732, ["routine_desk_work", "meeting_room"], support="MODERATE"),
                _segment(1080, 1092, ["routine_commute", "subway_interior"], support="MODERATE"),
            ],
            "EMPTY_DAY",
            [0, 0],
            [0, 0],
            [],
            review_prompts=["普通且重复的工作日保持 EMPTY_DAY，不为满足数量而生成。"],
        )
    )
    trials.append(_trial("T-D04-NOMINAL", "D04", "EMPTY_DAY", []))

    d05_gold = _gold_memory(
        "D05-G-AH1",
        "AHA",
        [1188, 1200],
        ["proposal_ring_reveal"],
        ["proposal_ring_reveal", "surprised_embrace"],
        optional_atoms=["restaurant_dinner"],
        allowed_concepts=["ACTIVITY.SHARED_MEAL"],
        required_media_atoms=["proposal_ring_reveal"],
        story_role="SPARSE_DAY_PEAK",
    )
    days.append(
        _day(
            "D05",
            "平静晚餐中的求婚瞬间",
            "OCCASIONAL_CAPTURE",
            [
                _segment(1170, 1180, ["restaurant_dinner", "table_conversation"], source_kind="MANUAL_VIDEO"),
                _segment(1182, 1186, ["restaurant_dinner", "dessert_plate"], source_kind="MANUAL_PHOTO"),
                _segment(1188, 1196, ["restaurant_dinner", "proposal_ring_reveal", "surprised_embrace"], source_kind="MANUAL_VIDEO"),
            ],
            "HIGHLIGHT_DAY",
            [0, 0],
            [1, 1],
            [d05_gold],
        )
    )
    d05_aha = _prediction_memory(
        "D05-P-AH1",
        "AHA",
        [1188, 1200],
        ["proposal_ring_reveal", "surprised_embrace", "restaurant_dinner"],
        ["proposal_ring_reveal"],
        concepts=["ACTIVITY.SHARED_MEAL"],
        moment_line="戒指亮起，拥抱随即落下。",
        time_label="19:48",
    )
    trials.append(_trial("T-D05-NOMINAL", "D05", "HIGHLIGHT_DAY", [d05_aha]))

    d06_gold = _gold_memory(
        "D06-G-CH1",
        "CHAPTER",
        [660, 752],
        ["food_crawl"],
        ["food_crawl", "hot_noodle_bowl", "street_snack", "dessert_cup"],
        forbidden_atoms=["food_delicious"],
        required_concepts=["CENTRAL_SUBJECT.FOOD_OR_DESSERT"],
        allowed_concepts=["ACTIVITY.WALKING", "ACTIVITY.SHARED_MEAL", "CENTRAL_SUBJECT.FOOD_OR_DESSERT"],
        required_media_atoms=["hot_noodle_bowl", "street_snack", "dessert_cup"],
    )
    days.append(
        _day(
            "D06",
            "周末小吃一路逛",
            "FOOD_EXPLORER",
            [
                _segment(660, 674, ["food_crawl", "market_walk", "food_stalls"]),
                _segment(676, 690, ["food_crawl", "hot_noodle_bowl", "noodle_shop"]),
                _segment(692, 708, ["food_crawl", "market_walk", "street_snack"]),
                _segment(710, 728, ["food_crawl", "shared_table", "grilled_food"]),
                _segment(730, 750, ["food_crawl", "dessert_cup", "market_walk"]),
            ],
            "CHAPTER_DAY",
            [1, 1],
            [0, 0],
            [d06_gold],
        )
    )
    d06_chapter = _prediction_memory(
        "D06-P-CH1",
        "CHAPTER",
        [660, 752],
        ["food_crawl", "hot_noodle_bowl", "street_snack", "dessert_cup", "market_walk"],
        ["hot_noodle_bowl", "street_snack", "dessert_cup"],
        concepts=["ACTIVITY.WALKING", "ACTIVITY.SHARED_MEAL", "CENTRAL_SUBJECT.FOOD_OR_DESSERT"],
        title="一路小吃",
        story="热汤之后，又在街角遇见一份小甜点。",
        time_label="中午",
    )
    trials.append(_trial("T-D06-NOMINAL", "D06", "CHAPTER_DAY", [d06_chapter]))

    d07_gold = _gold_memory(
        "D07-G-CH1",
        "CHAPTER",
        [540, 662],
        ["cat_at_home"],
        ["cat_at_home", "cat_by_window", "cat_chasing_string", "cat_napping"],
        required_concepts=["CENTRAL_SUBJECT.CAT"],
        allowed_concepts=["SETTING.HOME", "CENTRAL_SUBJECT.CAT"],
        required_media_atoms=["cat_by_window", "cat_chasing_string", "cat_napping"],
    )
    days.append(
        _day(
            "D07",
            "居家陪猫的重复日常",
            "PET_COMPANION",
            [
                _segment(540, 558, ["cat_at_home", "cat_napping", "sofa"]),
                _segment(560, 582, ["cat_at_home", "cat_by_window", "window_light"]),
                _segment(584, 606, ["cat_at_home", "cat_chasing_string", "playful_cat"]),
                _segment(608, 632, ["cat_at_home", "cat_by_window", "window_light"]),
                _segment(634, 660, ["cat_at_home", "cat_napping", "sofa"]),
            ],
            "CHAPTER_DAY",
            [1, 1],
            [0, 0],
            [d07_gold],
        )
    )
    d07_chapter = _prediction_memory(
        "D07-P-CH1",
        "CHAPTER",
        [540, 662],
        ["cat_at_home", "cat_by_window", "cat_chasing_string", "cat_napping"],
        ["cat_by_window", "cat_chasing_string", "cat_napping"],
        concepts=["SETTING.HOME", "CENTRAL_SUBJECT.CAT"],
        title="有猫作伴",
        story="窗边晒过太阳，小猫又追着线团闹了一阵。",
        time_label="上午",
    )
    trials.append(_trial("T-D07-NOMINAL", "D07", "CHAPTER_DAY", [d07_chapter]))

    d08_gold = _gold_memory(
        "D08-G-CH1",
        "CHAPTER",
        [840, 932],
        ["pottery_workshop"],
        ["pottery_workshop", "clay_wedging", "wheel_shaping", "surface_carving"],
        optional_atoms=["glaze_brushing"],
        forbidden_atoms=["finished_pot"],
        required_concepts=["ACTIVITY.POTTERY"],
        allowed_concepts=["ACTIVITY.CRAFT", "ACTIVITY.POTTERY", "CENTRAL_SUBJECT.CRAFT_OBJECT"],
        required_media_atoms=["clay_wedging", "wheel_shaping", "surface_carving"],
    )
    days.append(
        _day(
            "D08",
            "手作陶艺过程",
            "HOBBY_MAKER",
            [
                _segment(840, 852, ["pottery_workshop", "clay_wedging"], source_kind="MANUAL_VIDEO"),
                _segment(854, 878, ["pottery_workshop", "wheel_shaping", "wet_clay"], source_kind="MANUAL_VIDEO"),
                _segment(880, 900, ["pottery_workshop", "surface_carving", "craft_tools"], source_kind="MANUAL_VIDEO"),
                _segment(902, 916, ["pottery_workshop", "glaze_brushing", "craft_tools"], source_kind="MANUAL_VIDEO"),
                _segment(918, 930, ["pottery_workshop", "unfinished_clay_form"], source_kind="MANUAL_PHOTO"),
            ],
            "CHAPTER_DAY",
            [1, 1],
            [0, 0],
            [d08_gold],
        )
    )
    d08_chapter = _prediction_memory(
        "D08-P-CH1",
        "CHAPTER",
        [840, 932],
        ["pottery_workshop", "clay_wedging", "wheel_shaping", "surface_carving", "glaze_brushing"],
        ["clay_wedging", "wheel_shaping", "surface_carving", "glaze_brushing"],
        concepts=["ACTIVITY.CRAFT", "ACTIVITY.POTTERY", "CENTRAL_SUBJECT.CRAFT_OBJECT"],
        title="泥土成形",
        story="泥土在手里旋转，轮廓一点点清晰起来。",
        time_label="下午",
    )
    trials.append(_trial("T-D08-NOMINAL", "D08", "CHAPTER_DAY", [d08_chapter]))

    d09_gold_memories = [
        _gold_memory(
            "D09-G-CH1", "CHAPTER", [480, 512], ["morning_commute"],
            ["morning_commute", "bike_lane", "station_arrival"],
            allowed_concepts=["ACTIVITY.WALKING"],
            required_media_atoms=["bike_lane", "station_arrival"],
        ),
        _gold_memory(
            "D09-G-CH2", "CHAPTER", [540, 722], ["office_work_block"],
            ["office_work_block", "team_meeting", "desk_focus"],
            allowed_concepts=["SETTING.WORKPLACE"],
            required_media_atoms=["team_meeting", "desk_focus"],
        ),
        _gold_memory(
            "D09-G-CH3", "CHAPTER", [1080, 1112], ["friend_dinner"],
            ["friend_dinner", "shared_dishes", "restaurant_table"],
            allowed_concepts=["ACTIVITY.SHARED_MEAL"],
            required_media_atoms=["shared_dishes", "restaurant_table"],
        ),
    ]
    days.append(
        _day(
            "D09",
            "通勤办公与朋友晚餐",
            "URBAN_WORKER_SOCIAL",
            [
                _segment(480, 492, ["morning_commute", "bike_lane", "city_street"]),
                _segment(494, 510, ["morning_commute", "station_arrival", "transit_platform"]),
                _segment(540, 566, ["office_work_block", "desk_focus", "computer_screen"]),
                _segment(568, 600, ["office_work_block", "team_meeting", "meeting_room"]),
                _segment(602, 650, ["office_work_block", "desk_focus", "computer_screen"]),
                _segment(652, 690, ["office_work_block", "whiteboard_discussion", "team_meeting"]),
                _segment(692, 720, ["office_work_block", "desk_focus", "notebook"]),
                _segment(1080, 1094, ["friend_dinner", "restaurant_table", "arrival_greeting"]),
                _segment(1096, 1110, ["friend_dinner", "shared_dishes", "table_conversation"]),
            ],
            "CHAPTER_DAY",
            [3, 3],
            [0, 0],
            d09_gold_memories,
        )
    )
    d09_predictions = [
        _prediction_memory(
            "D09-P-CH1", "CHAPTER", [480, 512],
            ["morning_commute", "bike_lane", "station_arrival", "city_street"],
            ["bike_lane", "station_arrival", "city_street"], concepts=[], title="清晨通勤",
            story="沿着车道出发，城市在到站前慢慢醒来。", time_label="早晨",
        ),
        _prediction_memory(
            "D09-P-CH2", "CHAPTER", [540, 722],
            ["office_work_block", "team_meeting", "desk_focus", "whiteboard_discussion"],
            ["team_meeting", "desk_focus", "whiteboard_discussion"], concepts=["SETTING.WORKPLACE"], title="工作节奏",
            story="会议和专注工作的片段，交替填满了白天。", time_label="白天",
        ),
        _prediction_memory(
            "D09-P-CH3", "CHAPTER", [1080, 1112],
            ["friend_dinner", "shared_dishes", "restaurant_table", "table_conversation"],
            ["shared_dishes", "restaurant_table", "table_conversation"], concepts=["ACTIVITY.SHARED_MEAL"], title="朋友晚餐",
            story="几道菜陆续上桌，聊天也跟着热闹起来。", time_label="晚上",
        ),
    ]
    trials.append(_trial("T-D09-NOMINAL", "D09", "CHAPTER_DAY", d09_predictions))

    d10_gold = _gold_memory(
        "D10-G-CH1",
        "CHAPTER",
        [600, 782],
        ["museum_visit"],
        ["museum_visit", "sculpture_hall", "painting_gallery", "artifact_display"],
        allowed_concepts=["ACTIVITY.WALKING"],
        required_media_atoms=["sculpture_hall", "painting_gallery", "artifact_display"],
    )
    days.append(
        _day(
            "D10",
            "博物馆多展厅参观",
            "CULTURE_VISITOR",
            [
                _segment(600, 620, ["museum_visit", "museum_entry", "grand_staircase"]),
                _segment(622, 654, ["museum_visit", "sculpture_hall", "stone_sculpture"]),
                _segment(656, 688, ["museum_visit", "painting_gallery", "framed_paintings"]),
                _segment(690, 714, ["museum_visit", "rest_bench", "gallery_corridor"]),
                _segment(716, 750, ["museum_visit", "artifact_display", "glass_cases"]),
                _segment(752, 780, ["museum_visit", "museum_exit", "gift_shop"]),
            ],
            "CHAPTER_DAY",
            [1, 1],
            [0, 0],
            [d10_gold],
        )
    )
    d10_chapter = _prediction_memory(
        "D10-P-CH1",
        "CHAPTER",
        [600, 782],
        ["museum_visit", "sculpture_hall", "painting_gallery", "artifact_display"],
        ["sculpture_hall", "painting_gallery", "artifact_display"],
        concepts=["ACTIVITY.WALKING"],
        title="穿行展厅",
        story="从雕塑到画作，再到玻璃柜里的旧物，脚步一直向前。",
        time_label="上午",
    )
    trials.append(_trial("T-D10-NOMINAL", "D10", "CHAPTER_DAY", [d10_chapter]))

    d11_chapter_gold = _gold_memory(
        "D11-G-CH1",
        "CHAPTER",
        [900, 982],
        ["family_park_walk"],
        ["family_park_walk", "tree_lined_path", "family_picnic"],
        required_concepts=["OCCASION.FAMILY_GATHERING"],
        allowed_concepts=["ACTIVITY.WALKING", "SETTING.OUTDOOR_NATURE", "OCCASION.FAMILY_GATHERING"],
        required_media_atoms=["tree_lined_path", "family_picnic"],
    )
    d11_aha_gold = _gold_memory(
        "D11-G-AH1",
        "AHA",
        [938, 950],
        ["child_chases_bubbles"],
        ["child_chases_bubbles", "bubbles_in_sunlight"],
        allowed_concepts=["SETTING.OUTDOOR_NATURE", "OCCASION.FAMILY_GATHERING"],
        required_media_atoms=["child_chases_bubbles"],
        requirement="OPTIONAL_REVIEW",
        story_role="EMBEDDED_VALUE_UNRESOLVED",
    )
    days.append(
        _day(
            "D11",
            "家庭公园散步与泡泡游戏",
            "FAMILY_WEEKEND",
            [
                _segment(900, 918, ["family_park_walk", "tree_lined_path", "family_together"]),
                _segment(920, 936, ["family_park_walk", "family_picnic", "grass_lawn"]),
                _segment(938, 948, ["family_park_walk", "child_chases_bubbles", "bubbles_in_sunlight"]),
                _segment(950, 964, ["family_park_walk", "playground", "family_together"]),
                _segment(966, 980, ["family_park_walk", "tree_lined_path", "park_exit"]),
            ],
            "CHAPTER_DAY",
            [1, 1],
            [0, 1],
            [d11_chapter_gold, d11_aha_gold],
            distinct_pairs=[
                {
                    "chapter_gold_id": "D11-G-CH1",
                    "aha_gold_id": "D11-G-AH1",
                    "chapter_forbidden_atoms": ["child_chases_bubbles", "bubbles_in_sunlight"],
                    "aha_forbidden_atoms": ["family_picnic", "tree_lined_path"],
                }
            ],
            review_prompts=["泡泡游戏是否有足够独立的用户价值成为 Aha，而不是只留在家庭公园 Chapter。"],
        )
    )
    d11_chapter = _prediction_memory(
        "D11-P-CH1",
        "CHAPTER",
        [900, 982],
        ["family_park_walk", "tree_lined_path", "family_picnic", "playground"],
        ["tree_lined_path", "family_picnic", "playground"],
        concepts=["ACTIVITY.WALKING", "SETTING.OUTDOOR_NATURE", "OCCASION.FAMILY_GATHERING"],
        title="公园午后",
        story="树影下走走停停，一家人的午后显得很松弛。",
        time_label="下午",
    )
    trials.append(
        _trial(
            "T-D11-NOMINAL",
            "D11",
            "CHAPTER_DAY",
            [d11_chapter],
            expected_status="REVIEW",
            required_error_codes=["OPTIONAL_MEMORY_REVIEW"],
        )
    )

    d12_gold_memories = [
        _gold_memory(
            "D12-G-CH1", "CHAPTER", [390, 452], ["morning_run"],
            ["morning_run", "riverside_path", "sunrise_light"],
            required_concepts=["ACTIVITY.WALKING"],
            allowed_concepts=["ACTIVITY.WALKING", "SETTING.OUTDOOR_NATURE"],
            required_media_atoms=["riverside_path", "sunrise_light"],
        ),
        _gold_memory(
            "D12-G-CH2", "CHAPTER", [1200, 1282], ["evening_concert"],
            ["evening_concert", "stage_lights", "live_performance"],
            allowed_concepts=[],
            required_media_atoms=["stage_lights", "live_performance"],
        ),
    ]
    days.append(
        _day(
            "D12",
            "多次同步的晨跑与晚间演出",
            "ACTIVE_MUSIC_FAN",
            [
                _segment(390, 408, ["morning_run", "riverside_path", "dawn_sky"], import_batch_id="B1"),
                _segment(410, 430, ["morning_run", "sunrise_light", "river_view"], import_batch_id="B1"),
                _segment(432, 450, ["morning_run", "riverside_path", "cool_down"], import_batch_id="B1"),
                _segment(1200, 1218, ["evening_concert", "venue_entry", "crowd"], import_batch_id="B2"),
                _segment(1220, 1250, ["evening_concert", "stage_lights", "live_performance"], import_batch_id="B2"),
                _segment(1252, 1280, ["evening_concert", "live_performance", "audience_applause"], import_batch_id="B2"),
            ],
            "CHAPTER_DAY",
            [2, 2],
            [0, 0],
            d12_gold_memories,
        )
    )
    d12_predictions = [
        _prediction_memory(
            "D12-P-CH1", "CHAPTER", [390, 452],
            ["morning_run", "riverside_path", "sunrise_light", "river_view"],
            ["riverside_path", "sunrise_light", "river_view"],
            concepts=["ACTIVITY.WALKING", "SETTING.OUTDOOR_NATURE"], title="河边晨跑",
            story="天色沿着河面亮起，晨跑也渐渐进入节奏。", time_label="清晨",
        ),
        _prediction_memory(
            "D12-P-CH2", "CHAPTER", [1200, 1282],
            ["evening_concert", "stage_lights", "live_performance", "audience_applause"],
            ["stage_lights", "live_performance", "audience_applause"], concepts=[], title="舞台亮起",
            story="灯光落下时，晚上的节奏从舞台一路推向人群。", time_label="晚上",
        ),
    ]
    trials.append(_trial("T-D12-NOMINAL", "D12", "CHAPTER_DAY", d12_predictions))

    # Four deliberate failures prove attribution instead of merely proving that
    # the nominal reference examples can pass their own evaluator.
    d01_split_left = _prediction_memory(
        "D01-X-CH1", "CHAPTER", [540, 572],
        ["ancient_town_walk", "historic_architecture", "stone_lane", "historic_gate", "wood_carving"],
        ["historic_gate", "wood_carving"],
        concepts=["ACTIVITY.CITY_WALK", "SETTING.TRADITIONAL_HISTORIC_DISTRICT", "CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE", "OCCASION.TRAVEL_OUTING"],
        title="古镇前段", story="牌坊之后，石板路带着脚步走进老街。", time_label="上午",
    )
    d01_split_right = _prediction_memory(
        "D01-X-CH2", "CHAPTER", [594, 604],
        ["ancient_town_walk", "historic_architecture", "stone_lane"],
        ["historic_architecture", "stone_lane"],
        concepts=["ACTIVITY.CITY_WALK", "SETTING.TRADITIONAL_HISTORIC_DISTRICT", "CENTRAL_SUBJECT.HISTORIC_ARCHITECTURE", "OCCASION.TRAVEL_OUTING"],
        title="重回老街", story="走出小店，石板路又接回了原来的街巷。", time_label="上午",
    )
    trials.append(
        _trial(
            "T-D01-FALSE-SPLIT", "D01", "CHAPTER_DAY",
            [d01_split_left, d01_split_right, copy.deepcopy(d01_aha)],
            trial_kind="FAILURE_INJECTION", expected_status="QUALITY_FAIL",
            required_error_codes=["FALSE_SPLIT"],
        )
    )

    d02_same_story_aha = _prediction_memory(
        "D02-X-AH1", "AHA", [1102, 1110],
        ["birthday_gathering", "candle_blowing", "birthday_applause"],
        ["candle_blowing"], concepts=["OCCASION.BIRTHDAY"],
        moment_line="蜡烛吹灭，掌声响起。", time_label="18:22",
    )
    trials.append(
        _trial(
            "T-D02-SAME-STORY-AHA", "D02", "CHAPTER_DAY",
            [copy.deepcopy(d02_chapter), d02_same_story_aha],
            trial_kind="FAILURE_INJECTION", expected_status="BLOCKING_FAIL",
            required_error_codes=["SAME_STORY_AHA"],
        )
    )

    d06_unsupported = copy.deepcopy(d06_chapter)
    d06_unsupported["memory_id"] = "D06-X-CH1"
    d06_unsupported["asserted_atoms"] = list(d06_unsupported["asserted_atoms"]) + ["food_delicious"]
    for index, media in enumerate(d06_unsupported["media"]):
        media["media_id"] = f"D06-X-CH1-M{index + 1}"
    trials.append(
        _trial(
            "T-D06-UNSUPPORTED-TASTE", "D06", "CHAPTER_DAY", [d06_unsupported],
            trial_kind="FAILURE_INJECTION", expected_status="BLOCKING_FAIL",
            required_error_codes=["UNSUPPORTED_ASSERTION"],
        )
    )

    d09_merged = _prediction_memory(
        "D09-X-CH1", "CHAPTER", [480, 722],
        ["morning_commute", "bike_lane", "station_arrival", "office_work_block", "team_meeting", "desk_focus"],
        ["bike_lane", "team_meeting", "desk_focus"], concepts=[], title="从路上到工位",
        story="通勤结束后，白天很快进入会议和专注工作的节奏。", time_label="上午至白天",
    )
    trials.append(
        _trial(
            "T-D09-FALSE-MERGE", "D09", "CHAPTER_DAY",
            [d09_merged, copy.deepcopy(d09_predictions[2])],
            trial_kind="FAILURE_INJECTION", expected_status="BLOCKING_FAIL",
            required_error_codes=["FALSE_MERGE"],
        )
    )

    return {
        "contract_version": SUITE_CONTRACT_VERSION,
        "suite_id": "V02_HIGH_PROBABILITY_USER_DAYS_2026_08_29",
        "title": "Diary One V01/V02 semantic day conformance suite",
        "evidence_scope": "SEMANTIC_TIMELINE_ONLY",
        "narrative_locale": "zh-CN",
        "pipeline_contract_ref": "DIARY_ONE_PRODUCTION_PIPELINE_V1_0",
        "days": days,
        "trials": trials,
    }
