# coding = UTF-8

import os
import data
import glob
import numpy as np
import nibabel as nib
from models.networks import MyModel, Unet, BCDUnet
from models.losses import *

import tensorflow as tf
from tensorflow.keras.optimizers import *
from tensorflow.keras.callbacks import *

# 可视化
import show
from random import randint
import IPython.display as display
from IPython.display import clear_output
from tensorflow.keras.utils import plot_model, model_to_dot

import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.animation as anim
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec

print("tensorflow 版本: " + tf.version.VERSION)

sample_filename = '../Datasets/BraTS2020/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_flair.nii.gz'
sample_filename_mask = '../Datasets/BraTS2020/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_seg.nii.gz'

sample_img = nib.load(sample_filename)
sample_img = np.asanyarray(sample_img.dataobj)
sample_img = np.rot90(sample_img)
sample_mask = nib.load(sample_filename_mask)
sample_mask = np.asanyarray(sample_mask.dataobj)
sample_mask = np.rot90(sample_mask)
print("img shape ->", sample_img.shape)
print("mask shape ->", sample_mask.shape)

sample_filename2 = '../Datasets/BraTS2020/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_t1.nii.gz'
sample_img2 = nib.load(sample_filename2)
sample_img2 = np.asanyarray(sample_img2.dataobj)
sample_img2 = np.rot90(sample_img2)

sample_filename3 = '../Datasets/BraTS2020/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_t2.nii.gz'
sample_img3 = nib.load(sample_filename3)
sample_img3 = np.asanyarray(sample_img3.dataobj)
sample_img3 = np.rot90(sample_img3)

sample_filename4 = '../Datasets/BraTS2020/MICCAI_BraTS2020_TrainingData/BraTS20_Training_001/BraTS20_Training_001_t1ce.nii.gz'
sample_img4 = nib.load(sample_filename4)
sample_img4 = np.asanyarray(sample_img4.dataobj)
sample_img4 = np.rot90(sample_img4)

mask_WT = sample_mask.copy()
mask_WT[mask_WT == 1] = 1
mask_WT[mask_WT == 2] = 1
mask_WT[mask_WT == 4] = 1

mask_TC = sample_mask.copy()
mask_TC[mask_TC == 1] = 1
mask_TC[mask_TC == 2] = 0
mask_TC[mask_TC == 4] = 1

mask_ET = sample_mask.copy()
mask_ET[mask_ET == 1] = 0
mask_ET[mask_ET == 2] = 0
mask_ET[mask_ET == 4] = 1

fig = plt.figure(figsize=(20, 10))

gs = gridspec.GridSpec(nrows=2, ncols=4, height_ratios=[1, 1.5])

#  Varying density along a streamline
ax0 = fig.add_subplot(gs[0, 0])
flair = ax0.imshow(sample_img[:, :, 65], cmap='bone')
ax0.set_title("FLAIR", fontsize=18, weight='bold', y=-0.2)
fig.colorbar(flair)

#  Varying density along a streamline
ax1 = fig.add_subplot(gs[0, 1])
t1 = ax1.imshow(sample_img2[:, :, 65], cmap='bone')
ax1.set_title("T1", fontsize=18, weight='bold', y=-0.2)
fig.colorbar(t1)

#  Varying density along a streamline
ax2 = fig.add_subplot(gs[0, 2])
t2 = ax2.imshow(sample_img3[:, :, 65], cmap='bone')
ax2.set_title("T2", fontsize=18, weight='bold', y=-0.2)
fig.colorbar(t2)

#  Varying density along a streamline
ax3 = fig.add_subplot(gs[0, 3])
t1ce = ax3.imshow(sample_img4[:, :, 65], cmap='bone')
ax3.set_title("T1 contrast", fontsize=18, weight='bold', y=-0.2)
fig.colorbar(t1ce)

#  Varying density along a streamline
ax4 = fig.add_subplot(gs[1, 1:3])

# ax4.imshow(np.ma.masked_where(mask_WT[:,:,65]== False,  mask_WT[:,:,65]), cmap='summer', alpha=0.6)
l1 = ax4.imshow(mask_WT[:, :, 65], cmap='summer', )
l2 = ax4.imshow(np.ma.masked_where(mask_TC[:, :, 65] == False, mask_TC[:, :, 65]), cmap='rainbow', alpha=0.6)
l3 = ax4.imshow(np.ma.masked_where(mask_ET[:, :, 65] == False, mask_ET[:, :, 65]), cmap='winter', alpha=0.6)

ax4.set_title("", fontsize=20, weight='bold', y=-0.1)

_ = [ax.set_axis_off() for ax in [ax0, ax1, ax2, ax3, ax4]]

