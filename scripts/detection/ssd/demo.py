"""Train Gluon Object-Detection models."""
import os
import argparse
import mxnet as mx
import gluonvision as gv
from matplotlib import pyplot as plt

def parse_args():
    parser = argparse.ArgumentParser(description='Test with SSD networks.')
    parser.add_argument('--network', type=str, default='ssd_300_vgg16_atrous_voc',
                        help="Base network name")
    parser.add_argument('--images', type=str, default='',
                        help='Test images, use comma to split multiple.')
    parser.add_argument('--gpus', type=str, default='0',
                        help='Training with GPUs, you can specify 1,3 for example.')
    parser.add_argument('--pretrained', type=str, default='True',
                        help='Load weights from previously saved parameters.')
    args = parser.parse_args()
    return args

def process_img(im_name, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
    """Pre-process image to tensor required by network."""
    img = mx.image.imread(im_name)
    img = mx.image.resize_short(img, 480)
    orig_img = img.asnumpy().astype('uint8')
    img = mx.nd.image.to_tensor(img)
    img = mx.nd.image.normalize(img, mean=mean, std=std)
    return img, orig_img


if __name__ == '__main__':
    args = parse_args()
    # context list
    ctx = [mx.gpu(int(i)) for i in args.gpus.split(',') if i.strip()]
    ctx = [mx.cpu()] if not ctx else ctx

    # grab some image if not specified
    if not args.images.strip():
        gv.utils.download("https://cloud.githubusercontent.com/assets/3307514/" +
            "20012568/cbc2d6f6-a27d-11e6-94c3-d35a9cb47609.jpg", 'street.jpg')
        image_list = ['street.jpg']
    else:
        image_list = [x.strip() for x in args.images.split(',') if x.strip()]

    if args.pretrained in ['True', '1', 'true']:
        net = gv.model_zoo.get_model(args.network, pretrained=True)
    else:
        net = gv.model_zoo.get_model(args.network, pretrained=False)
        net.load_params(args.pretrained)
    net.set_nms(0.45, 200)

    ax = None
    for image in image_list:
        x, orig_img = process_img(image)
        ids, scores, bboxes = [xx[0].asnumpy() for xx in net(x)]
        ax = gv.utils.viz.plot_bbox(orig_img, bboxes, scores, ids,
                                    class_names=net.classes, ax=ax)
        plt.show()
