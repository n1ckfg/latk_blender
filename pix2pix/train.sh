NAME=$1

python train.py --dataroot ./datasets/$NAME --name pix2pix_$NAME --n_epochs 50 --n_epochs_decay 50 --save_epoch_freq 20 --model pix2pix --direction AtoB --display_id -1

python test.py --dataroot ./datasets/$NAME --name pix2pix_$NAME --model pix2pix

