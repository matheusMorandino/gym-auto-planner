import os
import pandas as pd
from typing import List, Dict

import src.utils as utils
from src.models.data_models import Exercise, Muscle


ROOT_DIR = os.path.dirname(os.path.dirname(os.getcwd()))


def __build_training_list(df_raw: pd.DataFrame) -> Dict[str, Exercise]:
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

    return {row['name']: Exercise(**row) for _, row in df_raw.iterrows()}


# Raw dataframe with exercise data
RAW_EXERCISE_TABLE = pd.read_csv(os.path.join(ROOT_DIR, 'datasets', 'gym_exercise_dataset.csv'))

# Dict listing all the exercises using the Exercise datamodel
EXERCISE_DICT = __build_training_list(RAW_EXERCISE_TABLE)

# Mappings for muscle and muscle groups in the SVG image
SVG_TO_MUSCLES = utils.read_json(os.path.join(ROOT_DIR, 'datasets', 'muscle_mapping.json'))

# Dict listing all muscles present
MUSCLES_DICT = {name: Muscle(name=name) for name in [item for sublist in SVG_TO_MUSCLES.values() for item in sublist]}

# M constant for Big-M constrain
M: int = 1e4
