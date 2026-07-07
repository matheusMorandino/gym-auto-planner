import os

import src.utils as utils


ROOT_DIR = os.path.dirname(os.getcwd())

SVG_TO_MUSCLES = utils.read_json(os.path.join(ROOT_DIR, 'datasets', 'svg_to_muscles.json'))
