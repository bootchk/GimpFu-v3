#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#[license] GPLv3
#[plugin]
#[name] blend-fg-bg-color
#[desc]
#blend foreground and background color and set it as foreground color
#[version]
#0.1 初期リリース
#0.2 パレットを使用する方法に変更
#0.3 パレットの最後のエントリが、現在の混色された色を示すように変更
#0.4 「blend history」ヒストリ用パレットを使用するように変更。
#     以前のカラーをGUI上で参照でき、またテンポラリファイルを使用しない
#     ようになった。
#0.5  アンドゥ周りがオカシイ気がしたので修正
#[end]

#  このプログラムはGPLライセンスver3で公開します。
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You may have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#   Copyright (C) 2015 dothiko(http://dothiko.blog.fc2.com/)


from gimpfu import *

##### 各種設定定数：自分の環境に応じて変える
##### configuration constants: change these values as your environment
MAX_UNDO_COUNT=32 # 最大履歴数 maximum history count
PALETTE_NAME="blend history" # 履歴用パレットの名前 palette name to store blended color history

##### グローバル変数：カスタマイズ時の変更はしない
##### global variables,do not modify when customizing
g_palette_name=None # actual palette name within gimp

def python_fu_blendbgfg_func(a_img,a_drawable,sample_arg=True):
    blend_bgfg(0.5)

def python_fu_blendbgfg_slightly_func(a_img,a_drawable,sample_arg=True):
    blend_bgfg(0.90)

def python_fu_blendbgfg_undo_func(a_img,a_drawable,sample_arg=True):
    undo_color()

def blend_bgfg(ratio):

    init_undo_colors()

    rf=ratio
    rb=1.0-ratio
    fg=pdb.gimp_context_get_foreground()
    bg=pdb.gimp_context_get_background()
    cc=get_last_color()

    try:
       #if cc!=None and cc!=fg:  # this line cannot work. read the exception block below
        if cc!=fg:
            save_undo_colors(fg) # save current color to enable undo
                                 # when first commit(cc==None) or
                                 # current foreground color is not last undo entry.
    except TypeError:
        # gimpcolor.RGB cannot compare with NoneType
        # so when get_last_color() returns None,
        # the line "if cc!=fg:" raise this exception.
        # and the line such as "if cc!=None and cc!=fg:"
        # also raise this exception every time.
        pass


    fg.r=min(1.0,max((fg.r*rf)+(bg.r*rb),0.0))
    fg.g=min(1.0,max((fg.g*rf)+(bg.g*rb),0.0))
    fg.b=min(1.0,max((fg.b*rf)+(bg.b*rb),0.0))

    save_undo_colors(fg) # changed this here to save new color.
    pdb.gimp_context_set_foreground(fg)

def init_undo_colors():
    global g_palette_name
    if g_palette_name==None:
        count,pals=pdb.gimp_palettes_get_list(PALETTE_NAME)
        if count==0:
            g_palette_name=pdb.gimp_palette_new(PALETTE_NAME)
        else:
            g_palette_name=pals[0]

def get_last_color():
    cnt=pdb.gimp_palette_get_info(g_palette_name)
    if cnt > 0:
        return pdb.gimp_palette_entry_get_color(g_palette_name,cnt-1)
    else:
        return None


def save_undo_colors(fg):
    """
    save undo colors list as json format.

    Arguments:
    fg -- foreground color of gimp.Color,or None when pop undo stuck

    Returns:
        None
    """

    try:
        cnt=pdb.gimp_palette_get_info(g_palette_name)

        if cnt >= MAX_UNDO_COUNT:
            pdb.gimp_palette_delete_entry(g_palette_name,0)

        pdb.gimp_palette_add_entry(g_palette_name,"",fg)

    except RuntimeError:
        print('runtimeerror raised at blendcolor.py:save_undo_colors')
        pass


def undo_color():
    init_undo_colors()

    try:
        cnt=pdb.gimp_palette_get_info(g_palette_name)
        if cnt > 0:
            fg=pdb.gimp_context_get_foreground()
            lc=get_last_color()

            if fg!=lc:
                # fg is not last color,this means some other user interaction
                # happened since last operation occur
                # and current foreground color is nothing to do with 'blendcolor'

                fg=lc
            elif cnt > 1:
                fg=pdb.gimp_palette_entry_get_color(g_palette_name,cnt-2)
            else:
               #fg=pdb.gimp_palette_entry_get_color(g_palette_name,0) # fg must be same as lastcolor in this case,so this line should be meaningless.
                pass # so pass this case.

            pdb.gimp_palette_delete_entry(g_palette_name,cnt-1)
            pdb.gimp_context_set_foreground(fg)

    except RuntimeError:
        print('runtimeerror raised at blendcolor.py:save_undo_colors')
        pass



register(
        "python_fu_blendbgfg_func",
        "blend-fg-bg-color",
        "前景色と背景色を混合する",
        "dothiko",
        "kakukaku world",
        "Jan 2015",
        "<Image>/Python-Fu/color/blend-fg-bg-color",
        "RGB*,GRAY*",
        [
        ],
        [],
        python_fu_blendbgfg_func)

register(
        "python_fu_blendbgfg_slightly_func",
        "blend-fg-bg-color-slightly",
        "前景色と背景色を混合する(10%版)",
        "dothiko",
        "kakukaku world",
        "Jan 2015",
        "<Image>/Python-Fu/color/blend-fg-bg-color-slightly",
        "RGB*,GRAY*",
        [
        ],
        [],
        python_fu_blendbgfg_slightly_func)

register(
        "python_fu_blendbgfg_undo_func",
        "blend-fg-bg-color-undo",
        "前景色と背景色の混合を直前に戻す",
        "dothiko",
        "kakukaku world",
        "Jan 2015",
        "<Image>/Python-Fu/color/blend-fg-bg-color-undo",
        "RGB*,GRAY*",
        [
        ],
        [],
        python_fu_blendbgfg_undo_func)


main()
