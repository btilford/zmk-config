#!/usr/bin/env zsh

set -e
echo "Building ZMK for Typeractive Corn 3x6"
west build \
    -p \
    -s $HOME/Projects/public/zmk-config/zmk/app/ \
    -b nice_nano_v2 \
    -- -DSHIELD=corne_left \
    -DZMK_CONFIG=$HOME/Projects/public/zmk-config/config/ \
    -DZMK_EXTRA_MODULES=/home/btilford/Projects/public/zmk-leader-key


echo "Left side build completed."


# west build -s app/ \
#     -d /tmp/zmk-corn-right \
#     -b nice_nano_v2 \
#     -- -DSHIELD=corne_right \
#  -DZMK_CONFIG=$HOME/Projects/public/corne-wireless-view-zmk-config \
#     -DZMK_EXTRA_MODULES=/home/btilford/Projects/public/zmk-leader-key
#
    # -DZMK_CONFIG=$HOME/Projects/public/corne-wireless-view-zmk-config/config/ \

