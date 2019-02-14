# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import numpy as np
import os

sys.path.append('./models/research/slim/')  # add slim to PYTHONPATH

from datasets import imagenet
from nets import inception
from nets import resnet_v1
from nets import inception_utils
from nets import resnet_utils
from preprocessing import inception_preprocessing
from nets import nets_factory
from preprocessing import preprocessing_factory
import traceback

import tensorflow as tf
import time

# temp1 = './data/images/products_test/valid_list.txt'
# temp2 = './data/models/products-models/resnet_v1_50/bottleneck_tr_90/'
results_path = './results/'
probabilites_path = results_path + 'image_classifcation_probabilites.txt'
tf.app.flags.DEFINE_integer('num_classes', 2, 'The number of classes.')
tf.app.flags.DEFINE_string('infile', None , 'Image file, one image per line.')  # input file
tf.app.flags.DEFINE_boolean('tfrecord', False, 'Input file is formatted as TFRecord.')
tf.app.flags.DEFINE_string('outfile', probabilites_path, 'Output file for prediction probabilities.')
tf.app.flags.DEFINE_string('model_name', 'resnet_v1_50', 'The name of the architecture to evaluate.')
tf.app.flags.DEFINE_string('preprocessing_name', None,
                           'The name of the preprocessing to use. If left as `None`, then the model_name flag is used.')
tf.app.flags.DEFINE_string('checkpoint_path', None,
                           'The directory where the model was written to or an absolute path to a checkpoint file.')
tf.app.flags.DEFINE_integer('eval_image_size', None, 'Eval image size.')
FLAGS = tf.app.flags.FLAGS

slim = tf.contrib.slim

model_name_to_variables = {'nuclei':'nuclei',
                           'inception_v3':'InceptionV3', 'inception_v4':'InceptionV4', 'resnet_v1_50':'resnet_v1_50', 'resnet_v1_152':'resnet_v1_152'}

preprocessing_name = FLAGS.preprocessing_name or FLAGS.model_name
eval_image_size = FLAGS.eval_image_size


