import os
import pandas as pd
from typing import List, Tuple, Dict

import src.utils as utils
from src.models.data_models import Exercise, Muscle, Equipment, MuscleGroup

ROOT_DIR = os.path.dirname(os.path.dirname(os.getcwd()))


def __extract_list_from_str(text: str, sep: str = ',', none_ignore: bool = True) -> List[str]:
    """
    Extracts a list of strings from a string, using the given separator.
    :param text: The input string to be split.
    :param sep: The separator to use for splitting the string.
    :param none_ignore: If True, ignores empty strings in the result.
    :return: A list of strings extracted from the input string.
    """
    if not isinstance(text, str):
        return []

    result = [item.strip() for item in text.split(sep)]
    if none_ignore:
        result = [item for item in result if item and item != 'None']

    return result


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
            in __extract_list_from_str(x['Secondary Muscles'])
            if len(m.strip()) > 0
        ], axis=1)

    # Normalize name of synergistic_muscles
    df_raw['synergistic_muscles'] = df_raw.apply(
        lambda x: [
            ' '.join(m.split())
            for m
            in __extract_list_from_str(x['Synergist_Muscles'])
            if len(m.strip()) > 0
        ], axis=1)

    # Normalize name of stabilizing_muscles
    df_raw['stabilizing_muscles'] = df_raw.apply(
        lambda x: [
            ' '.join(m.split())
            for m
            in __extract_list_from_str(x['Stabilizer_Muscles'])
            if len(m.strip()) > 0
        ], axis=1)

    # Normalize name of antagonist_muscles
    df_raw['antagonist_muscles'] = df_raw.apply(
        lambda x: [
            ' '.join(m.split())
            for m
            in __extract_list_from_str(x['Antagonist_Muscles'])
            if len(m.strip()) > 0
        ], axis=1)

    # Normalize name of dynamic_muscles
    df_raw['dynamic_muscles'] = df_raw.apply(
        lambda x: [
            ' '.join(m.split())
            for m
            in __extract_list_from_str(x['Dynamic_Stabilizer_Muscles'])
            if len(m.strip()) > 0
        ], axis=1)

    df_raw = df_raw[[
        'name',
        'equipment',
        'primary_muscles',
        'secondary_muscles',
        'synergistic_muscles',
        'stabilizing_muscles',
        'antagonist_muscles',
        'dynamic_muscles'
    ]]

    # Building muscle usage vector
    df_raw['muscle_vector'] = df_raw.apply(
        lambda x: {
            muscle:
            1
                if muscle
                in (x['primary_muscles'] +
                 x['secondary_muscles'] +
                 x['synergistic_muscles'] +
                 x['stabilizing_muscles'] +
                 x['antagonist_muscles'] +
                 x['dynamic_muscles'])
                else 0
            for muscle
            in MUSCLES_DICT.keys()},
        axis=1
    )

    return {row['name']: Exercise(**row) for _, row in df_raw.iterrows()}


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

# Mappings for muscle and muscle groups in the SVG image
MUSCLE_GROUPS = __get_all_muscle_groups(mapping_path=os.path.join(ROOT_DIR, 'datasets', 'muscle_mapping.json'))

# Dict listing all muscles present
MUSCLES_DICT = {
    muscle.name: muscle for muscle in [muscle for group in MUSCLE_GROUPS.values() for muscle in group.components]}

# Dict listing all the exercises using the Exercise dataclass
EXERCISE_DICT = __build_training_list(df_raw=RAW_EXERCISE_TABLE)

# Dict listing of all equipments available across all exercises
EQUIPMENT_DICT = __get_all_equipments(df_raw=RAW_EXERCISE_TABLE)
