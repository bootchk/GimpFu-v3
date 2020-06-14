#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Импортируем необходимые модули
from gimpfu import *

# Минимальные значения
min_size = 1
min_radius = 0.1
min_amount = 0.01
min_threshold = 0

# Максимальные значения
max_size = 262144
max_radius = 500
max_amount = 10
max_threshold = 255

# Процедура обработки
def process_for_stts(image, drawable,
                     side, size, steps,
                     radius, amount, threshold,
                     new_image):

    # Проверка значений на корректность
    inc_types = (str, basestring, list, tuple, dict)
    if isinstance(size, inc_types) or size < min_size or size > max_size:
        err_msg = "Неверный размер: " + str(size)
        pdb.gimp_message_set_handler(0)
        pdb.gimp_message(err_msg)
        exit(err_msg)
    if isinstance(radius, inc_types) or radius > max_radius or radius < min_radius:
        radius = 3.0
    if isinstance(amount, inc_types) or amount > max_amount or amount < min_amount:
        amount = 0.3
    if isinstance(threshold, inc_types) or threshold > max_threshold or threshold < min_threshold:
        threshold = 1

    # Сохраняем исходные значения системных переменных
    orig_msg_handler = pdb.gimp_message_get_handler()
    orig_context_intrepolation = pdb.gimp_context_get_interpolation()
    orig_background = pdb.gimp_context_get_background()

    # Запрещаем запись информации для отмены действий
    pdb.gimp_context_push()
    pdb.gimp_image_undo_group_start(image)

    # Отменяем выделение
    pdb.gimp_selection_none(image)

    # Создаем временное изображение
    cur_image = pdb.gimp_image_duplicate(image)
    cur_drawable = pdb.gimp_image_get_active_drawable(cur_image)

    # Устанавливаем тип интерполяции: кубическая
    pdb.gimp_context_set_interpolation(2)

    # Устанавливаем цвет фона: белый
    pdb.gimp_context_set_background((255, 255, 255))

    # Считываем размер изображения
    orig_width = pdb.gimp_image_width(cur_image)
    orig_height = pdb.gimp_image_height(cur_image)

    cur_width = orig_width
    cur_height = orig_height
    cur_radius = float(radius)
    cur_amount = float(amount)
    cur_threshold = int(threshold)

    # Вычисление таблицы размеров
    if side == 0:
        step_resizeX = float(size - orig_width) / steps
        targ_width = float(step_resizeX * steps) + orig_width
        targ_height = float(orig_height * targ_width) / orig_width
        step_resizeY = float(targ_height - orig_height) / steps
    elif side == 1:
        step_resizeY = float(size - orig_height) / steps
        targ_height = float(step_resizeY * steps) + orig_height
        targ_width = float(orig_width * targ_height) / orig_height
        step_resizeX = float(targ_width - orig_width) / steps

    # Работаем пошагово
    while steps >= 1:
        cur_width += step_resizeX
        cur_height += step_resizeY

        # Изменяем размер изображения
        pdb.gimp_image_scale(cur_image, cur_width, cur_height)

        # Каждый нечетный шаг
        if steps % 2:
            # Разбираем изображение на слои по модели HSV
            decom_images = pdb.plug_in_decompose_registered(cur_image, cur_drawable, "HSV", 0)
            decom_drawable = pdb.gimp_image_get_active_drawable(decom_images[2])

            # Применяем фильтр "Нерезкая маска" к слою "Яркость"
            pdb.plug_in_unsharp_mask(decom_images[2], decom_drawable, cur_radius, cur_amount, cur_threshold)

            # Изменяем значения для усиления резкости
            if size > orig_width:
                cur_radius = round(cur_radius * 1.5, 1)
                cur_amount = round(cur_amount * 1.5, 2)
                cur_threshold = int(cur_threshold * 1.5)
            else:
                cur_radius = round(cur_radius / 2, 1)
                cur_amount = round(cur_amount / 2, 2)
                cur_threshold = int(cur_threshold / 2)

            # Собираем изображение из слоев по модели HSV
            com_image = pdb.plug_in_compose(decom_images[0], None, decom_images[1], decom_images[2], decom_images[3], "HSV")
            com_layer = pdb.gimp_layer_new_from_visible(com_image, cur_image, steps)
            pdb.gimp_image_insert_layer(cur_image, com_layer, None, -1)
            pdb.gimp_image_set_active_layer(cur_image, com_layer)

            # Удаляем ненужные изображения
            for x in decom_images:
                if x:
                    pdb.gimp_image_delete(x)
            pdb.gimp_image_delete(com_image)

        steps -= 1

    if new_image:
        # Задаем имя нового изображения
        pdb.gimp_image_set_filename(cur_image, (pdb.gimp_item_get_name(drawable)) + "+")

        # Выводим результат в новое изображение
        display = pdb.gimp_display_new(cur_image)
    else:
        # Копируем результат на новый слой
        res_layer = pdb.gimp_layer_new_from_visible(cur_image, image, "HSV+Sharpen")
        pdb.gimp_image_insert_layer(image, res_layer, None, -1)
        pdb.gimp_image_set_active_layer(image, res_layer)

        # Если новое изображение больше старого, то увеличиваем размер холста
        if size > orig_width:
            pdb.gimp_image_resize(image, cur_width, cur_height, 0, 0)

        # Удаляем временное изображение
        pdb.gimp_image_delete(cur_image)

    # Выводим изображения обратно
    pdb.gimp_displays_flush()

    # Разрешаем запись информации для отмены действий
    pdb.gimp_image_undo_group_end(image)
    pdb.gimp_context_pop()
    print pdb.gimp_image_list()

    # Возвращаем значения системных переменных в исходное состояние
    pdb.gimp_message_set_handler(orig_msg_handler)
    pdb.gimp_context_set_interpolation(orig_context_intrepolation)
    pdb.gimp_context_set_background(orig_background)

# Регистрируем функцию в PDB
register(
    proc_name = "python-fu-process-transphoto",
    blurb = "Image size reduction for site http://transphoto.ru",
    help = "Step-by-step decrease of image size with applying filter \"Unsharp mask\"",
    author = "Charles Malaheenee",
    copyright = "Charles Malaheenee (http://github.com/malaheenee)",
    date = "20.11.2016",
    label = "<Image>/Filters/STTS processing...",
    imagetypes = "*",
    params = [
        (PF_OPTION, "side", "Target side", 0, ["Width", "Height"]),
        (PF_INT, "size", "Size (in pixels)", 1200),
        (PF_ADJUSTMENT, "steps", "Number of steps", 0, (2, 10, 1)),
        (PF_SPINNER, "radius", "Unsharp mask: radius", 2, (min_radius, max_radius, 0.1)),
        (PF_SPINNER, "amount", "Unsharp mask: amount", 0.2, (min_amount, max_amount, 0.01)),
        (PF_SPINNER, "threshold", "Unsharp mask: threshold", 0, (min_threshold, max_threshold, 1)),
        (PF_TOGGLE, "new_image", "Output to new image", False)
    ],
    results = [],
    #lkk remove parens
    function = process_for_stts,
    )

# Запускаем скрипт
main()