def main(_):
  if not FLAGS.infile:
    raise ValueError('You must supply the dataset directory with --infile')
  if FLAGS.tfrecord:
    fls = tf.python_io.tf_record_iterator(path=FLAGS.infile)
  else:
    fls = [s.strip() for s in open(FLAGS.infile)]

  model_variables = model_name_to_variables.get(FLAGS.model_name)
  if model_variables is None:
    tf.logging.error("Unknown model_name provided `%s`." % FLAGS.model_name)
    sys.exit(-1)

  if FLAGS.tfrecord:
    tf.logging.warn('Image name is not available in TFRecord file.')

  if tf.gfile.IsDirectory(FLAGS.checkpoint_path):
    checkpoint_path = tf.train.latest_checkpoint(FLAGS.checkpoint_path)
  else:
    checkpoint_path = FLAGS.checkpoint_path

  #image = tf.placeholder(tf.string)  # Entry to the computational graph, e.g. image_string = tf.gfile.FastGFile(image_file).read()
  image_string = tf.placeholder(tf.uint8, shape=[None, None, 3])

  # image = tf.image.decode_image(image_string, channels=3)
  #image = tf.image.decode_jpeg(image_string, channels=3, try_recover_truncated=True,
  #                            acceptable_fraction=0.3)  ## To process corrupted image files

  image_preprocessing_fn = preprocessing_factory.get_preprocessing(preprocessing_name, is_training=False)

  network_fn = nets_factory.get_network_fn(FLAGS.model_name, FLAGS.num_classes, is_training=False)

  if FLAGS.eval_image_size is None:
    eval_image_size = network_fn.default_image_size


  processed_image = image_preprocessing_fn(image_string, eval_image_size, eval_image_size)

  processed_images = tf.expand_dims(processed_image,
                                    0)  # Or tf.reshape(processed_image, (1, eval_image_size, eval_image_size, 3))

  # images, labels = tf.train.batch(
  #   [image, label],
  #   batch_size=FLAGS.batch_size,
  #   num_threads=FLAGS.num_preprocessing_threads,
  #   capacity=5 * FLAGS.batch_size)


  logits, _ = network_fn(processed_images)
  #logits, _ = network_fn(processed_images)

  probabilities = tf.nn.softmax(logits)

  init_fn = slim.assign_from_checkpoint_fn(checkpoint_path, slim.get_model_variables(model_variables))

  sess = tf.Session()
  init_fn(sess)

  fout = sys.stdout
  if FLAGS.outfile is not None:
    fout = open(FLAGS.outfile, 'w')

  # h = ['image']
  # h.extend(['class%s' % i for i in range(FLAGS.num_classes)])
  # h.append('predicted_class')
  # print('\t'.join(h), file=fout)

  start_time = time.time()
  start_time_iter = 0

  probs = []
  predict_cls = []
  for fl in fls:
    image_name = None
    # print(fl)


    try:
      if FLAGS.tfrecord is False:
        #tf.logging.warn(fl)
        #x = tf.gfile.FastGFile(fl, 'rb').read()  # You can also use x = open(fl).read()
        # x = open(fl).read()
        image_name = os.path.basename(fl)
        # tf.logging.warn(' image file %s' % image_name)

        ###########################################



        #------------------------------
        import glob
        import scipy.misc

        base_path = './data/1-nuclei/images/original_images/'
        OUTPUT_DIR = './data/1-nuclei/images/fold_1'
        wsize = 32
        hwsize = int(wsize / 2)
        #----------------------

        #bb = glob.glob("%s_*.tif" % (base_fname))
        #aa = sorted(glob.glob("%s_*.tif" % (base_fname)))
        #print(base_path)
        #print(fl)
        ori_img_list = sorted(glob.glob("%s%s_*.tif" % (base_path, fl)))
        #print(ori_img_list)
        for fname in ori_img_list:  # get all of the files which start with this patient ID
          #print(fname)
          fname = '12751_500_f00028_original.tif'


          ori_fname = fname
          fname = fname.split('/')
          fname = fname[-1]
          #print(fname)


          newfname_class = "%s/%s_class.png" % (OUTPUT_DIR, fname[0:-4])  # create the new files
          newfname_prob = "%s/%s_prob.png" % (OUTPUT_DIR, fname[0:-4])

          if (os.path.exists(newfname_class)):  # if this file exists, skip it...this allows us to do work in parallel across many machines
            continue
          print("working on file: \t %s" % fname)

          outputimage = np.zeros(shape=(10, 10))
          scipy.misc.imsave(newfname_class, outputimage)  # first thing we do is save a file to let potential other workers know that this file is being worked on and it should be skipped

          #image = caffe.io.load_image(fname)  # load our image
          #		image = caffe.io.resize_image(image, [image.shape[0]/2,image.shape[1]/2]) #if you need to resize or crop, do it here

          #@@image load
          from PIL import Image
          import numpy
          import cv2
          #image = Image.open(ori_fname)

          #from scipy.ndimage import imread
          #image = imread(ori_fname)
          print(base_path + fname)
          fname = '12751_500_f00028_original.tif'
          image = Image.open(base_path + fname)
          image_temp = image
          # outfile = os.path.splitext(ori_fname)[0] + ".jpg"
          # image.thumbnail(image.size, Image.ANTIALIAS)


          image = np.lib.pad(image, ((hwsize, hwsize), (hwsize, hwsize), (0, 0)),
                             'symmetric')  # mirror the edges so that we can compute the full image

          outputimage_probs = np.zeros(
            shape=(image.shape[0], image.shape[1], 3))  # make the output files where we'll store the data
          outputimage_class = np.zeros(shape=(image.shape[0], image.shape[1]))
          for rowi in range(hwsize + 1, image.shape[0] - hwsize):
            print("%s\t (%.3f,%.3f)\t %d of %d" % (
              ori_fname, time.time() - start_time, time.time() - start_time_iter, rowi, image.shape[0] - hwsize))
            start_time_iter = time.time()
            #patches = []  # create a set of patches, oeprate on a per column basis

            probs = []
            index = 0
            for coli in range(hwsize + 1, image.shape[1] - hwsize):

              patch = image[rowi - hwsize:rowi + hwsize, coli - hwsize:coli + hwsize, :]

              # if coli >= 193 and coli < 198:
              #   border = (coli - hwsize, rowi - hwsize, coli + hwsize, rowi + hwsize)
              #   crop = image_temp.crop(border)
              #   crop.show()
              #   if coli == 197:
              #     break

              prob = sess.run(probabilities, feed_dict={image_string: patch})
              probs.append(prob[0,0:])

            probs = np.array(probs)
            pclass = probs.argmax(axis=1)  # get the argmax
            outputimage_probs[rowi, hwsize + 1:image.shape[1] - hwsize, 0:2] = probs  # save the results to our output images
            outputimage_class[rowi, hwsize + 1:image.shape[1] - hwsize] = pclass


          outputimage_probs = outputimage_probs[hwsize:-hwsize, hwsize:-hwsize, :]  # remove the edge padding
          outputimage_class = outputimage_class[hwsize:-hwsize, hwsize:-hwsize]

          scipy.misc.imsave(newfname_prob, outputimage_probs)  # save the files
          scipy.misc.imsave(newfname_class, outputimage_class)


        ############################################
        #probs = sess.run(probabilities, feed_dict={image_string: x})
        # np_image, network_input, probs = sess.run([image, processed_image, probabilities], feed_dict={image_string:x})

      else:
        example = tf.train.Example()
        example.ParseFromString(fl)

        # Note: The key of example.features.feature depends on how you generate tfrecord.
        x = example.features.feature['image/encoded'].bytes_list.value[0]  # retrieve image string

        image_name = 'TFRecord'


    except Exception:
      traceback.print_exc()
      exit(1)



  # evaluate accuracy

  # generate probabilits list file

  sess.close()
  fout.close()


if __name__ == '__main__':
  tf.app.run()