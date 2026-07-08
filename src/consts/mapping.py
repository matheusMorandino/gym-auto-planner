import os
import pandas as pd
from typing import List, Tuple, Dict

import src.utils as utils
from src.models.data_models import Exercise, Muscle, Equipment, MuscleGroup

ROOT_DIR = os.path.dirname(os.path.dirname(os.getcwd()))


def __build_training_list(df_raw: pd.DataFrame) -> Dict[Tuple[str, str], Exercise]:
    """
    Returns a Dict of Exercise objects
    :param df_raw:
    :return:
    """
    # Normalize exercise name
    df_raw['name'] = df_raw['Exercise Name'].apply(lambda x: ' '.join(x.split()).replace('\u200b', ''))

    # Normalize equipment name
    df_raw['equipment'] = df_raw['Equipment'].apply(lambda x: ' '.join(x.split()).replace('\u200b', ''))

    # Normalize name of primary_muscles
    df_raw['primary_muscles'] = df_raw.apply(
        lambda x: [
            ' '.join(m.split())
            for m
            in x['Target_Muscles'].split(',') if len(m.strip()) > 0
        ], axis=1)

    # Normalize name of secondary_muscles
    df_raw['secondary_muscles'] = df_raw.apply(
        lambda x: [
            ' '.join(m.split())
            for m
            in (x['Secondary Muscles'].split(',') if isinstance(x['Secondary Muscles'], str) else [])
            if len(m.strip()) > 0
        ], axis=1)

    df_raw = df_raw[['name', 'equipment', 'primary_muscles', 'secondary_muscles']]

    return {(row['name'], row['equipment']): Exercise(**row) for _, row in df_raw.iterrows()}


def __get_all_equipments(df_raw: pd.DataFrame) -> Dict[str, Equipment]:
    equip_list = df_raw['Equipment'].apply(
        lambda x: ' '.join(x.split()).replace('\u200b', '')).drop_duplicates().to_list()

    return {str(equip): Equipment(name=equip) for equip in equip_list}


def __get_all_muscle_groups(mapping_path: str) -> Dict[str, MuscleGroup]:
    mapping = utils.read_json(mapping_path)

    return {
        group_name: MuscleGroup(
            name=group_name,
            components=[Muscle(name=name) for name in group_components]
        )
        for group_name, group_components
        in mapping.items()
    }

# Raw dataframe with exercise data
RAW_EXERCISE_TABLE = pd.read_csv(os.path.join(ROOT_DIR, 'datasets', 'gym_exercise_dataset.csv'))

# Dict listing all the exercises using the Exercise dataclass
EXERCISE_DICT = __build_training_list(df_raw=RAW_EXERCISE_TABLE)

# Mappings for muscle and muscle groups in the SVG image
MUSCLE_GROUPS = __get_all_muscle_groups(mapping_path=os.path.join(ROOT_DIR, 'datasets', 'muscle_mapping.json'))

# Dict listing all muscles present
MUSCLES_DICT = {
    muscle.name: muscle for muscle in [muscle for group in MUSCLE_GROUPS.values() for muscle in group.components]}

# Dict listing of all equipments available across all exercises
EQUIPMENT_DICT = __get_all_equipments(df_raw=RAW_EXERCISE_TABLE)

# M constant for Big-M constrain
M: int = 1e4
