# Nucleui segmentation-tensorflow (in progress)
  
This source is tensorflow version of [1].   
We used tensorflow-slim and implemented on ubuntu 16.04, python3.5, and tensorflow1.13.0rc1.

## Requirments
python3.5  
tensorflow


## Overview  
### Quick start

This script executes train, evalution and segmenation step.
```bash
   cd DEEP_TUTORIAL_ROOT
   ./train_nucleui.sh
```

### Data  
Download [dataset(train and valiation tfRecord)](http://naver.me/Fyamxy1v)
URL_PASSWORD: 1234

```bash
   cd DEEP_TUTORIAL_ROOT/data/1-nuclei/images
   mv DOWNLOAD_DIR/nuclei* ./
```

### Pre-trained model
Download [model(nucleui-models2.zip)](http://naver.me/Fyamxy1v) 
```bash
   cd DEEP_TUTORIAL_ROOT/data/1-nuclei/models
   unzip nucleui-models2.zip
```

For step6 segmentation, original image is on [here](http://andrewjanowczyk.com/wp-static/nuclei.tgz)
 

### Training/Evalution  
```bash
   cd DEEP_TUTORIAL_ROOT/
   step1_patch_extraction.py 
   step2_cross_validation_creation.py (training and testing list creation step)
   step3_generate_datasets (make tensorflow-slim data format (tfRecord)
   step4_train_image_classifier.py (training step)
   step5_eval_image_classifier.py (testing step)
```

### Segmentation
```bash
   cd DEEP_TUTORIAL_ROOT/
   step6_segment_test_images.py (segmentation for test image)
```

## Acknowledgements  
 We would like to thank the authors of DLtutorialCode[2], which we use in this work.

## References  
[1][python version of [3]](https://github.com/ai-lab-circle/deep_tutorial_python)   
[2] https://github.com/tensorflow/tensorflow/tree/master/tensorflow/contrib/slim
[3][original source](https://github.com/choosehappy/public/tree/master/DL%20tutorial%20Code)   