colors = [im.cmap(im.norm(1)) for im in [l1, l2, l3]]
labels = ['Non-Enhancing tumor core', 'Peritumoral Edema ', 'GD-enhancing tumor']
patches = [mpatches.Patch(color=colors[i], label=f"{labels[i]}") for i in range(len(labels))]
# put those patched as legend-handles into the legend
plt.legend(handles=patches, bbox_to_anchor=(1.1, 0.65), loc=2, borderaxespad=0.4, fontsize='xx-large',
           title='Mask Labels', title_fontsize=18, edgecolor="black", facecolor='#c5c6c7')

plt.suptitle("Multimodal Scans -  Data | Manually-segmented mask - Target", fontsize=20, weight='bold')

fig.savefig("data_sample.png", format="png", pad_inches=0.2, transparent=False, bbox_inches='tight')
fig.savefig("data_sample.svg", format="svg", pad_inches=0.2, transparent=False, bbox_inches='tight')

# # load datasets
# train_images_file_path = '../Datasets/ISIC2016/ISBI2016_ISIC_Part1_Training_Data/*jpg'
# test_images_file_path = '../Datasets/ISIC2016/ISBI2016_ISIC_Part1_Test_Data/*jpg'
# train_masks_file_path = '../Datasets/ISIC2016/ISBI2016_ISIC_Part1_Training_GroundTruth/*.png'
# test_masks_file_path = '../Datasets/ISIC2016/ISBI2016_ISIC_Part1_Test_GroundTruth/*.png'
#
# images_path = glob.glob(train_images_file_path)  # + glob.glob(test_images_file_path)
# masks_path = glob.glob(train_masks_file_path)  # + glob.glob(test_masks_file_path)
#
# train_count = int(len(images_path) * 0.8)  # 80%
# val_count = len(images_path) - train_count  # 20%
#
# # # /////////// 测试用,请注释 ///////////
# # os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
# # os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # 使用CPU计算
# # train_count = int(train_count * 0.05)
# # val_count = int(val_count * 0.05)
#
# print('数据集个数:', len(images_path),
#       '训练集个数:', train_count, '测试集个数:', val_count)
# # 数据集个数: 900 训练集个数: 720 测试集个数: 180
#
# # //////////////////////////////////////////////////////////
# # 加载模型, 这样是为了在多个模型的情况下便于修改
# # model = MyModel.UNet(input_size=(256, 256, 3))
# # model_name = 'Unet'
# # model = MyModel.AttentionUNet(input_size=(256, 256, 3))
# # model_name = 'AttUnet'
# # model = BCDUnet.BCDU_net_D3(input_size=(256, 256, 3))
# # model_name = 'BCDUnet'
# # model = MyModel.ADUNet_L5(input_size=(256, 256, 3))
# # model_name = 'ADUnet_L5'
# model = MyModel.ADUNet_L4(input_size=(256, 256, 3))
# model_name = 'ADUnet_L4'
#
# # 超参数
# BATCH_SIZE = 2
# EPOCHS = 100
# BUFFER_SIZE = train_count
# STEPS_PER_EPOCH = train_count // BATCH_SIZE
# VALIDATION_STEPS = 1
# # //////////////////////////////////////////////////////////
#
# # 打乱数据集，重写
# dataset = tf.data.Dataset.from_tensor_slices((images_path, masks_path))
#
# dataset = dataset.map(data.load_image_train, num_parallel_calls=tf.data.experimental.AUTOTUNE)
# # 跳过test_count个
# train = dataset.skip(val_count)
# val = dataset.take(val_count)
# # print(train, test)
# train_dataset = train.batch(BATCH_SIZE).shuffle(BUFFER_SIZE).cache().repeat()
# train_dataset = train_dataset.prefetch(buffer_size=tf.data.experimental.AUTOTUNE)
# val_dataset = val.batch(BATCH_SIZE)
# # train:  <SkipDataset shapes: ((256, 256, 3), (256, 256, 1)), types: (tf.float32, tf.float32)>
# # test:   <TakeDataset shapes: ((256, 256, 3), (256, 256, 1)), types: (tf.float32, tf.float32)>
# # train_dataset:  <PrefetchDataset shapes: ((None, 256, 256, 3), (None, 256, 256, 1)), types: (tf.float32, tf.float32)>
# # test_dataset:   <BatchDataset shapes: ((None, 256, 256, 3), (None, 256, 256, 1)), types: (tf.float32, tf.float32)>
#
# # # 看一下数据加载是否正常
# # sample_image, sample_mask = [], []
# # for image, mask in train.take(randint(0, train_count)):
# #     sample_image, sample_mask = image, mask
# # show.display_sample([sample_image, sample_mask])
#
#
# # -----------------------------------------------------------------------------
#
# # save path
# save_model_path = 'output/' + model_name + '.h5'
# # # 模型结构
# # plot_model(model, to_file=os.path.join(save_dir, model_name + '_MODEL.png'))
#
# # build
# # 评价函数 和 损失函数 相似, 只不过评价函数的结果不会用于训练过程中
# model.compile(optimizer=Adam(lr=1e-4),
#               # loss='binary_crossentropy',
#               loss=dice_coef_loss,
#               metrics=[dice_coef, 'binary_accuracy', f1_scores, precision_m, recall_m])
#
# early_stopping = EarlyStopping(monitor='val_loss', patience=7)  # 在验证集的误差不再下降时，中断训练
# reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.3, patience=2, verbose=1,
#                               min_delta=1e-4)  # 当标准评估停止提升时，降低学习速率
# cp_callback = ModelCheckpoint(save_model_path, verbose=1, save_best_only=True)  # 保存模型
#
#
# class DisplayCallback(tf.keras.callbacks.Callback):
#     def on_epoch_end(self, epoch, logs=None):
#         # clear_output(wait=True)  # 每次输出图像前关闭上一次
#         show.show_predictions(save_model_path, val_dataset)
#         # print('\nSample Prediction after epoch {}\n'.format(epoch + 1))
#
#
# # 训练模型
# history = model.fit(train_dataset, epochs=EPOCHS,
#
#                     # shuffle=True,  # 则训练数据将在每个 epoch 混洗, 验证集永远不会混洗
#                     # validation_split=0.2,  # 使用的验证数据将是最后 20％ 的数据。
#
#                     steps_per_epoch=STEPS_PER_EPOCH,
#                     validation_data=val_dataset,
#                     validation_steps=VALIDATION_STEPS,
#
#                     callbacks=[
#                         early_stopping,
#                         # cp_callback,
#                         # DisplayCallback(),
#                         reduce_lr
#                     ],
#                     verbose=1)
#
# # # 模型结构展示
# # model.summary()
#
# # -----------------------------------------------------------------------------
#
# # 可视化
# print(history.history.keys())
# dice_coef = history.history['dice_coef']
# binary_accuracy = history.history['binary_accuracy']
# f1_scores = history.history['f1_scores']
# precision_m = history.history['precision_m']
# recall_m = history.history['recall_m']
#
# val_dice_coef = history.history['val_dice_coef']
# val_binary_accuracy = history.history['val_binary_accuracy']
# val_f1_scores = history.history['val_f1_scores']
# val_precision_m = history.history['val_precision_m']
# val_recall_m = history.history['val_recall_m']
#
# lr = history.history['lr']
#
# loss = history.history['loss']
# val_loss = history.history['val_loss']
#
# plt.subplot(2, 1, 1)
# plt.plot(dice_coef, 'o-', label="dice_coef", color='#d7191c')
# plt.plot(val_dice_coef, 'o--', label="val_dice_coef", color='#d7191c')
#
# plt.plot(binary_accuracy, '^-', label="binary_accuracy", color='#fdae61')
# plt.plot(val_binary_accuracy, '^--', label="val_binary_accuracy", color='#fdae61')
#
# plt.plot(f1_scores, 's-', label="f1_scores", color='#abdda4')
# plt.plot(val_f1_scores, 's--', label="val_f1_scores", color='#abdda4')
#
# plt.plot(precision_m, 'p-', label="precision", color='#2b83ba')
# plt.plot(val_precision_m, 'p--', label="val_precision", color='#2b83ba')
#
# plt.plot(recall_m, '<-', label="recall", color='#5e4fa2')
# plt.plot(val_recall_m, '<--', label="val_recall", color='#5e4fa2')
#
# plt.title("Accuracy")
# plt.xlabel('Epoch')
# plt.ylabel('Accuracy Value')
# plt.ylim([0, 1])
# plt.grid()
# plt.legend()
#
# plt.subplot(2, 2, 3)
# plt.plot(loss, 'x-', label="Training Loss")
# plt.plot(val_loss, 'x--', label="Validation Loss")
# plt.title("loss")
# plt.xlabel('Epoch')
# plt.ylabel('Loss Value')
# plt.ylim([0, 1])
# plt.grid()
# plt.legend()
#
# plt.subplot(2, 2, 4)
# plt.plot(lr, 'o-', label="Learning Rate")
# plt.title("lr")
# plt.xlabel('Epoch')
# plt.ylabel('lr Value')
# # plt.ylim([0, 1])
# plt.grid()
# plt.legend()
#
# plt.show()
