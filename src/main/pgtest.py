from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import os
import time

from magenta.models.piano_genie import gold
from magenta.models.piano_genie.configs import get_named_config
from magenta.models.piano_genie.loader import load_noteseqs
from magenta.models.piano_genie.model import build_genie_model
import numpy as np
import tensorflow as tf
import json

BASE_DIR = '/Users/timmy/Documents/projects/artuino/'

flags = tf.app.flags
FLAGS = flags.FLAGS

flags.DEFINE_string("dataset_fp", os.path.join(BASE_DIR, 'data/notesequences.tfrecord'),
                    "Path to dataset containing TFRecords of NoteSequences.")
flags.DEFINE_string("train_dir", "", "The directory for this experiment.")
flags.DEFINE_string("model_cfg", "stp_iq_auto_dt", "Hyperparameter configuration.")
flags.DEFINE_string("model_cfg_overrides", "",
                    "E.g. rnn_nlayers=4,rnn_nunits=256")
flags.DEFINE_string("ckpt_fp", os.path.join(BASE_DIR, 'data', 'piano_genie', 'pg_stp_iq_auto_dt.ckpt'),
                    "If specified, only evaluate a single checkpoint.")


def update_with_json_weights(model_vars, json_weights_fp):
    '''loads weights from pretrained weight jsons from 
    https://github.com/tensorflow/magenta-js/tree/master/music/src/piano_genie/test_data
    '''
    print('Loading pretrained weights from: {}'.format(json_weights_fp))
    with open(json_weights_fp, 'r') as f:
        pretrained_variables = json.loads(f.read())

    for var in model_vars:
        name = var.name[:-2]
        pretrained_var = pretrained_variables[name]
        shape = pretrained_var['shape']
        pretrained_var_array = np.array(list(pretrained_var.values())[:-2])\
            .reshape(shape)
        var.assign(pretrained_var_array)


cfg, _ = get_named_config(FLAGS.model_cfg, FLAGS.model_cfg_overrides)

# Load data
with tf.name_scope("loader"):
  feat_dict = load_noteseqs(
      FLAGS.dataset_fp,
      cfg.eval_batch_size,
      cfg.eval_seq_len,
      max_discrete_times=cfg.data_max_discrete_times,
      max_discrete_velocities=cfg.data_max_discrete_velocities,
      augment_stretch_bounds=None,
      augment_transpose_bounds=None,
      randomize_chord_order=cfg.data_randomize_chord_order,
      repeat=False)

# Build model
with tf.variable_scope("phero_model"):
  model_dict = build_genie_model(
      feat_dict,
      cfg,
      cfg.eval_batch_size,
      cfg.eval_seq_len,
      is_training=False)
genie_vars = tf.get_collection(
    tf.GraphKeys.GLOBAL_VARIABLES, scope="phero_model")

# updating variables with pretrained weights
pretrained_vars_fp = os.path.join(BASE_DIR, 'data/piano_genie/testdata/{}.json'.format(FLAGS.model_cfg))
update_with_json_weights(genie_vars, pretrained_vars_fp)